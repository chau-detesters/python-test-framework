# test_fixture_scope.py
"""
Unittests voor pytest fixture scopes: validatie van scopegedrag.
"""
import pytest

@pytest.fixture(scope="function")
def function_obj():
    obj = object()
    print(f"function_obj id: {id(obj)}")
    return obj

@pytest.fixture(scope="session")
def session_obj():
    obj = object()
    print(f"session_obj id: {id(obj)}")
    return obj

class TestFixtureScope:
    def test_function_scope_1(self, function_obj):
        """Test dat function-scope fixture uniek is per test."""
        pass

    def test_function_scope_2(self, function_obj):
        """Test dat function-scope fixture uniek is per test (tweede test)."""
        pass

    def test_session_scope_1(self, session_obj):
        """Test dat session-scope fixture gedeeld wordt tussen tests."""
        pass

    def test_session_scope_2(self, session_obj):
        """Test dat session-scope fixture gedeeld wordt tussen tests (tweede test)."""
        pass

    def test_session_scope_3(self, session_obj):
        """Test dat session-scope fixture gedeeld wordt tussen tests (derde test)."""
        pass 