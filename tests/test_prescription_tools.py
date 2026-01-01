"""
Tests for Task 3.3: prescription_tools.py

Purpose (Why):
Validates that prescription requirement check tool works correctly with various inputs,
handles edge cases, and provides proper error messages with safe fallback values.

Implementation (What):
Tests the check_prescription_requirement function with:
- Medications that require prescription
- Medications that don't require prescription
- Non-existent medications
- Empty/invalid inputs
- Safe fallback behavior (requires_prescription=True)
"""

import pytest
from app.tools.prescription_tools import (
    check_prescription_requirement,
    PrescriptionCheckInput,
    PrescriptionCheckResult,
    PrescriptionCheckError
)


class TestPrescriptionTools:
    """Test suite for prescription tools."""
    
    def test_check_prescription_requirement_no_prescription_required(self):
        """
        Test checking prescription for medication that doesn't require prescription.
        
        Arrange: Medication ID for OTC medication
        Act: Call check_prescription_requirement
        Assert: Returns requires_prescription=False
        """
        # Arrange
        medication_id = "med_001"  # Acamol - requires_prescription=False
        
        # Act
        result = check_prescription_requirement(medication_id)
        
        # Assert
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        assert result["medication_id"] == medication_id, \
            f"Expected medication_id='{medication_id}', got '{result.get('medication_id')}'"
        assert result["requires_prescription"] is False, \
            f"Expected requires_prescription=False, got {result.get('requires_prescription')}"
        assert result["prescription_type"] == "not_required", \
            f"Expected prescription_type='not_required', got '{result.get('prescription_type')}'"
    
    def test_check_prescription_requirement_prescription_required(self):
        """
        Test checking prescription for medication that requires prescription.
        
        Arrange: Medication ID for prescription medication
        Act: Call check_prescription_requirement
        Assert: Returns requires_prescription=True
        """
        # Arrange
        medication_id = "med_003"  # Amoxicillin - requires_prescription=True
        
        # Act
        result = check_prescription_requirement(medication_id)
        
        # Assert
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        assert result["medication_id"] == medication_id, \
            f"Expected medication_id='{medication_id}', got '{result.get('medication_id')}'"
        assert result["requires_prescription"] is True, \
            f"Expected requires_prescription=True, got {result.get('requires_prescription')}"
        assert result["prescription_type"] == "prescription_required", \
            f"Expected prescription_type='prescription_required', got '{result.get('prescription_type')}'"
    
    def test_check_prescription_requirement_medication_not_found(self):
        """
        Test error handling when medication ID is not found.
        
        Arrange: Non-existent medication ID
        Act: Call check_prescription_requirement with invalid ID
        Assert: Returns error with safe fallback (requires_prescription=True)
        """
        # Arrange
        medication_id = "med_999"
        
        # Act
        result = check_prescription_requirement(medication_id)
        
        # Assert
        assert "error" in result, f"Expected error but got success: {result}"
        assert result["error"], f"Expected non-empty error message, got '{result.get('error')}'"
        assert result["medication_id"] == medication_id, \
            f"Expected medication_id='{medication_id}', got '{result.get('medication_id')}'"
        assert result["requires_prescription"] is True, \
            f"Expected requires_prescription=True (safe fallback), got {result.get('requires_prescription')}"
        assert result["prescription_type"] == "prescription_required", \
            f"Expected prescription_type='prescription_required' (safe fallback), got '{result.get('prescription_type')}'"
    
    def test_check_prescription_requirement_empty_medication_id(self):
        """
        Test validation with empty medication ID.
        
        Arrange: Empty string as medication ID
        Act: Call check_prescription_requirement with empty ID
        Assert: Returns error with safe fallback
        """
        # Arrange
        medication_id = ""
        
        # Act
        result = check_prescription_requirement(medication_id)
        
        # Assert
        assert "error" in result, f"Expected error for empty ID but got success: {result}"
        assert "cannot be empty" in result["error"].lower() or "empty" in result["error"].lower(), \
            f"Expected error message about empty ID, got '{result.get('error')}'"
        assert result["requires_prescription"] is True, \
            f"Expected requires_prescription=True (safe fallback), got {result.get('requires_prescription')}"
        assert result["prescription_type"] == "prescription_required", \
            f"Expected prescription_type='prescription_required' (safe fallback), got '{result.get('prescription_type')}'"
    
    def test_check_prescription_requirement_whitespace_medication_id(self):
        """
        Test validation with whitespace-only medication ID.
        
        Arrange: String with only whitespace
        Act: Call check_prescription_requirement with whitespace
        Assert: Returns error with safe fallback
        """
        # Arrange
        medication_id = "   "
        
        # Act
        result = check_prescription_requirement(medication_id)
        
        # Assert
        assert "error" in result, f"Expected error for whitespace-only ID but got success: {result}"
        assert result["requires_prescription"] is True, \
            f"Expected requires_prescription=True (safe fallback), got {result.get('requires_prescription')}"
        assert result["prescription_type"] == "prescription_required", \
            f"Expected prescription_type='prescription_required' (safe fallback), got '{result.get('prescription_type')}'"
    
    def test_check_prescription_requirement_result_contains_all_fields(self):
        """
        Test that successful result contains all required fields.
        
        Arrange: Valid medication ID
        Act: Call check_prescription_requirement
        Assert: Result contains all expected fields
        """
        # Arrange
        medication_id = "med_002"
        
        # Act
        result = check_prescription_requirement(medication_id)
        
        # Assert
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        required_fields = [
            "medication_id", "medication_name", "requires_prescription", "prescription_type"
        ]
        for field in required_fields:
            assert field in result, f"Result must include field '{field}', but it's missing"
    
    def test_check_prescription_requirement_prescription_type_mapping(self):
        """
        Test that prescription_type correctly maps to requires_prescription.
        
        Arrange: Medications with different prescription requirements
        Act: Call check_prescription_requirement for each
        Assert: prescription_type matches requires_prescription value
        """
        # Arrange & Act - Test OTC medication
        result_otc = check_prescription_requirement("med_001")
        
        # Assert - OTC
        assert result_otc["requires_prescription"] is False, \
            f"Expected requires_prescription=False for OTC, got {result_otc.get('requires_prescription')}"
        assert result_otc["prescription_type"] == "not_required", \
            f"Expected prescription_type='not_required' for OTC, got '{result_otc.get('prescription_type')}'"
        
        # Arrange & Act - Test prescription medication
        result_rx = check_prescription_requirement("med_003")
        
        # Assert - Prescription required
        assert result_rx["requires_prescription"] is True, \
            f"Expected requires_prescription=True for RX, got {result_rx.get('requires_prescription')}"
        assert result_rx["prescription_type"] == "prescription_required", \
            f"Expected prescription_type='prescription_required' for RX, got '{result_rx.get('prescription_type')}'"
    
    def test_check_prescription_requirement_multiple_otc_medications(self):
        """
        Test checking prescription for multiple OTC medications.
        
        Arrange: Multiple OTC medication IDs
        Act: Call check_prescription_requirement for each
        Assert: All return requires_prescription=False
        """
        # Arrange
        otc_medication_ids = ["med_001", "med_002", "med_004"]  # Acamol, Aspirin, Ibuprofen
        
        # Act & Assert
        for medication_id in otc_medication_ids:
            result = check_prescription_requirement(medication_id)
            assert "error" not in result, \
                f"Expected success for {medication_id} but got error: {result.get('error', 'Unknown error')}"
            assert result["requires_prescription"] is False, \
                f"Expected requires_prescription=False for {medication_id}, got {result.get('requires_prescription')}"
    
    def test_check_prescription_requirement_multiple_rx_medications(self):
        """
        Test checking prescription for multiple prescription medications.
        
        Arrange: Multiple prescription medication IDs
        Act: Call check_prescription_requirement for each
        Assert: All return requires_prescription=True
        """
        # Arrange
        rx_medication_ids = ["med_003", "med_005"]  # Amoxicillin, Metformin
        
        # Act & Assert
        for medication_id in rx_medication_ids:
            result = check_prescription_requirement(medication_id)
            assert "error" not in result, \
                f"Expected success for {medication_id} but got error: {result.get('error', 'Unknown error')}"
            assert result["requires_prescription"] is True, \
                f"Expected requires_prescription=True for {medication_id}, got {result.get('requires_prescription')}"
    
    def test_check_prescription_requirement_safe_fallback_on_error(self):
        """
        Test that errors return safe fallback values (requires_prescription=True).
        
        Arrange: Invalid medication ID
        Act: Call check_prescription_requirement
        Assert: Error result has requires_prescription=True as safe fallback
        """
        # Arrange
        medication_id = "invalid_id_123"
        
        # Act
        result = check_prescription_requirement(medication_id)
        
        # Assert
        assert "error" in result, f"Expected error but got success: {result}"
        assert result["requires_prescription"] is True, \
            f"Expected requires_prescription=True (safe fallback), got {result.get('requires_prescription')}"
        assert result["prescription_type"] == "prescription_required", \
            f"Expected prescription_type='prescription_required' (safe fallback), got '{result.get('prescription_type')}'"
    
    def test_check_prescription_requirement_special_characters_in_id(self):
        """
        Test handling of special characters in medication ID (edge case).
        
        Arrange: Medication ID with special characters
        Act: Call check_prescription_requirement with special characters
        Assert: Returns error with safe fallback
        """
        # Arrange
        medication_id = "med_@#$%^&*()"
        
        # Act
        result = check_prescription_requirement(medication_id)
        
        # Assert
        assert "error" in result, f"Expected error for special characters but got success: {result}"
        assert result["requires_prescription"] is True, \
            f"Expected requires_prescription=True (safe fallback), got {result.get('requires_prescription')}"
    
    def test_check_prescription_requirement_very_long_medication_id(self):
        """
        Test handling of very long medication ID (edge case).
        
        Arrange: Very long medication ID string
        Act: Call check_prescription_requirement with very long ID
        Assert: Returns error with safe fallback
        """
        # Arrange
        medication_id = "med_" + "x" * 1000
        
        # Act
        result = check_prescription_requirement(medication_id)
        
        # Assert
        assert "error" in result, f"Expected error for very long ID but got success: {result}"
        assert result["requires_prescription"] is True, \
            f"Expected requires_prescription=True (safe fallback), got {result.get('requires_prescription')}"
    
    def test_check_prescription_requirement_newlines_and_tabs(self):
        """
        Test handling of newlines and tabs in medication ID (edge case).
        
        Arrange: Medication ID with newlines and tabs
        Act: Call check_prescription_requirement
        Assert: Handles or rejects appropriately
        """
        # Arrange
        medication_id = "med_001\n\t\r"
        
        # Act
        result = check_prescription_requirement(medication_id)
        
        # Assert
        # Should either strip whitespace and find, or return error
        assert isinstance(result, dict), f"Expected dict result, got {type(result)}"
        if "error" not in result:
            # If found, should have correct medication_id
            assert result["medication_id"] == "med_001", \
                f"Expected medication_id='med_001' after stripping, got '{result.get('medication_id')}'"
    
    def test_check_prescription_requirement_multiple_whitespace(self):
        """
        Test handling of multiple whitespace in medication ID (edge case).
        
        Arrange: Medication ID with multiple spaces
        Act: Call check_prescription_requirement
        Assert: Strips whitespace and handles correctly
        """
        # Arrange
        medication_id = "   med_001   "
        
        # Act
        result = check_prescription_requirement(medication_id)
        
        # Assert
        # Should strip whitespace and find medication
        assert "error" not in result, \
            f"Expected success after whitespace stripping but got error: {result.get('error', 'Unknown error')}"
        assert result["medication_id"] == "med_001", \
            f"Expected medication_id='med_001', got '{result.get('medication_id')}'"

