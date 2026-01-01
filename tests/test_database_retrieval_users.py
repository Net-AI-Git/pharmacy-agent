"""
Tests for user retrieval operations.

Purpose (Why):
Validates that users can be retrieved correctly by ID with all required fields.

Implementation (What):
Tests get_user_by_id with various scenarios including success, not found, and field validation.
"""

import pytest
from app.database.db import DatabaseManager


class TestUserRetrieval:
    """Test suite for user retrieval."""
    
    def test_get_user_by_id_success(self):
        """
        Test that get_user_by_id finds users correctly.
        
        Arrange: DatabaseManager instance
        Act: Call get_user_by_id("user_001")
        Assert: Returns User instance with correct ID
        """
        db = DatabaseManager()
        user = db.get_user_by_id("user_001")
        
        assert user is not None, "get_user_by_id('user_001') returned None"
        assert user.user_id == "user_001", f"Expected user_id='user_001', got '{user.user_id}'"
    
    def test_get_user_by_id_not_found(self):
        """
        Test that get_user_by_id returns None for non-existent ID.
        
        Arrange: DatabaseManager instance
        Act: Call get_user_by_id("user_nonexistent")
        Assert: Returns None
        """
        db = DatabaseManager()
        user = db.get_user_by_id("user_nonexistent")
        
        assert user is None, f"Expected None for non-existent user, got {user}"
    
    def test_get_user_by_id_retrieves_all_fields(self):
        """
        Test that get_user_by_id retrieves user with all required fields.
        
        Arrange: DatabaseManager instance
        Act: Call get_user_by_id("user_001")
        Assert: User has all required fields populated
        """
        db = DatabaseManager()
        user = db.get_user_by_id("user_001")
        
        assert user is not None, "User user_001 should exist"
        assert user.user_id == "user_001", f"Expected user_id='user_001', got '{user.user_id}'"
        assert len(user.name) > 0, "User must have name"
        assert len(user.email) > 0, "User must have email"
        assert isinstance(user.prescriptions, list), "User prescriptions must be a list"
    
    def test_get_all_users(self):
        """
        Test that we can retrieve all users.
        
        Arrange: DatabaseManager instance
        Act: Get all users by ID
        Assert: Can retrieve all 10 users
        """
        db = DatabaseManager()
        all_users = []
        for user_id in [f"user_{i:03d}" for i in range(1, 11)]:
            user = db.get_user_by_id(user_id)
            if user:
                all_users.append(user)
        
        assert len(all_users) == 10, f"Expected to retrieve all 10 users, got {len(all_users)}"

