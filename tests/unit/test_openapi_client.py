"""Unit tests for OpenAPIClient class."""
import pytest
import httpx
import yaml
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from src.openapi_client import OpenAPIClient
from jsonschema.exceptions import ValidationError

class TestOpenAPIClient:
    @pytest.fixture
    def base_url(self):
        return "http://api.example.com"
    
    @pytest.fixture
    def sample_spec(self):
        return {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "List of users",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/User"}
                                        }
                                    }
                                }
                            },
                            "204": {
                                "description": "No content"
                            }
                        }
                    },
                    "post": {
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/User"}
                                }
                            }
                        },
                        "responses": {
                            "201": {
                                "description": "User created",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/User"}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                            "email": {"type": "string"}
                        },
                        "required": ["id", "name", "email"]
                    }
                }
            }
        }

    def test_load_spec_from_url_success(self, base_url, sample_spec):
        """Test successful loading of spec from URL"""
        with patch('httpx.Client.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = sample_spec
            mock_get.return_value = mock_response
            
            client = OpenAPIClient(base_url, spec_url="http://api.example.com/openapi.json")
            assert client.spec == sample_spec
            assert "User" in client.schemas

    def test_load_spec_from_url_error(self, base_url):
        """Test error handling when loading spec from URL fails"""
        with patch('httpx.Client.get') as mock_get:
            mock_get.side_effect = httpx.RequestError("Connection failed")
            
            with pytest.raises(httpx.RequestError):
                OpenAPIClient(base_url, spec_url="http://invalid-url/openapi.json")

    def test_load_spec_from_file_json(self, base_url, sample_spec, tmp_path):
        """Test loading spec from JSON file"""
        spec_file = tmp_path / "openapi.json"
        spec_file.write_text(json.dumps(sample_spec))
        
        client = OpenAPIClient(base_url, spec_file=str(spec_file))
        assert client.spec == sample_spec
        assert "User" in client.schemas

    def test_load_spec_from_file_yaml(self, base_url, sample_spec, tmp_path):
        """Test loading spec from YAML file"""
        spec_file = tmp_path / "openapi.yaml"
        spec_file.write_text(yaml.dump(sample_spec))
        
        client = OpenAPIClient(base_url, spec_file=str(spec_file))
        assert client.spec == sample_spec
        assert "User" in client.schemas

    def test_load_spec_from_file_not_found(self, base_url):
        """Test error handling when spec file is not found"""
        with pytest.raises(FileNotFoundError):
            OpenAPIClient(base_url, spec_file="nonexistent.json")

    def test_validate_spec_invalid(self, base_url):
        """Test validation of invalid OpenAPI spec"""
        invalid_spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test API"}  # Missing required version
        }
        
        with patch('httpx.Client.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = invalid_spec
            mock_get.return_value = mock_response
            
            with pytest.raises(Exception):
                OpenAPIClient(base_url, spec_url="http://api.example.com/openapi.json")

    def test_validate_response_non_json(self, base_url, sample_spec):
        """Test validation of non-JSON response"""
        with patch('httpx.Client.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = sample_spec
            mock_get.return_value = mock_response
            
            client = OpenAPIClient(base_url, spec_url="http://api.example.com/openapi.json")
            
            # Create a response that raises JSONDecodeError
            response = httpx.Response(200, content=b"not json")
            validation_results = client.validate_response(response, "get", "/users")
            
            assert not validation_results["valid"]
            assert any("invalid JSON" in error for error in validation_results["errors"])

    def test_request_with_validation_invalid_request(self, base_url, sample_spec):
        """Test request validation failure"""
        with patch('httpx.Client.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = sample_spec
            mock_get.return_value = mock_response
            
            client = OpenAPIClient(base_url, spec_url="http://api.example.com/openapi.json")
            
            # Mock validate_request to return validation error
            with patch.object(client, 'validate_request') as mock_validate:
                mock_validate.return_value = {
                    "valid": False,
                    "errors": ["Invalid request body"]
                }
                
                with pytest.raises(ValueError) as exc_info:
                    client.request_with_validation("post", "/users", json={"invalid": "data"})
                
                assert "Invalid request body" in str(exc_info.value)

    def test_resolve_schema_ref_not_found(self, base_url, sample_spec):
        """Test error handling when schema reference is not found"""
        with patch('httpx.Client.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = sample_spec
            mock_get.return_value = mock_response
            
            client = OpenAPIClient(base_url, spec_url="http://api.example.com/openapi.json")
            
            invalid_ref = {"$ref": "#/components/schemas/NonExistentSchema"}
            with pytest.raises(ValueError) as exc_info:
                client._resolve_schema_ref(invalid_ref)
            
            assert "Schema reference not found" in str(exc_info.value)

    def test_close_client(self, base_url, sample_spec):
        """Test closing the client"""
        with patch('httpx.Client.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = sample_spec
            mock_get.return_value = mock_response
            
            client = OpenAPIClient(base_url, spec_url="http://api.example.com/openapi.json")
            
            with patch.object(client.client, 'close') as mock_close:
                client.close()
                mock_close.assert_called_once()

    def test_validate_response_undocumented_status(self, base_url, sample_spec):
        """Test validation of response with undocumented status code"""
        with patch('httpx.Client.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = sample_spec
            mock_get.return_value = mock_response
            
            client = OpenAPIClient(base_url, spec_url="http://api.example.com/openapi.json")
            
            # Create a response with undocumented status code
            response = httpx.Response(418, json={})  # I'm a teapot
            validation_results = client.validate_response(response, "get", "/users")
            
            assert not validation_results["valid"]
            assert any("Status code 418 not documented" in error for error in validation_results["errors"])

    def test_validate_response_no_content_204(self, base_url, sample_spec):
        """Test validation of 204 No Content response"""
        with patch('httpx.Client.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = sample_spec
            mock_get.return_value = mock_response
            
            client = OpenAPIClient(base_url, spec_url="http://api.example.com/openapi.json")
            
            # Create a 204 response
            response = httpx.Response(204)
            validation_results = client.validate_response(response, "get", "/users")
            
            assert validation_results["valid"]
            assert not validation_results["errors"]

    def test_validate_request_with_body(self, base_url, sample_spec):
        """Test validation of request with body"""
        with patch('httpx.Client.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = sample_spec
            mock_get.return_value = mock_response
            
            client = OpenAPIClient(base_url, spec_url="http://api.example.com/openapi.json")
            
            # Test valid request body
            valid_user = {
                "id": 1,
                "name": "Test User",
                "email": "test@example.com"
            }
            validation_results = client.validate_request("post", "/users", json=valid_user)
            assert validation_results["valid"]
            assert not validation_results["errors"]
            
            # Test invalid request body
            invalid_user = {
                "id": "not a number",  # Should be integer
                "name": 123,  # Should be string
                "email": "invalid"  # Should be string but invalid email
            }
            validation_results = client.validate_request("post", "/users", json=invalid_user)
            assert not validation_results["valid"]
            assert validation_results["errors"]

    def test_validate_response_with_schema(self, base_url, sample_spec):
        """Test validation of response with schema"""
        with patch('httpx.Client.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = sample_spec
            mock_get.return_value = mock_response
            
            client = OpenAPIClient(base_url, spec_url="http://api.example.com/openapi.json")
            
            # Test valid response
            valid_response = httpx.Response(200, json=[{
                "id": 1,
                "name": "Test User",
                "email": "test@example.com"
            }])
            validation_results = client.validate_response(valid_response, "get", "/users")
            assert validation_results["valid"]
            assert not validation_results["errors"]
            
            # Test invalid response
            invalid_response = httpx.Response(200, json=[{
                "id": "not a number",
                "name": 123,
                "email": "invalid"
            }])
            validation_results = client.validate_response(invalid_response, "get", "/users")
            assert not validation_results["valid"]
            assert validation_results["errors"]

    def test_get_endpoint_info_not_found(self, base_url, sample_spec):
        """Test getting info for non-existent endpoint"""
        with patch('httpx.Client.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = sample_spec
            mock_get.return_value = mock_response
            
            client = OpenAPIClient(base_url, spec_url="http://api.example.com/openapi.json")
            
            # Test non-existent path
            info = client.get_endpoint_info("get", "/nonexistent")
            assert info is None
            
            # Test non-existent method
            info = client.get_endpoint_info("delete", "/users")
            assert info is None

    def test_resolve_nested_schema_refs(self, base_url, sample_spec):
        """Test resolving nested schema references"""
        with patch('httpx.Client.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = sample_spec
            mock_get.return_value = mock_response
            
            client = OpenAPIClient(base_url, spec_url="http://api.example.com/openapi.json")
            
            # Add a nested schema to test
            client.schemas["NestedUser"] = {
                "type": "object",
                "properties": {
                    "user": {"$ref": "#/components/schemas/User"},
                    "items": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/User"}
                    }
                }
            }
            
            resolved = client._resolve_schema_ref({"$ref": "#/components/schemas/NestedUser"})
            assert "type" in resolved
            assert "properties" in resolved
            assert "user" in resolved["properties"]
            assert "items" in resolved["properties"]
            assert "type" in resolved["properties"]["user"]
            assert "items" in resolved["properties"]["items"]

    def test_validate_response_body_no_schema(self, base_url, sample_spec):
        """Test response with body but no schema defined triggers warning"""
        with patch('httpx.Client.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = sample_spec
            mock_get.return_value = mock_response

            client = OpenAPIClient(base_url, spec_url="http://api.example.com/openapi.json")

            # Patch get_endpoint_info to return a response spec with no schema
            endpoint_info = {
                'responses': {
                    '200': {
                        'description': 'OK',
                        'content': {
                            'application/json': {}
                        }
                    }
                }
            }
            with patch.object(client, 'get_endpoint_info', return_value=endpoint_info):
                # Create a response with a JSON body
                response = httpx.Response(200, json={"foo": "bar"})
                results = client.validate_response(response, 'GET', '/users')
                assert results["valid"] is True
                assert any("no schema defined" in w for w in results["warnings"])

    def test_validate_response_endpoint_info_missing(self, base_url, sample_spec):
        """Test validate_response when endpoint_info is missing triggers warning"""
        with patch('httpx.Client.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = sample_spec
            mock_get.return_value = mock_response

            client = OpenAPIClient(base_url, spec_url="http://api.example.com/openapi.json")

            # Patch get_endpoint_info to return None
            with patch.object(client, 'get_endpoint_info', return_value=None):
                response = httpx.Response(200, json={"foo": "bar"})
                results = client.validate_response(response, 'GET', '/users')
                assert results["valid"] is True
                assert any("No spec found" in w for w in results["warnings"])

    def test_extract_schemas_sets_schemas(self, base_url, sample_spec):
        """Test _extract_schemas sets self.schemas when schemas exist"""
        client = OpenAPIClient(base_url)
        client.spec = sample_spec
        client._extract_schemas()
        assert client.schemas == sample_spec["components"]["schemas"]

    def test_resolve_schema_ref_returns_non_dict(self, base_url):
        """Test _resolve_schema_ref returns non-dict schema unchanged"""
        client = OpenAPIClient(base_url)
        # Should return the value unchanged if not a dict and no $ref
        assert client._resolve_schema_ref([1, 2, 3]) == [1, 2, 3]
        assert client._resolve_schema_ref("string") == "string"
        assert client._resolve_schema_ref(123) == 123 