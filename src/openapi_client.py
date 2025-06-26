import httpx
import yaml
import json
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import jsonschema
from openapi_spec_validator import validate_spec
from openapi_spec_validator.readers import read_from_filename

class OpenAPIClient:
    """HTTP client with OpenAPI schema validation"""
    
    def __init__(self, base_url: str, spec_url: str = None, spec_file: str = None):
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url, timeout=30.0)
        self.spec = None
        self.schemas = {}
        
        if spec_url:
            self.load_spec_from_url(spec_url)
        elif spec_file:
            self.load_spec_from_file(spec_file)
    
    def load_spec_from_url(self, spec_url: str):
        """Load OpenAPI spec from URL"""
        response = self.client.get(spec_url)
        response.raise_for_status()
        self.spec = response.json()
        self._extract_schemas()
        self._validate_spec()
    
    def load_spec_from_file(self, spec_file: str):
        """Load OpenAPI spec from file"""
        spec_path = Path(spec_file)
        if spec_path.suffix.lower() in ['.yaml', '.yml']:
            with open(spec_path, 'r') as f:
                self.spec = yaml.safe_load(f)
        else:
            with open(spec_path, 'r') as f:
                self.spec = json.load(f)
        
        self._extract_schemas()
        self._validate_spec()
    
    def _validate_spec(self):
        """Validate the OpenAPI specification itself"""
        try:
            validate_spec(self.spec)
            print("✅ OpenAPI specification is valid")
        except Exception as e:
            print(f"❌ OpenAPI specification is invalid: {e}")
            raise
    
    def _extract_schemas(self):
        """Extract component schemas from OpenAPI spec"""
        if 'components' in self.spec and 'schemas' in self.spec['components']:
            self.schemas = self.spec['components']['schemas']
    
    def get_endpoint_info(self, method: str, path: str) -> Optional[Dict[str, Any]]:
        """Get endpoint information from OpenAPI spec"""
        if not self.spec or 'paths' not in self.spec:
            return None
        
        path_info = self.spec['paths'].get(path)
        if not path_info:
            return None
        
        return path_info.get(method.lower())
    
    def validate_request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """Validate request against OpenAPI spec"""
        endpoint_info = self.get_endpoint_info(method, path)
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        if not endpoint_info:
            validation_results["warnings"].append(f"No spec found for {method} {path}")
            return validation_results
        
        # Validate request body if present
        if 'json' in kwargs and 'requestBody' in endpoint_info:
            request_body_spec = endpoint_info['requestBody']
            content_spec = request_body_spec.get('content', {})
            json_spec = content_spec.get('application/json', {})
            
            if 'schema' in json_spec:
                schema = self._resolve_schema_ref(json_spec['schema'])
                try:
                    jsonschema.validate(kwargs['json'], schema)
                except jsonschema.ValidationError as e:
                    validation_results["valid"] = False
                    validation_results["errors"].append(f"Request body validation error: {e.message}")
        
        return validation_results
    
    def validate_response(self, response: httpx.Response, method: str, path: str) -> Dict[str, Any]:
        """Validate response against OpenAPI spec"""
        endpoint_info = self.get_endpoint_info(method, path)
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        if not endpoint_info:
            validation_results["warnings"].append(f"No spec found for {method} {path}")
            return validation_results
        
        # Validate status code
        responses_spec = endpoint_info.get('responses', {})
        status_code_spec = responses_spec.get(str(response.status_code))
        
        if not status_code_spec:
            # Check for default response
            status_code_spec = responses_spec.get('default')
            if not status_code_spec:
                validation_results["errors"].append(
                    f"Status code {response.status_code} not documented in spec"
                )
                validation_results["valid"] = False
                return validation_results
        
        # Validate response body
        if response.status_code != 204:  # No content expected for 204
            try:
                response_data = response.json()
                content_spec = status_code_spec.get('content', {})
                json_spec = content_spec.get('application/json', {})
                
                if 'schema' in json_spec:
                    schema = self._resolve_schema_ref(json_spec['schema'])
                    try:
                        jsonschema.validate(response_data, schema)
                    except jsonschema.ValidationError as e:
                        validation_results["valid"] = False
                        validation_results["errors"].append(f"Response body validation error: {e.message}")
                elif response_data:
                    validation_results["warnings"].append("Response has body but no schema defined")
            
            except json.JSONDecodeError:
                if 'application/json' in status_code_spec.get('content', {}):
                    validation_results["valid"] = False
                    validation_results["errors"].append("Expected JSON response but got invalid JSON")
        
        return validation_results
    
    def _resolve_schema_ref(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve schema references ($ref)"""
        if isinstance(schema, dict) and '$ref' in schema:
            ref_path = schema['$ref']
            if ref_path.startswith('#/components/schemas/'):
                schema_name = ref_path.split('/')[-1]
                if schema_name in self.schemas:
                    return self._resolve_schema_ref(self.schemas[schema_name])
                else:
                    raise ValueError(f"Schema reference not found: {ref_path}")
        
        # Recursively resolve nested references
        if isinstance(schema, dict):
            resolved_schema = {}
            for key, value in schema.items():
                if key == 'properties' and isinstance(value, dict):
                    resolved_schema[key] = {
                        prop_name: self._resolve_schema_ref(prop_schema)
                        for prop_name, prop_schema in value.items()
                    }
                elif key == 'items' and isinstance(value, dict):
                    resolved_schema[key] = self._resolve_schema_ref(value)
                else:
                    resolved_schema[key] = value
            return resolved_schema
        
        return schema
    
    def request_with_validation(self, method: str, path: str, **kwargs) -> httpx.Response:
        """Make request with automatic validation"""
        # Validate request
        request_validation = self.validate_request(method, path, **kwargs)
        if not request_validation["valid"]:
            raise ValueError(f"Request validation failed: {request_validation['errors']}")
        
        # Make request
        response = self.client.request(method, path, **kwargs)
        
        # Validate response
        response_validation = self.validate_response(response, method, path)
        
        # Attach validation results to response
        response.validation_results = response_validation
        
        return response
    
    def close(self):
        """Close the HTTP client"""
        self.client.close() 