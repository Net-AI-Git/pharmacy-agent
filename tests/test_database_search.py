"""
Tests for medication search operations.

Purpose (Why):
Validates that medications can be searched by name in Hebrew and English with various edge cases.

Implementation (What):
Tests search_medications_by_name with different languages, partial matches, case sensitivity, and edge cases.
"""

import pytest
from app.database.db import DatabaseManager


class TestMedicationSearch:
    """Test suite for medication search."""
    
    def test_search_medications_by_name_hebrew(self):
        """
        Test that search_medications_by_name finds medications by Hebrew name.
        
        Arrange: DatabaseManager instance
        Act: Call search_medications_by_name("Acamol", "he")
        Assert: Returns list with at least one Medication
        """
        db = DatabaseManager()
        meds = db.search_medications_by_name("Acamol", "he")
        
        assert isinstance(meds, list), f"Expected list, got {type(meds)}"
        assert len(meds) > 0, f"Expected at least 1 medication for 'Acamol', got {len(meds)}"
        assert any("Acamol" in med.name_he for med in meds), "At least one medication should have 'Acamol' in Hebrew name"
    
    def test_search_medications_by_name_english(self):
        """
        Test that search_medications_by_name finds medications by English name.
        
        Arrange: DatabaseManager instance
        Act: Call search_medications_by_name("Acetaminophen", "en")
        Assert: Returns list with at least one Medication
        """
        db = DatabaseManager()
        meds = db.search_medications_by_name("Acetaminophen", "en")
        
        assert isinstance(meds, list), f"Expected list, got {type(meds)}"
        assert len(meds) > 0, f"Expected at least 1 medication for 'Acetaminophen', got {len(meds)}"
        assert any("Acetaminophen" in med.name_en for med in meds), "At least one medication should have 'Acetaminophen' in English name"
    
    def test_search_medications_by_name_both_languages(self):
        """
        Test that search_medications_by_name searches both languages when language is None.
        
        Arrange: DatabaseManager instance
        Act: Call search_medications_by_name("Acamol")
        Assert: Returns list with at least one Medication
        """
        db = DatabaseManager()
        meds = db.search_medications_by_name("Acamol")
        
        assert isinstance(meds, list), f"Expected list, got {type(meds)}"
        assert len(meds) > 0, f"Expected at least 1 medication for 'Acamol' (both languages), got {len(meds)}"
    
    def test_search_medications_by_name_partial_match(self):
        """
        Test that search_medications_by_name finds medications with partial name match.
        
        Arrange: DatabaseManager instance
        Act: Call search_medications_by_name("Acam") (partial match)
        Assert: Returns medications containing the partial string
        """
        db = DatabaseManager()
        meds = db.search_medications_by_name("Acam")
        
        assert isinstance(meds, list), f"Expected list, got {type(meds)}"
        assert len(meds) > 0, f"Expected at least 1 medication for partial 'Acam', got {len(meds)}"
        assert any("Acam" in med.name_he or "Acam" in med.name_en for med in meds), (
            "At least one medication should match partial 'Acam'"
        )
    
    def test_search_medications_by_name_case_insensitive(self):
        """
        Test that search_medications_by_name is case-insensitive.
        
        Arrange: DatabaseManager instance
        Act: Call search_medications_by_name("ACAMOL") (uppercase)
        Assert: Returns medications regardless of case
        """
        db = DatabaseManager()
        meds_upper = db.search_medications_by_name("ACAMOL")
        meds_lower = db.search_medications_by_name("acamol")
        
        assert len(meds_upper) > 0, "Uppercase search should find medications"
        assert len(meds_lower) > 0, "Lowercase search should find medications"
        assert len(meds_upper) == len(meds_lower), (
            f"Case-insensitive search should return same results, got {len(meds_upper)} vs {len(meds_lower)}"
        )
    
    def test_search_medications_by_name_empty_string(self):
        """
        Test that search_medications_by_name handles empty string gracefully.
        
        Arrange: DatabaseManager instance
        Act: Call search_medications_by_name("")
        Assert: Returns empty list
        """
        db = DatabaseManager()
        meds = db.search_medications_by_name("")
        
        assert isinstance(meds, list), f"Expected list, got {type(meds)}"
        assert len(meds) == 0, f"Empty string search should return empty list, got {len(meds)}"
    
    def test_search_medications_by_name_not_found(self):
        """
        Test that search_medications_by_name returns empty list for non-existent medication.
        
        Arrange: DatabaseManager instance
        Act: Call search_medications_by_name("NonExistentMedication123")
        Assert: Returns empty list
        """
        db = DatabaseManager()
        meds = db.search_medications_by_name("NonExistentMedication123")
        
        assert isinstance(meds, list), f"Expected list, got {type(meds)}"
        assert len(meds) == 0, f"Non-existent medication search should return empty list, got {len(meds)}"

