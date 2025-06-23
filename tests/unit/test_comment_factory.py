# test_comment_factory.py
"""
Unit tests for the comment factory: validation of comment generation and edge cases.
"""
import pytest
from typing import Dict, Any, List
from src.test_data_factory import CommentFactory

class TestCommentFactory:
    
    async def test_create_single_comment(self, comment_factory):
        """Test creating a single comment"""
        comment = comment_factory.create_comment()
        
        # Validate that all required fields are present
        assert "id" in comment
        assert "postId" in comment
        assert "name" in comment
        assert "email" in comment
        assert "body" in comment
        
        # Validate that ID is a positive number
        assert comment["id"] > 0
        assert comment["postId"] > 0
        
        # Validate that email contains @
        assert "@" in comment["email"]
        
        # Validate that body is not empty
        assert len(comment["body"]) > 0

    async def test_create_comment_with_post_id(self, comment_factory):
        """Test creating a comment with a specific post ID"""
        post_id = 42
        comment = comment_factory.create_comment(post_id=post_id)
        
        assert comment["postId"] == post_id
        assert comment["name"] and comment["email"] and comment["body"]

    async def test_create_comment_with_overrides(self, comment_factory):
        """Test creating a comment with overridden fields"""
        custom_comment = comment_factory.create_comment(
            post_id=123,
            name="Test User",
            email="test@example.com",
            body="This is a test comment"
        )
        
        assert custom_comment["postId"] == 123
        assert custom_comment["name"] == "Test User"
        assert custom_comment["email"] == "test@example.com"
        assert custom_comment["body"] == "This is a test comment"

    async def test_create_multiple_comments_for_post(self, comment_factory):
        """Test creating multiple comments for a post"""
        post_id = 15
        comments = comment_factory.create_comments_for_post(post_id=post_id, count=3)
        
        assert len(comments) == 3
        
        # Validate that all comments belong to the correct post
        for comment in comments:
            assert comment["postId"] == post_id
            assert comment["id"] > 0
            assert "@" in comment["email"]

    async def test_create_comments_for_user_posts(self, comment_factory):
        """Test creating comments for multiple posts of a user"""
        user_id = 7
        comments = comment_factory.create_comments_for_user_posts(
            user_id=user_id,
            posts_per_user=2,
            comments_per_post=3
        )
        
        # Expected 2 posts * 3 comments = 6 comments
        assert len(comments) == 6
        
        # Validate that all comments have valid data
        for comment in comments:
            assert comment["postId"] > 0
            assert comment["name"] and comment["email"] and comment["body"]

    @pytest.mark.parametrize("comment_count", [1, 3, 5])
    async def test_dynamic_comment_creation(self, comment_factory, comment_count):
        """Test creating different numbers of comments"""
        comments = comment_factory.create_comments_for_post(post_id=25, count=comment_count)
        
        assert len(comments) == comment_count
        
        # Validate that all comments have unique IDs
        comment_ids = [comment["id"] for comment in comments]
        assert len(set(comment_ids)) == comment_count

    async def test_comment_data_realism(self, comment_factory):
        """Test that generated comment data is realistic"""
        comment = comment_factory.create_comment()
        
        # Test that name is a realistic name (contains space)
        assert " " in comment["name"]
        
        # Test that email is a valid format
        assert "@" in comment["email"]
        assert "." in comment["email"]
        
        # Test that body is a reasonable length
        assert 10 < len(comment["body"]) < 1000
        
        # Test that postId is within a reasonable range
        assert 1 <= comment["postId"] <= 100

    def test_create_comment(self):
        """Test that a single comment is correctly created."""
        comment = CommentFactory.create()
        assert "id" in comment and "postId" in comment 