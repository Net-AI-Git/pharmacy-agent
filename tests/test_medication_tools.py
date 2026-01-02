"""
Tests for Task 3.1: medication_tools.py

Purpose (Why):
Validates that medication search tool works correctly with various inputs,
handles edge cases, and provides proper error messages with suggestions.

Implementation (What):
Tests the get_medication_by_name function with:
- Valid medication names (Hebrew and English)
- Fuzzy matching (partial names)
- Non-existent medications
- Empty/invalid inputs
- Required fields validation
"""

import pytest
from app.tools.medication_tools import (
    get_medication_by_name,
    MedicationSearchInput,
    MedicationSearchResult,
    MedicationSearchError
)


class TestMedicationTools:
    """Test suite for medication tools."""
    
    def test_get_medication_by_name_exact_match_hebrew(self):
        """
        Test finding medication by exact Hebrew name.
        
        Arrange: Valid Hebrew medication name
        Act: Call get_medication_by_name with Hebrew name
        Assert: Returns medication with all required fields
        """
        # Arrange
        name = "אקמול"
        language = "he"
        
        # Act
        result = get_medication_by_name(name, language)
        
        # Assert
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        assert result["medication_id"] == "med_001", f"Expected medication_id='med_001', got '{result.get('medication_id')}'"
        assert result["name_he"] == "אקמול", f"Expected name_he='אקמול', got '{result.get('name_he')}'"
        assert "active_ingredients" in result, "Result must include active_ingredients (required field)"
        assert len(result["active_ingredients"]) > 0, f"Expected non-empty active_ingredients, got {result.get('active_ingredients')}"
        assert "dosage_instructions" in result, "Result must include dosage_instructions (required field)"
        assert result["dosage_instructions"], f"Expected non-empty dosage_instructions, got '{result.get('dosage_instructions')}'"
    
    def test_get_medication_by_name_exact_match_english(self):
        """
        Test finding medication by exact English name.
        
        Arrange: Valid English medication name
        Act: Call get_medication_by_name with English name
        Assert: Returns medication with all required fields
        """
        # Arrange
        name = "Acetaminophen"
        language = "en"
        
        # Act
        result = get_medication_by_name(name, language)
        
        # Assert
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        assert result["medication_id"] == "med_001", f"Expected medication_id='med_001', got '{result.get('medication_id')}'"
        assert result["name_en"] == "Acetaminophen", f"Expected name_en='Acetaminophen', got '{result.get('name_en')}'"
        assert "active_ingredients" in result, "Result must include active_ingredients (required field)"
        assert "dosage_instructions" in result, "Result must include dosage_instructions (required field)"
    
    def test_get_medication_by_name_fuzzy_matching_partial(self):
        """
        Test fuzzy matching with partial medication name.
        
        Arrange: Partial medication name
        Act: Call get_medication_by_name with partial name
        Assert: Returns medication using fuzzy matching
        """
        # Arrange
        name = "Acam"
        language = None
        
        # Act
        result = get_medication_by_name(name, language)
        
        # Assert
        assert "error" not in result, f"Expected success with fuzzy matching but got error: {result.get('error', 'Unknown error')}"
        assert "medication_id" in result, "Result must include medication_id"
        assert "Acamol" in result.get("name_he", "") or "Acetaminophen" in result.get("name_en", ""), \
            f"Expected medication name containing 'Acamol' or 'Acetaminophen', got {result.get('name_he')} / {result.get('name_en')}"
    
    def test_get_medication_by_name_case_insensitive(self):
        """
        Test that search is case-insensitive.
        
        Arrange: Medication name with different case
        Act: Call get_medication_by_name with lowercase name
        Assert: Returns medication regardless of case
        """
        # Arrange
        name = "aspirin"
        language = None
        
        # Act
        result = get_medication_by_name(name, language)
        
        # Assert
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        assert result["medication_id"] == "med_002", f"Expected medication_id='med_002', got '{result.get('medication_id')}'"
    
    def test_get_medication_by_name_not_found(self):
        """
        Test error handling when medication is not found.
        
        Arrange: Non-existent medication name
        Act: Call get_medication_by_name with invalid name
        Assert: Returns error with suggestions
        """
        # Arrange
        name = "NonExistentMedication123"
        language = None
        
        # Act
        result = get_medication_by_name(name, language)
        
        # Assert
        assert "error" in result, f"Expected error but got success result: {result}"
        assert result["error"], f"Expected non-empty error message, got '{result.get('error')}'"
        assert result["searched_name"] == name, f"Expected searched_name='{name}', got '{result.get('searched_name')}'"
        assert "suggestions" in result, "Error result must include suggestions"
        assert isinstance(result["suggestions"], list), f"Expected suggestions to be a list, got {type(result['suggestions'])}"
    
    def test_get_medication_by_name_empty_name(self):
        """
        Test validation with empty medication name.
        
        Arrange: Empty string as name
        Act: Call get_medication_by_name with empty name
        Assert: Returns error for empty input
        """
        # Arrange
        name = ""
        language = None
        
        # Act
        result = get_medication_by_name(name, language)
        
        # Assert
        assert "error" in result, f"Expected error for empty name but got success: {result}"
        assert "cannot be empty" in result["error"].lower() or "empty" in result["error"].lower(), \
            f"Expected error message about empty name, got '{result.get('error')}'"
    
    def test_get_medication_by_name_whitespace_only(self):
        """
        Test validation with whitespace-only name.
        
        Arrange: String with only whitespace
        Act: Call get_medication_by_name with whitespace
        Assert: Returns error for invalid input
        """
        # Arrange
        name = "   "
        language = None
        
        # Act
        result = get_medication_by_name(name, language)
        
        # Assert
        assert "error" in result, f"Expected error for whitespace-only name but got success: {result}"
    
    def test_get_medication_by_name_invalid_language(self):
        """
        Test handling of invalid language parameter.
        
        Arrange: Valid name with invalid language code
        Act: Call get_medication_by_name with invalid language
        Assert: Searches both languages (language ignored)
        """
        # Arrange
        name = "Acamol"
        language = "invalid_lang"
        
        # Act
        result = get_medication_by_name(name, language)
        
        # Assert
        # Should still find the medication (invalid language is ignored)
        assert "error" not in result, f"Expected success (invalid language ignored) but got error: {result.get('error', 'Unknown error')}"
        assert result["medication_id"] == "med_001", f"Expected medication_id='med_001', got '{result.get('medication_id')}'"
    
    def test_get_medication_by_name_no_language_filter(self):
        """
        Test search without language filter (searches both).
        
        Arrange: Valid name without language parameter
        Act: Call get_medication_by_name without language
        Assert: Returns medication from either language
        """
        # Arrange
        name = "Ibuprofen"
        language = None
        
        # Act
        result = get_medication_by_name(name, language)
        
        # Assert
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        assert result["medication_id"] == "med_004", f"Expected medication_id='med_004', got '{result.get('medication_id')}'"
    
    def test_get_medication_by_name_result_contains_all_fields(self):
        """
        Test that successful result contains all required and optional fields.
        
        Arrange: Valid medication name
        Act: Call get_medication_by_name
        Assert: Result contains all expected fields (basic medication info only, no stock/prescription)
        """
        # Arrange
        name = "Acamol"
        language = "he"
        
        # Act
        result = get_medication_by_name(name, language)
        
        # Assert
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        required_fields = [
            "medication_id", "name_he", "name_en", "active_ingredients",
            "dosage_forms", "dosage_instructions", "usage_instructions", "description"
        ]
        for field in required_fields:
            assert field in result, f"Result must include field '{field}', but it's missing"
        
        # Verify that stock and prescription fields are NOT included
        assert "requires_prescription" not in result, \
            "Result should NOT include requires_prescription (use check_prescription_requirement instead)"
        assert "available" not in result, \
            "Result should NOT include available (use check_stock_availability instead)"
        assert "quantity_in_stock" not in result, \
            "Result should NOT include quantity_in_stock (use check_stock_availability instead)"
    
    def test_get_medication_by_name_active_ingredients_not_empty(self):
        """
        Test that active_ingredients is not empty (required field).
        
        Arrange: Valid medication name
        Act: Call get_medication_by_name
        Assert: active_ingredients is present and non-empty
        """
        # Arrange
        name = "Aspirin"
        language = None
        
        # Act
        result = get_medication_by_name(name, language)
        
        # Assert
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        assert "active_ingredients" in result, "Result must include active_ingredients"
        assert isinstance(result["active_ingredients"], list), \
            f"Expected active_ingredients to be a list, got {type(result['active_ingredients'])}"
        assert len(result["active_ingredients"]) > 0, \
            f"Expected non-empty active_ingredients list, got {result['active_ingredients']}"
    
    def test_get_medication_by_name_dosage_instructions_not_empty(self):
        """
        Test that dosage_instructions is not empty (required field).
        
        Arrange: Valid medication name
        Act: Call get_medication_by_name
        Assert: dosage_instructions is present and non-empty
        """
        # Arrange
        name = "Amoxicillin"
        language = None
        
        # Act
        result = get_medication_by_name(name, language)
        
        # Assert
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        assert "dosage_instructions" in result, "Result must include dosage_instructions"
        assert isinstance(result["dosage_instructions"], str), \
            f"Expected dosage_instructions to be a string, got {type(result['dosage_instructions'])}"
        assert result["dosage_instructions"].strip(), \
            f"Expected non-empty dosage_instructions, got '{result['dosage_instructions']}'"
    
    def test_get_medication_by_name_suggestions_provided_on_error(self):
        """
        Test that error result includes helpful suggestions.
        
        Arrange: Similar but incorrect medication name
        Act: Call get_medication_by_name with similar name
        Assert: Error includes suggestions list
        """
        # Arrange
        name = "Acamole"  # Similar to Acamol but incorrect
        language = None
        
        # Act
        result = get_medication_by_name(name, language)
        
        # Assert
        assert "error" in result, f"Expected error but got success: {result}"
        assert "suggestions" in result, "Error result must include suggestions"
        assert isinstance(result["suggestions"], list), \
            f"Expected suggestions to be a list, got {type(result['suggestions'])}"
        # Suggestions may be empty if no similar matches, but field must exist
    
    def test_get_medication_by_name_very_long_string(self):
        """
        Test handling of very long medication name (edge case).
        
        Arrange: Very long string as medication name
        Act: Call get_medication_by_name with very long name
        Assert: Returns error or handles gracefully
        """
        # Arrange
        name = "A" * 1000  # Very long string
        language = None
        
        # Act
        result = get_medication_by_name(name, language)
        
        # Assert
        # Should either return error or handle gracefully
        assert isinstance(result, dict), f"Expected dict result, got {type(result)}"
        # If error, should have error field; if success, should have medication_id
        assert "error" in result or "medication_id" in result, \
            f"Result should be either error or success, got {result}"
    
    def test_get_medication_by_name_special_characters(self):
        """
        Test handling of special characters in medication name (edge case).
        
        Arrange: Medication name with special characters
        Act: Call get_medication_by_name with special characters
        Assert: Handles gracefully (may return error or search)
        """
        # Arrange
        name = "Med@#$%^&*()ication"
        language = None
        
        # Act
        result = get_medication_by_name(name, language)
        
        # Assert
        assert isinstance(result, dict), f"Expected dict result, got {type(result)}"
        # Should handle gracefully without crashing
        assert "error" in result or "medication_id" in result, \
            f"Result should be either error or success, got {result}"
    
    def test_get_medication_by_name_unicode_hebrew_complex(self):
        """
        Test handling of complex Hebrew Unicode characters (edge case).
        
        Arrange: Medication name with complex Hebrew characters
        Act: Call get_medication_by_name with Hebrew Unicode
        Assert: Handles Hebrew characters correctly
        """
        # Arrange
        name = "אקמול"  # Hebrew name
        language = "he"
        
        # Act
        result = get_medication_by_name(name, language)
        
        # Assert
        # Should handle Hebrew characters correctly
        assert isinstance(result, dict), f"Expected dict result, got {type(result)}"
        if "error" not in result:
            # If found, should have Hebrew name
            assert "name_he" in result, "Result should include name_he for Hebrew search"
    
    def test_get_medication_by_name_newlines_and_tabs(self):
        """
        Test handling of newlines and tabs in medication name (edge case).
        
        Arrange: Medication name with newlines and tabs
        Act: Call get_medication_by_name with whitespace characters
        Assert: Handles or rejects appropriately
        """
        # Arrange
        name = "Acamol\n\t\r"
        language = None
        
        # Act
        result = get_medication_by_name(name, language)
        
        # Assert
        assert isinstance(result, dict), f"Expected dict result, got {type(result)}"
        # Should either strip whitespace and find, or return error
        assert "error" in result or "medication_id" in result, \
            f"Result should be either error or success, got {result}"
    
    def test_get_medication_by_name_exact_boundary_single_char(self):
        """
        Test handling of single character search (edge case - boundary).
        
        Arrange: Single character as medication name
        Act: Call get_medication_by_name with single character
        Assert: Returns error or handles gracefully
        """
        # Arrange
        name = "A"
        language = None
        
        # Act
        result = get_medication_by_name(name, language)
        
        # Assert
        assert isinstance(result, dict), f"Expected dict result, got {type(result)}"
        # Single character may or may not match, but should not crash
        assert "error" in result or "medication_id" in result, \
            f"Result should be either error or success, got {result}"
    
    def test_get_medication_by_name_multiple_whitespace(self):
        """
        Test handling of multiple whitespace characters (edge case).
        
        Arrange: Medication name with multiple spaces
        Act: Call get_medication_by_name with multiple spaces
        Assert: Strips whitespace and handles correctly
        """
        # Arrange
        name = "   Acamol   "
        language = None
        
        # Act
        result = get_medication_by_name(name, language)
        
        # Assert
        # Should strip whitespace and find medication
        assert "error" not in result, \
            f"Expected success after whitespace stripping but got error: {result.get('error', 'Unknown error')}"
        assert result["medication_id"] == "med_001", \
            f"Expected medication_id='med_001', got '{result.get('medication_id')}'"

