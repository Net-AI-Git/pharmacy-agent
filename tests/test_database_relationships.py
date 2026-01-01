"""
Tests for database relationships and data integrity.

Purpose (Why):
Validates that relationships between entities (prescriptions, medications, users) are correct
and data integrity is maintained.

Implementation (What):
Tests that prescriptions correctly link to medications and that all relationships are valid.
"""

import pytest
from app.database.db import DatabaseManager


class TestDatabaseRelationships:
    """Test suite for database relationships."""
    
    def test_prescription_medication_link(self):
        """
        Test that prescriptions correctly link to medications.
        
        Arrange: DatabaseManager instance
        Act: Get prescription and verify medication exists
        Assert: Prescription medication_id corresponds to existing medication
        """
        db = DatabaseManager()
        prescriptions = db.get_prescriptions_by_user("user_001")
        
        assert len(prescriptions) > 0, "User_001 should have prescriptions"
        for presc in prescriptions:
            med = db.get_medication_by_id(presc.medication_id)
            assert med is not None, (
                f"Prescription references medication_id '{presc.medication_id}' which should exist"
            )
            assert med.medication_id == presc.medication_id, (
                f"Prescription medication_id '{presc.medication_id}' should match medication"
            )

