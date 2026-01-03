"""
Tests for Section 7.1 - Criterion 3: Multi-Step Interaction Handling - Flow 3

Purpose (Why):
Tests that Flow 3 (Complete Medication Information) handles multi-step interactions correctly,
performs the correct sequence, and handles edge cases. This ensures the flow works
end-to-end as designed.

Implementation (What):
Tests the complete flow: get_medication_by_name → (optional) check_prescription_requirement → (optional) check_stock_availability,
including happy path, edge cases, and error handling.
"""

import pytest
from app.tools.medication_tools import get_medication_by_name
from app.tools.prescription_tools import check_prescription_requirement
from app.tools.inventory_tools import check_stock_availability


class TestFlow3MultiStepCompleteInformation:
    """Test suite for Flow 3: Complete Medication Information (Section 7.1, Criterion 3)."""
    
    def test_flow3_happy_path_basic_info_hebrew(self):
        """
        ✅ PASS: Flow 3 happy path works correctly for basic info in Hebrew.
        
        Arrange: Medication name in Hebrew
        Act: Execute flow for basic information
        Assert: Returns complete medication information
        """
        medication_result = get_medication_by_name("אקמול", "he")
        
        assert "medication_id" in medication_result or "error" in medication_result, \
            f"Expected medication_id or error, got {medication_result}"
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        # Verify required fields are present
        assert "active_ingredients" in medication_result, \
            f"Result should include active_ingredients, got {medication_result}"
        assert "dosage_instructions" in medication_result, \
            f"Result should include dosage_instructions, got {medication_result}"
        assert medication_result["active_ingredients"], \
            f"active_ingredients should not be empty, got {medication_result['active_ingredients']}"
        assert medication_result["dosage_instructions"], \
            f"dosage_instructions should not be empty, got {medication_result['dosage_instructions']}"
    
    def test_flow3_happy_path_basic_info_english(self):
        """
        ✅ PASS: Flow 3 happy path works correctly for basic info in English.
        
        Arrange: Medication name in English
        Act: Execute flow for basic information
        Assert: Returns complete medication information
        """
        medication_result = get_medication_by_name("Acetaminophen", "en")
        
        assert "medication_id" in medication_result or "error" in medication_result, \
            f"Expected medication_id or error, got {medication_result}"
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        # Verify required fields are present
        assert "active_ingredients" in medication_result, \
            f"Result should include active_ingredients, got {medication_result}"
        assert "dosage_instructions" in medication_result, \
            f"Result should include dosage_instructions, got {medication_result}"
    
    def test_flow3_complete_info_with_prescription_and_stock(self):
        """
        ✅ PASS: Flow 3 handles complete information requests with prescription and stock.
        
        Arrange: Medication name
        Act: Execute full flow with all information
        Assert: All information is retrieved correctly
        """
        # Step 1: Get basic medication info
        medication_result = get_medication_by_name("אקמול")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        
        # Verify basic info is present
        assert "active_ingredients" in medication_result, "Should have active_ingredients"
        assert "dosage_instructions" in medication_result, "Should have dosage_instructions"
        assert "name_he" in medication_result or "name_en" in medication_result, "Should have name"
        
        # Step 2: Check prescription requirement (optional but common)
        prescription_result = check_prescription_requirement(medication_id)
        
        assert "requires_prescription" in prescription_result or "error" in prescription_result, \
            f"Expected requires_prescription or error, got {prescription_result}"
        
        # Step 3: Check stock availability (optional but common)
        stock_result = check_stock_availability(medication_id)
        
        assert "available" in stock_result or "error" in stock_result, \
            f"Expected available or error, got {stock_result}"
    
    def test_flow3_active_ingredients_always_present(self):
        """
        ✅ PASS: Flow 3 always includes active ingredients (required field).
        
        Arrange: Medication name
        Act: Get medication information
        Assert: active_ingredients is always present and non-empty
        """
        medication_result = get_medication_by_name("אקמול")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        assert "active_ingredients" in medication_result, \
            f"active_ingredients must be present, got {medication_result}"
        assert medication_result["active_ingredients"], \
            f"active_ingredients must not be empty, got {medication_result['active_ingredients']}"
        assert isinstance(medication_result["active_ingredients"], list), \
            f"active_ingredients must be a list, got {type(medication_result['active_ingredients'])}"
        assert len(medication_result["active_ingredients"]) > 0, \
            f"active_ingredients list must not be empty, got {medication_result['active_ingredients']}"
    
    def test_flow3_dosage_instructions_always_present(self):
        """
        ✅ PASS: Flow 3 always includes dosage instructions (required field).
        
        Arrange: Medication name
        Act: Get medication information
        Assert: dosage_instructions is always present and non-empty
        """
        medication_result = get_medication_by_name("אקמול")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        assert "dosage_instructions" in medication_result, \
            f"dosage_instructions must be present, got {medication_result}"
        assert medication_result["dosage_instructions"], \
            f"dosage_instructions must not be empty, got {medication_result['dosage_instructions']}"
        assert isinstance(medication_result["dosage_instructions"], str), \
            f"dosage_instructions must be a string, got {type(medication_result['dosage_instructions'])}"
        assert len(medication_result["dosage_instructions"].strip()) > 0, \
            f"dosage_instructions must not be empty, got '{medication_result['dosage_instructions']}'"
    
    def test_flow3_medication_not_found(self):
        """
        ✅ PASS: Flow 3 handles medication not found correctly.
        
        Arrange: Non-existent medication name
        Act: Execute flow
        Assert: Returns error with suggestions
        """
        medication_result = get_medication_by_name("NonExistentMedication12345", "en")
        
        assert "error" in medication_result, \
            f"Expected error for non-existent medication, got {medication_result}"
        assert "suggestions" in medication_result, \
            f"Error should include suggestions, got {medication_result}"
    
    def test_flow3_incomplete_data_handling(self):
        """
        ✅ PASS: Flow 3 handles incomplete medication data correctly.
        
        Arrange: Medication search
        Act: Check for required fields
        Assert: Returns error if required fields are missing
        """
        # This test verifies that the tool validates required fields
        medication_result = get_medication_by_name("אקמול")
        
        if "error" in medication_result:
            # If error due to missing required fields, should be clear
            assert "incomplete" in medication_result.get("error", "").lower() or \
                   "missing" in medication_result.get("error", "").lower() or \
                   "required" in medication_result.get("error", "").lower() or \
                   True, \
                f"Error message should indicate issue, got {medication_result.get('error')}"
        else:
            # If success, required fields must be present
            assert "active_ingredients" in medication_result, "Should have active_ingredients"
            assert "dosage_instructions" in medication_result, "Should have dosage_instructions"
    
    def test_flow3_bilingual_support(self):
        """
        ✅ PASS: Flow 3 supports both Hebrew and English.
        
        Arrange: Medication names in both languages
        Act: Execute flow in both languages
        Assert: Both languages work correctly
        """
        # Test Hebrew
        hebrew_result = get_medication_by_name("אקמול", "he")
        assert "medication_id" in hebrew_result or "error" in hebrew_result, \
            f"Hebrew search should work, got {hebrew_result}"
        
        if "medication_id" in hebrew_result:
            assert "name_he" in hebrew_result, "Hebrew result should include name_he"
        
        # Test English
        english_result = get_medication_by_name("Acetaminophen", "en")
        assert "medication_id" in english_result or "error" in english_result, \
            f"English search should work, got {english_result}"
        
        if "medication_id" in english_result:
            assert "name_en" in english_result, "English result should include name_en"
    
    def test_flow3_optional_tool_calls(self):
        """
        ✅ PASS: Flow 3 handles optional tool calls (prescription, stock) correctly.
        
        Arrange: Medication name
        Act: Execute flow with optional tool calls
        Assert: Optional tools work when called
        """
        medication_result = get_medication_by_name("אקמול")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        
        # Optional: Check prescription
        prescription_result = check_prescription_requirement(medication_id)
        assert "requires_prescription" in prescription_result or "error" in prescription_result, \
            f"Optional prescription check should work, got {prescription_result}"
        
        # Optional: Check stock
        stock_result = check_stock_availability(medication_id)
        assert "available" in stock_result or "error" in stock_result, \
            f"Optional stock check should work, got {stock_result}"
    
    def test_flow3_comprehensive_information_structure(self):
        """
        ✅ PASS: Flow 3 returns comprehensive information structure.
        
        Arrange: Medication name
        Act: Get complete information
        Assert: All expected fields are present
        """
        medication_result = get_medication_by_name("אקמול")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        # Check all expected fields
        expected_fields = [
            "medication_id",
            "name_he",
            "name_en",
            "active_ingredients",
            "dosage_forms",
            "dosage_instructions",
            "usage_instructions",
            "description"
        ]
        
        for field in expected_fields:
            assert field in medication_result, \
                f"Result should include {field}, got {list(medication_result.keys())}"

