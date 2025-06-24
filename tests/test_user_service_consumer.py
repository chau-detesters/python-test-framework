import pytest
from pact.v3 import Pact, match
from consumer.service import UserService, User

PACT_MOCK_PORT = 1234
PACT_MOCK_URL = f"http://localhost:{PACT_MOCK_PORT}"

@pytest.fixture(scope="function")
def pact():
    pact = Pact(
        "UserService",
        "UserAPI"
    )
    yield pact

class TestUserServiceConsumer:
    """Consumer contract tests using Pact"""
    
    def test_get_user_success(self, pact):
        """Test successful user retrieval"""
        expected_user = {
            'id': match.like(1),
            'name': match.like('John Doe'),
            'email': match.like('john@example.com'),
            'username': match.like('johndoe')
        }
        
        # Define the expected interaction
        (
            pact.upon_receiving("a request for user 1")
            .given("user 1 exists")
            .with_request("GET", "/users/1")
            .will_respond_with(200)
            .with_body(expected_user)
        )
        
        with pact.serve() as mock_server:
            user_service = UserService(str(mock_server.url))
            user = user_service.get_user(1)
            
            assert user is not None
            assert user.id == 1
            assert user.name == 'John Doe'
            assert user.email == 'john@example.com'
            user_service.close()
            pact.write_file('pacts/get_user_success.json')
    
    def test_get_user_not_found(self, pact):
        (
            pact.upon_receiving("a request for user 999")
            .given("user 999 does not exist")
            .with_request("GET", "/users/999")
            .will_respond_with(404)
            .with_body({'error': 'User not found'})
        )
        with pact.serve() as mock_server:
            user_service = UserService(str(mock_server.url))
            user = user_service.get_user(999)
            assert user is None
            user_service.close()
            pact.write_file('pacts/get_user_not_found.json')
    
    def test_get_users_list(self, pact):
        expected_user_structure = {
            'id': match.like(1),
            'name': match.like('John Doe'),
            'email': match.regex('john@example.com', regex=r'.+@.+\..+'),
            'username': match.like('johndoe')
        }
        (
            pact.upon_receiving("a request for users list")
            .given("users exist")
            .with_request("GET", "/users")
            .with_query_parameters({"_limit": "10"})
            .will_respond_with(200)
            .with_body(match.each_like(expected_user_structure))
        )
        with pact.serve() as mock_server:
            user_service = UserService(str(mock_server.url))
            users = user_service.get_users(limit=10)
            assert len(users) >= 1
            assert all(isinstance(user, User) for user in users)
            user_service.close()
            pact.write_file('pacts/get_users_list.json')
    
    def test_create_user_success(self, pact):
        user_data = {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'username': 'janesmith'
        }
        expected_response = {
            'id': match.like(101),
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'username': 'janesmith'
        }
        (
            pact.upon_receiving("a request to create a user")
            .given("user creation is allowed")
            .with_request("POST", "/users")
            .with_body(match.like(user_data))
            .will_respond_with(201)
            .with_body(expected_response)
        )
        with pact.serve() as mock_server:
            user_service = UserService(str(mock_server.url))
            created_user = user_service.create_user(user_data)
            assert created_user is not None
            assert created_user.name == 'Jane Smith'
            assert created_user.email == 'jane@example.com'
            assert created_user.id > 0
            user_service.close()
            pact.write_file('pacts/create_user_success.json')
    
    def test_get_user_posts(self, pact):
        expected_post_structure = {
            'id': match.like(1),
            'userId': match.like(1),
            'title': match.like('Sample Post Title'),
            'body': match.like('Sample post body content')
        }
        (
            pact.upon_receiving("a request for user 1 posts")
            .given("user 1 has posts")
            .with_request("GET", "/posts")
            .with_query_parameters({"userId": "1"})
            .will_respond_with(200)
            .with_body(match.each_like(expected_post_structure))
        )
        with pact.serve() as mock_server:
            user_service = UserService(str(mock_server.url))
            posts = user_service.get_user_posts(1)
            assert len(posts) >= 1
            assert all(post.userId == 1 for post in posts)
            user_service.close()
            pact.write_file('pacts/get_user_posts.json')
    
    def test_create_user_validation_error(self, pact):
        invalid_user_data = {
            'name': '',  # Invalid: empty name
            'email': 'invalid-email',  # Invalid: bad email format
            'username': 'usr'  # Invalid: too short
        }
        (
            pact.upon_receiving("a request to create user with invalid data")
            .given("user creation validation is enabled")
            .with_request("POST", "/users")
            .with_body(invalid_user_data)
            .will_respond_with(422)
            .with_body({
                'error': 'Validation failed',
                'details': match.each_like('Name is required')
            })
        )
        with pact.serve() as mock_server:
            user_service = UserService(str(mock_server.url))
            created_user = user_service.create_user(invalid_user_data)
            assert created_user is None
            user_service.close()
            pact.write_file('pacts/create_user_validation_error.json')

def test_minimal_pact_interaction(pact):
    (
        pact.upon_receiving("a minimal request")
        .with_request("GET", "/minimal")
        .will_respond_with(200)
        .with_body({"result": "ok"})
    )
    with pact.serve() as mock_server:
        import requests
        response = requests.get(f"{mock_server.url}/minimal")
        assert response.status_code == 200
        assert response.json() == {"result": "ok"}
        pact.write_file('pacts/minimal_pact_interaction.json')

def test_simple_provider_state(pact):
    (
        pact.upon_receiving("a request with provider state")
        .given("state A")
        .with_request("GET", "/state-a")
        .will_respond_with(200)
        .with_body({"result": "state-a-ok"})
    )
    with pact.serve() as mock_server:
        import requests
        response = requests.get(f"{mock_server.url}/state-a")
        assert response.status_code == 200
        assert response.json() == {"result": "state-a-ok"}
        pact.write_file('pacts/simple_provider_state.json') 