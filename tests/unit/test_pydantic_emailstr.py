# test_pydantic_emailstr.py
"""
Unittests voor Pydantic EmailStr validatie en edge cases.
"""
import pytest
from pydantic import BaseModel, EmailStr, ValidationError, field_validator
from typing import Optional

class UserModel(BaseModel):
    id: int
    name: str
    email: EmailStr

class AdvancedUserModel(BaseModel):
    id: int
    name: str
    email: EmailStr
    age: Optional[int] = None
    
    @field_validator('name')
    @classmethod
    def name_must_be_valid(cls, v):
        if len(v) < 2:
            raise ValueError('Name must be at least 2 characters long')
        if not v.replace(' ', '').isalpha():
            raise ValueError('Name must contain only letters and spaces')
        # Normalize whitespace and apply title case
        return ' '.join(v.split()).title()
    
    @field_validator('age')
    @classmethod
    def age_must_be_reasonable(cls, v):
        if v is not None:
            if v < 0 or v > 150:
                raise ValueError('Age must be between 0 and 150')
        return v

class TestPydanticEmailStr:
    def test_valid_email(self):
        """Test dat een geldig e-mailadres wordt geaccepteerd door het model."""
        user = UserModel(id=1, name="Alice", email="alice@example.com")
        assert user.email == "alice@example.com"

    @pytest.mark.parametrize("invalid_email", [
        "not-an-email",
        "missing-at-sign.com",
        "@missing-local.org",
        "user@.com",
        "user@domain"
    ])
    def test_invalid_email(self, invalid_email):
        """Test dat ongeldige e-mailadressen een ValidationError geven."""
        with pytest.raises(ValidationError) as exc_info:
            UserModel(id=1, name="Bob", email=invalid_email)
        print(f"Validation error for '{invalid_email}': {exc_info.value}")
        assert "email" in str(exc_info.value)

    def test_advanced_user_validation_valid(self):
        """Test advanced user model met custom validators"""
        user = AdvancedUserModel(
            id=1,
            name="john doe",
            email="john.doe@example.com",
            age=25
        )
        assert user.name == "John Doe"  # Title case conversion
        assert user.email == "john.doe@example.com"
        assert user.age == 25

    @pytest.mark.parametrize("invalid_name,expected_error", [
        ("a", "Name must be at least 2 characters long"),
        ("123", "Name must contain only letters and spaces"),
        ("John123", "Name must contain only letters and spaces"),
        ("", "Name must be at least 2 characters long"),
    ])
    def test_invalid_names(self, invalid_name, expected_error):
        """Test custom name validation"""
        with pytest.raises(ValidationError) as exc_info:
            AdvancedUserModel(
                id=1,
                name=invalid_name,
                email="test@example.com"
            )
        print(f"Name validation error for '{invalid_name}': {exc_info.value}")
        assert expected_error in str(exc_info.value)

    @pytest.mark.parametrize("invalid_age,expected_error", [
        (-1, "Age must be between 0 and 150"),
        (151, "Age must be between 0 and 150"),
        (-100, "Age must be between 0 and 150"),
        (200, "Age must be between 0 and 150"),
    ])
    def test_invalid_ages(self, invalid_age, expected_error):
        """Test custom age validation"""
        with pytest.raises(ValidationError) as exc_info:
            AdvancedUserModel(
                id=1,
                name="John Doe",
                email="test@example.com",
                age=invalid_age
            )
        print(f"Age validation error for {invalid_age}: {exc_info.value}")
        assert expected_error in str(exc_info.value)

    def test_optional_age(self):
        """Test dat age optioneel is"""
        user = AdvancedUserModel(
            id=1,
            name="Jane Smith",
            email="jane@example.com"
        )
        assert user.age is None

    def test_multiple_validation_errors(self):
        """Test dat meerdere validatiefouten tegelijk worden gerapporteerd"""
        with pytest.raises(ValidationError) as exc_info:
            AdvancedUserModel(
                id=1,
                name="a",  # Te kort
                email="invalid-email",  # Ongeldig email
                age=200  # Te oud
            )
        
        error_str = str(exc_info.value)
        print(f"Multiple validation errors: {error_str}")
        
        # Controleer dat alle verwachte fouten aanwezig zijn
        assert "Name must be at least 2 characters long" in error_str
        assert "value is not a valid email address" in error_str
        assert "Age must be between 0 and 150" in error_str

    def test_email_case_preservation(self):
        """Test dat email case wordt behouden voor het lokale deel, maar domein wordt lowercase"""
        user1 = AdvancedUserModel(
            id=1,
            name="Test User",
            email="TEST@EXAMPLE.COM"
        )
        user2 = AdvancedUserModel(
            id=2,
            name="Test User",
            email="test@example.com"
        )
        
        # Het domein wordt altijd lowercase gemaakt door Pydantic/EmailStr
        assert user1.email == "TEST@example.com"
        assert user2.email == "test@example.com"
        # Het lokale deel (voor de @) behoudt zijn case
        assert user1.email.split('@')[0] == "TEST"
        assert user2.email.split('@')[0] == "test"

    def test_name_normalization(self):
        """Test dat namen correct worden genormaliseerd"""
        test_cases = [
            ("john doe", "John Doe"),
            ("MARY JANE", "Mary Jane"),
            ("bob smith jr", "Bob Smith Jr"),
            ("  alice  cooper  ", "Alice Cooper"),
        ]
        
        for input_name, expected_name in test_cases:
            user = AdvancedUserModel(
                id=1,
                name=input_name,
                email="test@example.com"
            )
            assert user.name == expected_name 