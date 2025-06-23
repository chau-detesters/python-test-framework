"""
Integration tests for basic API functionality and responses.
"""
import pytest
import httpx
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    username: str
    email: str

class Post(BaseModel):
    userId: int
    id: int
    title: str
    body: str

class Comment(BaseModel):
    postId: int
    id: int
    name: str
    email: str
    body: str

@pytest.mark.asyncio
class TestUsersAPI:
    
    async def test_get_all_users(self, http_client):
        """Test getting all users"""
        response = await http_client.get("/users")
        
        assert response.status_code == 200
        users_data = response.json()
        assert len(users_data) > 0
        
        # Valideer eerste user met Pydantic
        first_user = User(**users_data[0])
        assert first_user.id > 0
        assert "@" in first_user.email

    async def test_get_single_user(self, http_client):
        """Test getting a specific user"""
        user_id = 1
        response = await http_client.get(f"/users/{user_id}")
        
        assert response.status_code == 200
        user_data = response.json()
        
        user = User(**user_data)
        assert user.id == user_id

    @pytest.mark.parametrize("user_id", [1, 2, 3, 5, 10])
    async def test_multiple_users(self, http_client, user_id):
        """Test multiple user IDs with parametrized testing"""
        response = await http_client.get(f"/users/{user_id}")
        
        assert response.status_code == 200
        user = User(**response.json())
        assert user.id == user_id

    async def test_user_not_found(self, http_client):
        """Test 404 scenario"""
        response = await http_client.get("/users/999")
        assert response.status_code == 404

@pytest.mark.asyncio  
class TestPostsAPI:
    
    async def test_get_posts_for_user(self, http_client):
        """Test posts of a specific user"""
        user_id = 1
        response = await http_client.get(f"/posts?userId={user_id}")
        
        assert response.status_code == 200
        posts = response.json()
        
        # Valideer dat alle posts van de juiste user zijn
        for post_data in posts:
            post = Post(**post_data)
            assert post.userId == user_id

    async def test_create_post(self, http_client, sample_user_data):
        """Test creating a new post"""
        new_post = {
            "title": "Test Post",
            "body": "Dit is een test post body",
            "userId": 1
        }
        
        response = await http_client.post("/posts", json=new_post)
        
        assert response.status_code == 201
        created_post = response.json()
        assert created_post["title"] == new_post["title"]
        assert created_post["userId"] == new_post["userId"] 

@pytest.mark.asyncio
class TestCommentsAPI:
    
    async def test_get_comments_for_post(self, http_client):
        """Test getting comments for a specific post"""
        post_id = 1
        response = await http_client.get(f"/comments?postId={post_id}")
        
        assert response.status_code == 200
        comments = response.json()
        assert len(comments) > 0
        
        # Valideer alle comments met Pydantic
        for comment_data in comments:
            comment = Comment(**comment_data)
            assert comment.postId == post_id
            assert "@" in comment.email
            assert len(comment.body) > 0
            
    @pytest.mark.parametrize("post_id", [1, 2, 3])
    async def test_comments_count_per_post(self, http_client, post_id):
        """Test if each post has a reasonable number of comments"""
        response = await http_client.get(f"/comments?postId={post_id}")
        
        assert response.status_code == 200
        comments = response.json()
        
        # Valideer dat er comments zijn maar niet te veel
        assert len(comments) > 0
        assert len(comments) <= 10, f"Post {post_id} heeft meer dan 10 comments"
        
        # Valideer eerste comment
        first_comment = Comment(**comments[0])
        assert first_comment.postId == post_id
        assert first_comment.name and first_comment.email and first_comment.body 

    async def test_create_comment_with_fake_data(self, http_client, fake):
        """Test creating a new comment with generated test data"""
        # Genereer realistische testdata met Faker
        fake_comment = {
            "postId": fake.random_int(min=1, max=100),
            "name": fake.name(),
            "email": fake.email(),
            "body": fake.paragraph(nb_sentences=3)
        }
        
        response = await http_client.post("/comments", json=fake_comment)
        
        assert response.status_code == 201
        created_comment = response.json()
        
        # Valideer de response met Pydantic
        comment = Comment(**created_comment)
        assert comment.postId == fake_comment["postId"]
        assert comment.name == fake_comment["name"]
        assert comment.email == fake_comment["email"]
        assert comment.body == fake_comment["body"]
        
    @pytest.mark.parametrize("num_comments", [1, 2, 3])
    async def test_create_multiple_comments(self, http_client, fake, num_comments):
        """Test creating multiple comments with unique test data"""
        post_id = fake.random_int(min=1, max=100)
        created_comments = []
        
        for _ in range(num_comments):
            # Genereer unieke testdata voor elke comment
            fake_comment = {
                "postId": post_id,
                "name": fake.unique.name(),
                "email": fake.unique.email(),
                "body": fake.paragraph(nb_sentences=2)
            }
            
            response = await http_client.post("/comments", json=fake_comment)
            assert response.status_code == 201
            
            comment = Comment(**response.json())
            created_comments.append(comment)
            
            # Valideer dat de data correct is opgeslagen
            assert comment.postId == post_id
            assert comment.name == fake_comment["name"]
            assert comment.email == fake_comment["email"]
            assert comment.body == fake_comment["body"]
        
        # Valideer dat alle comments uniek zijn
        assert len(created_comments) == num_comments
        assert len(set(c.email for c in created_comments)) == num_comments, "Niet alle comments hebben unieke emails"
        assert len(set(c.name for c in created_comments)) == num_comments, "Niet alle comments hebben unieke namen" 