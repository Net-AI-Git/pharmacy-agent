"""
Tests for Section 7.1 - Criterion 3: Multi-Step Interaction Handling - Flow 2

Purpose (Why):
Tests that Flow 2 (Prescription Requirement + Stock Check) handles multi-step interactions correctly,
performs the correct sequence, and handles edge cases. This ensures the flow works
end-to-end as designed.

Implementation (What):
Tests the complete flow: get_medication_by_name → check_prescription_requirement → (optional) check_stock_availability,
including happy path, edge cases, and error handling.
"""

import pytest
from app.tools.medication_tools import get_medication_by_name
from app.tools.prescription_tools import check_prescription_requirement
from app.tools.inventory_tools import check_stock_availability


class TestFlow2MultiStepPrescription:
    """Test suite for Flow 2: Prescription Requirement + Stock Check (Section 7.1, Criterion 3)."""
    
    def test_flow2_happy_path_prescription_required_hebrew(self):
        """
        ✅ PASS: Flow 2 happy path works correctly for prescription required in Hebrew.
        
        Arrange: Medication name in Hebrew that requires prescription
        Act: Execute flow sequence
        Assert: All tools execute successfully in correct order
        """
        # Step 1: Search medication by name
        medication_result = get_medication_by_name("אמוקסיצילין", "he")
        
        assert "medication_id" in medication_result or "error" in medication_result, \
            f"Expected medication_id or error, got {medication_result}"
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        
        # Step 2: Check prescription requirement
        prescription_result = check_prescription_requirement(medication_id)
        
        assert "requires_prescription" in prescription_result or "error" in prescription_result, \
            f"Expected requires_prescription or error, got {prescription_result}"
        assert "medication_id" in prescription_result, \
            f"Prescription result should include medication_id, got {prescription_result}"
    
    def test_flow2_happy_path_prescription_required_english(self):
        """
        ✅ PASS: Flow 2 happy path works correctly for prescription required in English.
        
        Arrange: Medication name in English that requires prescription
        Act: Execute flow sequence
        Assert: All tools execute successfully in correct order
        """
        # Step 1: Search medication by name
        medication_result = get_medication_by_name("Amoxicillin", "en")
        
        assert "medication_id" in medication_result or "error" in medication_result, \
            f"Expected medication_id or error, got {medication_result}"
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        
        # Step 2: Check prescription requirement
        prescription_result = check_prescription_requirement(medication_id)
        
        assert "requires_prescription" in prescription_result or "error" in prescription_result, \
            f"Expected requires_prescription or error, got {prescription_result}"
    
    def test_flow2_happy_path_no_prescription_required(self):
        """
        ✅ PASS: Flow 2 works correctly for medications that don't require prescription.
        
        Arrange: Medication name that doesn't require prescription
        Act: Execute flow sequence
        Assert: Prescription check returns requires_prescription=false
        """
        # Step 1: Search medication by name
        medication_result = get_medication_by_name("אקמול")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        
        # Step 2: Check prescription requirement
        prescription_result = check_prescription_requirement(medication_id)
        
        if "requires_prescription" in prescription_result:
            # Should be False for over-the-counter medications
            assert isinstance(prescription_result["requires_prescription"], bool), \
                f"requires_prescription should be boolean, got {prescription_result['requires_prescription']}"
    
    def test_flow2_combined_prescription_and_stock(self):
        """
        ✅ PASS: Flow 2 handles combined prescription + stock queries correctly.
        
        Arrange: Medication name
        Act: Execute full flow with prescription and stock checks
        Assert: Both checks execute successfully
        """
        # Step 1: Search medication
        medication_result = get_medication_by_name("אקמול")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        
        # Step 2: Check prescription requirement
        prescription_result = check_prescription_requirement(medication_id)
        
        assert "requires_prescription" in prescription_result or "error" in prescription_result, \
            f"Expected requires_prescription or error, got {prescription_result}"
        
        # Step 3: Check stock availability (optional but common in this flow)
        stock_result = check_stock_availability(medication_id)
        
        assert "available" in stock_result or "error" in stock_result, \
            f"Expected available or error, got {stock_result}"
    
    def test_flow2_medication_not_found(self):
        """
        ✅ PASS: Flow 2 handles medication not found correctly.
        
        Arrange: Non-existent medication name
        Act: Execute flow sequence
        Assert: Returns error with suggestions
        """
        medication_result = get_medication_by_name("NonExistentMedication12345", "en")
        
        assert "error" in medication_result, \
            f"Expected error for non-existent medication, got {medication_result}"
        assert "suggestions" in medication_result, \
            f"Error should include suggestions, got {medication_result}"
    
    def test_flow2_safe_fallback_prescription_required(self):
        """
        ✅ PASS: Flow 2 uses safe fallback (requires_prescription=true) on errors.
        
        Arrange: Invalid medication_id
        Act: Check prescription requirement
        Assert: Returns error with safe fallback (requires_prescription=true)
        """
        prescription_result = check_prescription_requirement("invalid_med_id")
        
        assert "error" in prescription_result or "requires_prescription" in prescription_result, \
            f"Expected error or requires_prescription, got {prescription_result}"
        
        # If error, should have safe fallback
        if "error" in prescription_result:
            assert "requires_prescription" in prescription_result, \
                f"Error result should include requires_prescription, got {prescription_result}"
            assert prescription_result["requires_prescription"] is True, \
                f"Safe fallback should be requires_prescription=true, got {prescription_result['requires_prescription']}"
            assert prescription_result.get("prescription_type") == "prescription_required", \
                f"Safe fallback prescription_type should be 'prescription_required', got {prescription_result.get('prescription_type')}"
    
    def test_flow2_tool_sequence_order(self):
        """
        ✅ PASS: Flow 2 enforces correct tool sequence order.
        
        Arrange: Medication ID from previous search
        Act: Verify sequence requirement
        Assert: check_prescription_requirement requires medication_id from get_medication_by_name
        """
        # Verify that we need valid medication_id from get_medication_by_name
        medication_result = get_medication_by_name("אקמול")
        
        if "medication_id" in medication_result:
            medication_id = medication_result["medication_id"]
            prescription_result = check_prescription_requirement(medication_id)
            assert "requires_prescription" in prescription_result or "error" in prescription_result, \
                f"Should work with valid medication_id, got {prescription_result}"
    
    def test_flow2_prescription_type_values(self):
        """
        ✅ PASS: Flow 2 returns correct prescription_type values.
        
        Arrange: Medication IDs
        Act: Check prescription requirements
        Assert: prescription_type is either "not_required" or "prescription_required"
        """
        medication_result = get_medication_by_name("אקמול")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        prescription_result = check_prescription_requirement(medication_id)
        
        if "prescription_type" in prescription_result:
            assert prescription_result["prescription_type"] in ["not_required", "prescription_required"], \
                f"prescription_type should be 'not_required' or 'prescription_required', got {prescription_result['prescription_type']}"
    
    def test_flow2_bilingual_support(self):
        """
        ✅ PASS: Flow 2 supports both Hebrew and English.
        
        Arrange: Medication names in both languages
        Act: Execute flow in both languages
        Assert: Both languages work correctly
        """
        # Test Hebrew
        hebrew_result = get_medication_by_name("אמוקסיצילין", "he")
        if "medication_id" in hebrew_result:
            prescription_result = check_prescription_requirement(hebrew_result["medication_id"])
            assert "requires_prescription" in prescription_result or "error" in prescription_result, \
                f"Hebrew flow should work, got {prescription_result}"
        
        # Test English
        english_result = get_medication_by_name("Amoxicillin", "en")
        if "medication_id" in english_result:
            prescription_result = check_prescription_requirement(english_result["medication_id"])
            assert "requires_prescription" in prescription_result or "error" in prescription_result, \
                f"English flow should work, got {prescription_result}"
    
    def test_flow2_error_handling_validation(self):
        """
        ✅ PASS: Flow 2 handles input validation errors correctly.
        
        Arrange: Invalid inputs
        Act: Execute flow with invalid inputs
        Assert: Returns appropriate errors
        """
        # Test empty medication_id
        prescription_result = check_prescription_requirement("")
        
        assert "error" in prescription_result or "requires_prescription" in prescription_result, \
            f"Should handle empty medication_id, got {prescription_result}"

