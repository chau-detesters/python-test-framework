"""
Factory voor het genereren van testdata (users, posts, comments) voor data-driven tests.
"""
from faker import Faker
import random
from typing import Dict, Any, List

fake = Faker()

class UserFactory:
    """Factory voor het genereren van user testdata."""
    @staticmethod
    def create(**overrides) -> Dict[str, Any]:
        """Genereer een enkele user (optioneel met overrides)."""
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
        """Genereer een lijst van n users."""
        return [UserFactory.create() for _ in range(n)]

    # Aliassen voor compatibiliteit
    @staticmethod
    def create_user(**kwargs):
        """Alias voor create (voor compatibiliteit)."""
        return UserFactory.create(**kwargs)

    @staticmethod
    def create_multiple_users(n: int):
        """Alias voor create_batch (voor compatibiliteit)."""
        return UserFactory.create_batch(n)

class PostFactory:
    """Factory voor het genereren van post testdata."""
    @staticmethod
    def create(user_id=None, **overrides) -> Dict[str, Any]:
        """Genereer een enkele post (optioneel met user_id en overrides)."""
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
        """Genereer een lijst van n posts (optioneel voor een user)."""
        return [PostFactory.create(user_id=user_id) for _ in range(n)]

    # Aliassen voor compatibiliteit
    @staticmethod
    def create_post(**kwargs):
        """Alias voor create (voor compatibiliteit)."""
        return PostFactory.create(**kwargs)

    @staticmethod
    def create_posts_for_user(user_id, count=1):
        """Genereer count posts voor een specifieke user."""
        return PostFactory.create_batch(count, user_id=user_id)

class CommentFactory:
    """Factory voor het genereren van comment testdata."""
    @staticmethod
    def create(post_id=None, **overrides) -> Dict[str, Any]:
        """Genereer een enkele comment (optioneel met post_id en overrides)."""
        data = {
            "id": random.randint(1, 10000),
            "postId": post_id or random.randint(1, 100),
            "name": fake.name(),  # Gebruik echte naam met spatie
            "email": fake.email(),
            "body": fake.text(),
        }
        data.update(overrides)
        return data

    @staticmethod
    def create_batch(n: int, post_id=None) -> List[Dict[str, Any]]:
        """Genereer een lijst van n comments (optioneel voor een post)."""
        return [CommentFactory.create(post_id=post_id) for _ in range(n)]

    # Aliassen voor compatibiliteit
    @staticmethod
    def create_comment(**kwargs):
        """Alias voor create (voor compatibiliteit)."""
        return CommentFactory.create(**kwargs)

    @staticmethod
    def create_comments_for_post(post_id, count):
        """Genereer count comments voor een specifieke post."""
        return CommentFactory.create_batch(count, post_id=post_id)

    @staticmethod
    def create_comments_for_user_posts(user_id, posts_per_user, comments_per_post):
        """Genereer comments voor alle posts van een user (combinatie)."""
        comments = []
        for _ in range(posts_per_user):
            post_id = random.randint(1, 10000)
            comments.extend(CommentFactory.create_batch(comments_per_post, post_id=post_id))
        return comments 