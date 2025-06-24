"""
Factory for generating test data (users, posts, comments) for data-driven tests.
"""
from faker import Faker
import random
from typing import Dict, Any, List

fake = Faker()

class UserFactory:
    """Factory for generating user test data."""
    @staticmethod
    def create(**overrides) -> Dict[str, Any]:
        """Generate a single user (optionally with overrides)."""
        data = {
            "id": random.randint(1, 10000),
            "name": fake.name(),
            "email": fake.email(),
            "age": random.randint(18, 80),
        }
        data.update(overrides)
        return data

    @staticmethod
    def create_batch(n: int) -> List[Dict[str, Any]]:
        """Generate a list of n users."""
        return [UserFactory.create() for _ in range(n)]

    # Aliases for compatibility
    @staticmethod
    def create_user(**kwargs):
        """Alias for create (for compatibility)."""
        return UserFactory.create(**kwargs)

    @staticmethod
    def create_multiple_users(n: int):
        """Alias for create_batch (for compatibility)."""
        return UserFactory.create_batch(n)

class PostFactory:
    """Factory for generating post test data."""
    @staticmethod
    def create(user_id=None, **overrides) -> Dict[str, Any]:
        """Generate a single post (optionally with user_id and overrides)."""
        data = {
            "id": random.randint(1, 10000),
            "userId": user_id or random.randint(1, 10000),
            "title": fake.sentence(),
            "body": fake.text(),
        }
        data.update(overrides)
        return data

    @staticmethod
    def create_batch(n: int, user_id=None) -> List[Dict[str, Any]]:
        """Generate a list of n posts (optionally for a user)."""
        return [PostFactory.create(user_id=user_id) for _ in range(n)]

    # Aliases for compatibility
    @staticmethod
    def create_post(**kwargs):
        """Alias for create (for compatibility)."""
        return PostFactory.create(**kwargs)

    @staticmethod
    def create_posts_for_user(user_id, count=1):
        """Generate count posts for a specific user."""
        return PostFactory.create_batch(count, user_id=user_id)

class CommentFactory:
    """Factory for generating comment test data."""
    @staticmethod
    def create(post_id=None, **overrides) -> Dict[str, Any]:
        """Generate a single comment (optionally with post_id and overrides)."""
        data = {
            "id": random.randint(1, 10000),
            "postId": post_id or random.randint(1, 100),
            "name": fake.name(),  # Use real name with space
            "email": fake.email(),
            "body": fake.text(),
        }
        data.update(overrides)
        return data

    @staticmethod
    def create_batch(n: int, post_id=None) -> List[Dict[str, Any]]:
        """Generate a list of n comments (optionally for a post)."""
        return [CommentFactory.create(post_id=post_id) for _ in range(n)]

    # Aliases for compatibility
    @staticmethod
    def create_comment(**kwargs):
        """Alias for create (for compatibility)."""
        return CommentFactory.create(**kwargs)

    @staticmethod
    def create_comments_for_post(post_id, count):
        """Generate count comments for a specific post."""
        return CommentFactory.create_batch(count, post_id=post_id)

    @staticmethod
    def create_comments_for_user_posts(user_id, posts_per_user, comments_per_post):
        """Generate comments for all posts of a user (combination)."""
        comments = []
        for _ in range(posts_per_user):
            post_id = random.randint(1, 10000)
            comments.extend(CommentFactory.create_batch(comments_per_post, post_id=post_id))
        return comments 