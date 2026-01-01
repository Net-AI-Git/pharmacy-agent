"""
Tests for Task 2.1-2.2: database.json structure and content validation.

Purpose (Why):
Validates that database.json exists and has correct structure with required data.

Implementation (What):
Checks file existence, validates JSON structure, and verifies data counts.
"""

import json
import pytest
from pathlib import Path


class TestDatabaseJson:
    """Test suite for database.json validation."""
    
    def test_database_json_exists(self, database_json_path: Path):
        """
        Test that database.json exists.
        
        Arrange: Database JSON path fixture
        Act: Check file existence
        Assert: File exists
        """
        assert database_json_path.exists(), f"database.json does not exist at {database_json_path}"
        assert database_json_path.is_file(), f"{database_json_path} is not a file"
    
    def test_database_json_valid_structure(self, database_json_path: Path):
        """
        Test that database.json has valid JSON structure.
        
        Arrange: Database JSON path
        Act: Parse JSON
        Assert: Valid JSON with required keys
        """
        with open(database_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        required_keys = ["users", "medications", "prescriptions"]
        missing_keys = [k for k in required_keys if k not in data]
        
        assert len(missing_keys) == 0, (
            f"Database JSON missing required keys: {', '.join(missing_keys)}"
        )
    
    def test_database_json_user_count(self, database_json_path: Path):
        """
        Test that database.json contains exactly 10 users.
        
        Arrange: Database JSON path
        Act: Parse JSON and count users
        Assert: Exactly 10 users
        """
        with open(database_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        user_count = len(data.get("users", []))
        assert user_count == 10, f"Expected 10 users, got {user_count}"
    
    def test_database_json_medication_count(self, database_json_path: Path):
        """
        Test that database.json contains exactly 5 medications.
        
        Arrange: Database JSON path
        Act: Parse JSON and count medications
        Assert: Exactly 5 medications
        """
        with open(database_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        med_count = len(data.get("medications", []))
        assert med_count == 5, f"Expected 5 medications, got {med_count}"
    
    def test_database_json_user_structure(self, database_json_path: Path):
        """
        Test that each user has required fields.
        
        Arrange: Database JSON path
        Act: Parse JSON and check user structure
        Assert: Each user has user_id, name, email, prescriptions
        """
        with open(database_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        required_fields = ["user_id", "name", "email", "prescriptions"]
        for i, user in enumerate(data.get("users", [])):
            missing_fields = [f for f in required_fields if f not in user]
            assert len(missing_fields) == 0, (
                f"User {i} missing required fields: {', '.join(missing_fields)}"
            )
    
    def test_database_json_medication_structure(self, database_json_path: Path):
        """
        Test that each medication has required fields including active_ingredients and dosage_instructions.
        
        Arrange: Database JSON path
        Act: Parse JSON and check medication structure
        Assert: Each medication has all required fields
        """
        with open(database_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        required_fields = [
            "medication_id", "name_he", "name_en", "active_ingredients",
            "dosage_forms", "dosage_instructions", "usage_instructions",
            "requires_prescription", "description", "stock"
        ]
        
        for i, medication in enumerate(data.get("medications", [])):
            missing_fields = [f for f in required_fields if f not in medication]
            assert len(missing_fields) == 0, (
                f"Medication {i} missing required fields: {', '.join(missing_fields)}"
            )
            
            # Critical fields must not be empty
            assert len(medication.get("active_ingredients", [])) > 0, (
                f"Medication {i} must have at least one active ingredient"
            )
            assert len(medication.get("dosage_instructions", "")) > 0, (
                f"Medication {i} must have dosage_instructions"
            )

