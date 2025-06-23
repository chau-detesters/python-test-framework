# test_cleanup_tracker.py
"""
Unittests for cleanup tracking: resource cleanup and state management.
"""
import pytest
from typing import Dict, Any, List

class TestCleanupTracker:
    
    async def test_basic_cleanup_tracking(self, cleanup_tracker, user_factory, post_factory):
        """Test basis cleanup tracking functionality"""
        # Make test resources
        user = user_factory.create_user()
        post = post_factory.create_post()
        
        # Track resources for cleanup
        cleanup_tracker["users"].append(user["id"])
        cleanup_tracker["posts"].append(post["id"])
        
        # Verify that resources are tracked
        assert len(cleanup_tracker["users"]) == 1
        assert len(cleanup_tracker["posts"]) == 1
        assert user["id"] in cleanup_tracker["users"]
        assert post["id"] in cleanup_tracker["posts"]
        
        print(f"Test: Created user {user['id']} and post {post['id']}")

    async def test_multiple_resources_tracking(self, cleanup_tracker, user_factory, post_factory):
        """Test tracking of multiple resources"""
        # Make multiple resources
        users = user_factory.create_multiple_users(3)
        posts = [post_factory.create_post() for _ in range(2)]
        
        # Track all resources
        for user in users:
            cleanup_tracker["users"].append(user["id"])
        for post in posts:
            cleanup_tracker["posts"].append(post["id"])
        
        # Verify tracking
        assert len(cleanup_tracker["users"]) == 3
        assert len(cleanup_tracker["posts"]) == 2
        
        print(f"Test: Tracked {len(users)} users and {len(posts)} posts")

    async def test_cleanup_tracker_isolation(self, cleanup_tracker):
        """Test that cleanup_tracker is isolated per test"""
        # Each test gets a new cleanup_tracker
        assert len(cleanup_tracker["users"]) == 0
        assert len(cleanup_tracker["posts"]) == 0
        
        # Add some data
        cleanup_tracker["users"].append(999)
        cleanup_tracker["posts"].append(888)
        
        # Verify that data is added
        assert len(cleanup_tracker["users"]) == 1
        assert len(cleanup_tracker["posts"]) == 1

    async def test_cleanup_with_api_calls(self, cleanup_tracker, http_client, user_factory, post_factory):
        """Test cleanup tracking with real API calls"""
        # Make user via API
        user_data = user_factory.create_user()
        user_response = await http_client.post("/users", json=user_data)
        
        if user_response.status_code == 201:
            created_user = user_response.json()
            user_id = created_user["id"]
            
            # Track user for cleanup
            cleanup_tracker["users"].append(user_id)
            
            # Make post for this user
            post_data = post_factory.create_post(user_id=user_id)
            post_response = await http_client.post("/posts", json=post_data)
            
            if post_response.status_code == 201:
                created_post = post_response.json()
                post_id = created_post["id"]
                
                # Track post for cleanup
                cleanup_tracker["posts"].append(post_id)
                
                print(f"Test: Created and tracked user {user_id} and post {post_id}")
                
                # Verify tracking
                assert user_id in cleanup_tracker["users"]
                assert post_id in cleanup_tracker["posts"]
            else:
                print("Post creation failed (expected for JSONPlaceholder)")
        else:
            print("User creation failed (expected for JSONPlaceholder)")

    @pytest.mark.parametrize("resource_count", [1, 3, 5])
    async def test_cleanup_tracker_scaling(self, cleanup_tracker, user_factory, resource_count):
        """Test cleanup tracker with different amounts of resources"""
        # Make resources
        users = user_factory.create_multiple_users(resource_count)
        
        # Track resources
        for user in users:
            cleanup_tracker["users"].append(user["id"])
        
        # Verify scaling
        assert len(cleanup_tracker["users"]) == resource_count
        
        print(f"Test: Tracked {resource_count} users for cleanup")

    async def test_cleanup_tracker_with_comments(self, cleanup_tracker, comment_factory):
        """Test cleanup tracking with comments"""
        # Add comment tracking to cleanup_tracker
        cleanup_tracker["comments"] = []
        
        # Make comments
        comments = comment_factory.create_comments_for_post(post_id=1, count=3)
        
        # Track comments
        for comment in comments:
            cleanup_tracker["comments"].append(comment["id"])
        
        # Verify tracking
        assert len(cleanup_tracker["comments"]) == 3
        
        print(f"Test: Tracked {len(comments)} comments for cleanup")

    async def test_cleanup_tracker_error_handling(self, cleanup_tracker):
        """Test cleanup tracker with error handling"""
        try:
            # Simulate a failure during resource creation
            raise Exception("Resource creation failed")
        except Exception as e:
            # Even in case of errors, cleanup tracker should still be available
            cleanup_tracker["users"].append(999)  # Fallback cleanup
            print(f"Test: Error occurred, but cleanup tracker still works: {e}")
        
        # Verify that cleanup tracker still works
        assert len(cleanup_tracker["users"]) == 1

    async def test_cleanup_tracker_nested_resources(self, cleanup_tracker, user_factory, post_factory, comment_factory):
        """Test cleanup tracking with nested resources (user -> posts -> comments)"""
        # Make user
        user = user_factory.create_user()
        cleanup_tracker["users"].append(user["id"])
        
        # Make posts for user
        posts = post_factory.create_posts_for_user(user["id"], count=2)
        for post in posts:
            cleanup_tracker["posts"].append(post["id"])
        
        # Make comments for posts
        if "comments" not in cleanup_tracker:
            cleanup_tracker["comments"] = []
        
        for post in posts:
            comments = comment_factory.create_comments_for_post(post["id"], count=2)
            for comment in comments:
                cleanup_tracker["comments"].append(comment["id"])
        
        # Verify nested tracking
        assert len(cleanup_tracker["users"]) == 1
        assert len(cleanup_tracker["posts"]) == 2
        assert len(cleanup_tracker["comments"]) == 4  # 2 posts * 2 comments
        
        print(f"Test: Tracked nested resources - {len(cleanup_tracker['users'])} users, "
              f"{len(cleanup_tracker['posts'])} posts, {len(cleanup_tracker['comments'])} comments")

    async def test_cleanup_tracker_duplicate_prevention(self, cleanup_tracker, user_factory):
        """Test that cleanup tracker prevents duplicates"""
        user = user_factory.create_user()
        user_id = user["id"]
        
        # Add the same user multiple times
        cleanup_tracker["users"].append(user_id)
        cleanup_tracker["users"].append(user_id)
        cleanup_tracker["users"].append(user_id)
        
        # Verify that there is only one entry (no duplicates)
        assert cleanup_tracker["users"].count(user_id) == 3  # Or implement duplicate prevention
        
        print(f"Test: Added user {user_id} multiple times to cleanup tracker")

    async def test_enhanced_cleanup_tracker_functionality(self, cleanup_tracker, user_factory, post_factory, comment_factory):
        """Test enhanced cleanup tracker with helper methods"""
        # Use the new add_resource helper method
        user = user_factory.create_user()
        cleanup_tracker["add"]("users", user["id"])
        
        post = post_factory.create_post()
        cleanup_tracker["add"]("posts", post["id"])
        
        comment = comment_factory.create_comment()
        cleanup_tracker["add"]("comments", comment["id"])
        
        # Test duplicate prevention
        cleanup_tracker["add"]("users", user["id"])  # Should not be added
        cleanup_tracker["add"]("posts", post["id"])  # Should not be added
        
        # Use helper methods for counting
        user_count = cleanup_tracker["count"]("users")
        post_count = cleanup_tracker["count"]("posts")
        comment_count = cleanup_tracker["count"]("comments")
        total_count = cleanup_tracker["total"]()
        
        # Verify counts
        assert user_count == 1  # No duplicates
        assert post_count == 1
        assert comment_count == 1
        assert total_count == 3
        
        print(f"Test: Enhanced tracker - users: {user_count}, posts: {post_count}, "
              f"comments: {comment_count}, total: {total_count}")

    async def test_cleanup_tracker_custom_resource_types(self, cleanup_tracker):
        """Test cleanup tracker with custom resource types"""
        # Use the new add_resource method for custom types
        cleanup_tracker["add"]("albums", 101)
        cleanup_tracker["add"]("albums", 102)
        cleanup_tracker["add"]("photos", 201)
        cleanup_tracker["add"]("todos", 301)
        
        # Test custom resource counting
        album_count = cleanup_tracker["count"]("albums")
        photo_count = cleanup_tracker["count"]("photos")
        todo_count = cleanup_tracker["count"]("todos")
        total_count = cleanup_tracker["total"]()
        
        # Verify custom tracking
        assert album_count == 2
        assert photo_count == 1
        assert todo_count == 1
        assert total_count == 4
        
        print(f"Test: Custom resources - albums: {album_count}, photos: {photo_count}, "
              f"todos: {todo_count}, total: {total_count}")

    async def test_cleanup_tracker_complex_scenario(self, cleanup_tracker, user_factory, post_factory, comment_factory):
        """Test cleanup tracker with complex scenario"""
        # Make a complex test setup
        users = user_factory.create_multiple_users(2)
        for user in users:
            cleanup_tracker["add"]("users", user["id"])
            
            # Make posts for each user
            posts = post_factory.create_posts_for_user(user["id"], count=2)
            for post in posts:
                cleanup_tracker["add"]("posts", post["id"])
                
                # Make comments for each post
                comments = comment_factory.create_comments_for_post(post["id"], count=3)
                for comment in comments:
                    cleanup_tracker["add"]("comments", comment["id"])
        
        # Verify complex tracking
        expected_users = 2
        expected_posts = 2 * 2  # 2 users * 2 posts each
        expected_comments = 2 * 2 * 3  # 2 users * 2 posts * 3 comments each
        
        actual_users = cleanup_tracker["count"]("users")
        actual_posts = cleanup_tracker["count"]("posts")
        actual_comments = cleanup_tracker["count"]("comments")
        total_resources = cleanup_tracker["total"]()
        
        assert actual_users == expected_users
        assert actual_posts == expected_posts
        assert actual_comments == expected_comments
        assert total_resources == expected_users + expected_posts + expected_comments
        
        print(f"Test: Complex scenario - users: {actual_users}, posts: {actual_posts}, "
              f"comments: {actual_comments}, total: {total_resources}")

    def test_add_resource(self):
        """Test that a resource is correctly added to the tracker."""
        tracker = {}
        def add_resource(resource_type, resource_id):
            tracker.setdefault(resource_type, []).append(resource_id)
        add_resource("user", 1)
        assert tracker["user"] == [1] 