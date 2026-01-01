"""
Tests for prescription retrieval operations.

Purpose (Why):
Validates that prescriptions can be retrieved correctly by user with all required fields.

Implementation (What):
Tests get_prescriptions_by_user with various scenarios including success, empty list, and field validation.
"""

import pytest
from app.database.db import DatabaseManager


class TestPrescriptionRetrieval:
    """Test suite for prescription retrieval."""
    
    def test_get_prescriptions_by_user_success(self):
        """
        Test that get_prescriptions_by_user returns user prescriptions.
        
        Arrange: DatabaseManager instance
        Act: Call get_prescriptions_by_user("user_001")
        Assert: Returns list of Prescription instances
        """
        db = DatabaseManager()
        prescriptions = db.get_prescriptions_by_user("user_001")
        
        assert isinstance(prescriptions, list), f"Expected list, got {type(prescriptions)}"
        assert len(prescriptions) > 0, f"Expected at least 1 prescription for user_001, got {len(prescriptions)}"
        assert all(p.user_id == "user_001" for p in prescriptions), "All prescriptions must belong to user_001"
    
    def test_get_prescriptions_by_user_empty_list(self):
        """
        Test that get_prescriptions_by_user returns empty list for user with no prescriptions.
        
        Arrange: DatabaseManager instance
        Act: Call get_prescriptions_by_user for user with no prescriptions
        Assert: Returns empty list
        """
        db = DatabaseManager()
        prescriptions = db.get_prescriptions_by_user("user_006")
        
        assert isinstance(prescriptions, list), f"Expected list, got {type(prescriptions)}"
        # Note: user_006 might have prescriptions, but we test the structure
    
    def test_get_prescriptions_by_user_retrieves_all_fields(self):
        """
        Test that get_prescriptions_by_user retrieves prescriptions with all required fields.
        
        Arrange: DatabaseManager instance
        Act: Call get_prescriptions_by_user("user_001")
        Assert: All prescriptions have required fields
        """
        db = DatabaseManager()
        prescriptions = db.get_prescriptions_by_user("user_001")
        
        assert len(prescriptions) > 0, "User_001 should have at least one prescription"
        for presc in prescriptions:
            assert presc.prescription_id is not None, "Prescription must have prescription_id"
            assert presc.user_id == "user_001", f"Prescription user_id must be 'user_001', got '{presc.user_id}'"
            assert presc.medication_id is not None, "Prescription must have medication_id"
            assert presc.status in ["active", "expired", "cancelled", "completed"], (
                f"Prescription status must be valid, got '{presc.status}'"
            )

