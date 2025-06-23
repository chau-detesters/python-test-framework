# test_data_validation.py
"""
Unittests voor data validatie helpers en edge cases.
"""
import pytest
from pydantic import BaseModel, ValidationError, EmailStr, field_validator
from typing import Optional

class UserModel(BaseModel):
    id: int
    name: str
    username: str
    email: EmailStr
    phone: Optional[str] = None
    website: Optional[str] = None

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name must not be empty')
        return v

class PostModel(BaseModel):
    id: int
    userId: int
    title: str
    body: str

class TestDataValidation:
    
    async def test_user_data_schema_validation(self, http_client):
        """Test that API responses match expected schema"""
        response = await http_client.get("/users/1")
        assert response.status_code == 200
        
        user_data = response.json()
        
        # This will raise ValidationError if data doesn't match schema
        user = UserModel(**user_data)
        assert user.id == 1
        assert "@" in user.email

    async def test_invalid_user_data_handling(self, user_factory):
        """Test handling of invalid user data"""
        # Create user with invalid email
        invalid_user = user_factory.create_user(email="invalid-email")
        
        with pytest.raises(ValidationError) as exc_info:
            UserModel(**invalid_user)
        
        assert "email" in str(exc_info.value)

    @pytest.mark.parametrize("field_name,invalid_value", [
        ("id", "not-a-number"),
        ("email", "invalid-email"),
        ("name", ""),
    ])
    async def test_field_validation(self, user_factory, field_name, invalid_value):
        """Test individual field validation"""
        user_data = user_factory.create_user(**{field_name: invalid_value})
        
        with pytest.raises(ValidationError):
            UserModel(**user_data)

    def test_valid_email(self):
        """Test dat een geldig e-mailadres wordt geaccepteerd."""
        user = UserModel(id=1, name="Alice", username="alice", email="alice@example.com")
        assert user.email == "alice@example.com"

    def test_invalid_email(self):
        """Test dat een ongeldige e-mail een ValidationError geeft."""
        with pytest.raises(ValidationError):
            UserModel(id=1, name="Bob", email="not-an-email") 