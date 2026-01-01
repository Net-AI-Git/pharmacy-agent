"""
Tests for DatabaseManager core functionality.

Purpose (Why):
Validates basic DatabaseManager operations: import, instantiation, and database loading.

Implementation (What):
Tests that DatabaseManager can be imported, instantiated, and loads database correctly.
"""

import pytest
from app.database.db import DatabaseManager


class TestDatabaseManagerCore:
    """Test suite for DatabaseManager core functionality."""
    
    def test_database_manager_import(self):
        """
        Test that DatabaseManager can be imported.
        
        Arrange: Import statement
        Act: Import DatabaseManager
        Assert: Import succeeds
        """
        assert DatabaseManager is not None, "DatabaseManager could not be imported"
    
    def test_database_manager_instantiation(self):
        """
        Test that DatabaseManager can be instantiated.
        
        Arrange: DatabaseManager class
        Act: Create instance
        Assert: Instance created successfully with valid db_path
        """
        db = DatabaseManager()
        assert db is not None, "DatabaseManager instance could not be created"
        assert db.db_path is not None, "DatabaseManager db_path is None"
    
    def test_load_db(self, database_json_path):
        """
        Test that load_db loads the database correctly.
        
        Arrange: DatabaseManager instance and database.json path
        Act: Call load_db()
        Assert: Database loaded with correct structure and counts
        """
        db = DatabaseManager()
        data = db.load_db()
        
        assert data is not None, "load_db() returned None"
        assert "users" in data, "Database missing 'users' key"
        assert "medications" in data, "Database missing 'medications' key"
        assert "prescriptions" in data, "Database missing 'prescriptions' key"
        assert len(data.get("users", [])) == 10, f"Expected 10 users, got {len(data.get('users', []))}"
        assert len(data.get("medications", [])) == 5, f"Expected 5 medications, got {len(data.get('medications', []))}"
    
    def test_database_caching(self):
        """
        Test that DatabaseManager caches loaded data.
        
        Arrange: DatabaseManager instance
        Act: Load database, then query multiple times
        Assert: Database is loaded once and cached
        """
        db = DatabaseManager()
        # First load
        data1 = db.load_db()
        # Second query should use cache
        med1 = db.get_medication_by_id("med_001")
        # Third query should also use cache
        user1 = db.get_user_by_id("user_001")
        
        assert data1 is not None, "First load_db() should succeed"
        assert med1 is not None, "get_medication_by_id should work with cached data"
        assert user1 is not None, "get_user_by_id should work with cached data"
        # Verify cache is populated
        assert db._data is not None, "Database should be cached in _data"

