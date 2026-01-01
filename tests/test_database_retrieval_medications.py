"""
Tests for medication retrieval operations.

Purpose (Why):
Validates that medications can be retrieved correctly by ID with all required fields.

Implementation (What):
Tests get_medication_by_id with various scenarios including success, not found, and field validation.
"""

import pytest
from app.database.db import DatabaseManager


class TestMedicationRetrieval:
    """Test suite for medication retrieval."""
    
    def test_get_medication_by_id_success(self):
        """
        Test that get_medication_by_id finds medications correctly.
        
        Arrange: DatabaseManager instance
        Act: Call get_medication_by_id("med_001")
        Assert: Returns Medication instance with correct ID
        """
        db = DatabaseManager()
        med = db.get_medication_by_id("med_001")
        
        assert med is not None, "get_medication_by_id('med_001') returned None"
        assert med.medication_id == "med_001", f"Expected medication_id='med_001', got '{med.medication_id}'"
    
    def test_get_medication_by_id_not_found(self):
        """
        Test that get_medication_by_id returns None for non-existent ID.
        
        Arrange: DatabaseManager instance
        Act: Call get_medication_by_id("med_nonexistent")
        Assert: Returns None
        """
        db = DatabaseManager()
        med = db.get_medication_by_id("med_nonexistent")
        
        assert med is None, f"Expected None for non-existent medication, got {med}"
    
    def test_get_medication_by_id_retrieves_all_fields(self):
        """
        Test that get_medication_by_id retrieves medication with all required fields.
        
        Arrange: DatabaseManager instance
        Act: Call get_medication_by_id("med_001")
        Assert: Medication has all required fields populated
        """
        db = DatabaseManager()
        med = db.get_medication_by_id("med_001")
        
        assert med is not None, "Medication med_001 should exist"
        assert med.medication_id == "med_001", f"Expected medication_id='med_001', got '{med.medication_id}'"
        assert len(med.name_he) > 0, "Medication must have Hebrew name"
        assert len(med.name_en) > 0, "Medication must have English name"
        assert len(med.active_ingredients) > 0, "Medication must have active ingredients"
        assert len(med.dosage_instructions) > 0, "Medication must have dosage instructions"
        assert med.stock is not None, "Medication must have stock information"
        assert hasattr(med.stock, 'available'), "Stock must have 'available' field"
        assert hasattr(med.stock, 'quantity_in_stock'), "Stock must have 'quantity_in_stock' field"
    
    def test_get_all_medications(self):
        """
        Test that we can retrieve all medications.
        
        Arrange: DatabaseManager instance
        Act: Get all medications by ID
        Assert: Can retrieve all 5 medications
        """
        db = DatabaseManager()
        all_meds = []
        for med_id in ["med_001", "med_002", "med_003", "med_004", "med_005"]:
            med = db.get_medication_by_id(med_id)
            if med:
                all_meds.append(med)
        
        assert len(all_meds) == 5, f"Expected to retrieve all 5 medications, got {len(all_meds)}"
    
    def test_medication_stock_information(self):
        """
        Test that medication stock information is properly retrieved.
        
        Arrange: DatabaseManager instance
        Act: Get medication and check stock
        Assert: Stock information is complete and valid
        """
        db = DatabaseManager()
        med = db.get_medication_by_id("med_001")
        
        assert med is not None, "Medication med_001 should exist"
        assert med.stock is not None, "Medication must have stock information"
        assert isinstance(med.stock.available, bool), f"Stock available must be bool, got {type(med.stock.available)}"
        assert isinstance(med.stock.quantity_in_stock, int), (
            f"Stock quantity_in_stock must be int, got {type(med.stock.quantity_in_stock)}"
        )
        assert med.stock.quantity_in_stock >= 0, f"Stock quantity must be non-negative, got {med.stock.quantity_in_stock}"
        assert len(med.stock.last_restocked) > 0, "Stock must have last_restocked date"

