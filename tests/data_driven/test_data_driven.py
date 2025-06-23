# test_data_driven.py
"""
Basis data-driven tests voor validatie van API en business logic.
"""
import pytest
import json
from pathlib import Path
from typing import List, Dict, Any

# Sample test data file content (save as test_data.json)
SAMPLE_TEST_DATA = {
    "user_validation_tests": [
        {
            "name": "valid_complete_user",
            "input": {
                "name": "John Doe",
                "username": "johndoe",
                "email": "john@example.com",
                "phone": "1-770-736-8031 x56442",
                "website": "hildegard.org"
            },
            "expected_valid": True
        },
        {
            "name": "missing_required_fields",
            "input": {
                # Missing name - should be invalid
            },
            "expected_valid": False
        },
        {
            "name": "invalid_email_format",
            "input": {
                "name": "John Doe",
                "username": "johndoe",
                "email": "invalid-email-format"
            },
            "expected_valid": False
        }
    ],
    "api_endpoint_tests": [
        {
            "endpoint": "/users",
            "method": "GET",
            "expected_status": 200,
            "expected_type": "list"
        },
        {
            "endpoint": "/users/1",
            "method": "GET", 
            "expected_status": 200,
            "expected_type": "dict"
        },
        {
            "endpoint": "/users/999",
            "method": "GET",
            "expected_status": 404,
            "expected_type": "dict"
        }
    ]
}

@pytest.fixture(scope="session")
def test_data():
    """Load test data from JSON file or return sample data"""
    # In real project, you'd load from file:
    # with open("test_data.json") as f:
    #     return json.load(f)
    return SAMPLE_TEST_DATA

def load_test_cases(test_data: Dict, test_category: str) -> List[Dict[str, Any]]:
    """Extract test cases from test data"""
    return test_data.get(test_category, [])

class TestDataDriven:
    """Data-driven testing examples"""
    
    def test_user_validation_from_data(self, test_data, user_factory):
        """Test user validation using external test data"""
        validation_tests = load_test_cases(test_data, "user_validation_tests")
        
        # Convert to parametrized test cases
        for test_case in validation_tests:
            # For negative cases, use raw input to allow missing required fields
            if not test_case["expected_valid"]:
                user_data = test_case["input"]
            else:
                user_data = user_factory.create_user(**test_case["input"])
            
            try:
                from pydantic import BaseModel, EmailStr
                from typing import Optional
                
                class UserModel(BaseModel):
                    name: str
                    username: Optional[str] = None
                    email: Optional[EmailStr] = None
                    phone: Optional[str] = None
                    website: Optional[str] = None
                
                UserModel(**user_data)
                is_valid = True
            except Exception:
                is_valid = False
            
            expected = test_case["expected_valid"]
            assert is_valid == expected, f"Test case '{test_case['name']}' failed"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("test_case", SAMPLE_TEST_DATA["api_endpoint_tests"])
    async def test_api_endpoints_from_data(self, http_client, test_case):
        """Test API endpoints using data-driven approach"""
        endpoint = test_case["endpoint"]
        method = test_case["method"].lower()
        expected_status = test_case["expected_status"]
        expected_type = test_case["expected_type"]
        
        response = await http_client.request(method, endpoint)
        assert response.status_code == expected_status
        
        if response.status_code == 200:
            data = response.json()
            if expected_type == "list":
                assert isinstance(data, list)
            elif expected_type == "dict":
                assert isinstance(data, dict) 