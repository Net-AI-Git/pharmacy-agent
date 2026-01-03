"""
Tests for user tools.

Purpose (Why):
Validates that user tools work correctly with various inputs, handle edge cases,
and provide proper error messages with suggestions. Tests all three user tools:
get_user_by_name_or_email, get_user_prescriptions, and check_user_prescription_for_medication.

Implementation (What):
Tests the user tools with:
- Valid user names and emails
- Case-insensitive search
- Partial matches
- Non-existent users
- Empty/invalid inputs
- Prescription retrieval
- Active prescription checking
"""

import pytest
from app.tools.user_tools import (
    get_user_by_name_or_email,
    get_user_prescriptions,
    check_user_prescription_for_medication
)


class TestGetUserByNameOrEmail:
    """Test suite for get_user_by_name_or_email tool."""
    
    def test_success_by_name(self):
        """
        Test finding user by exact name.
        
        Arrange: Valid user name
        Act: Call get_user_by_name_or_email with name
        Assert: Returns user with all required fields
        """
        result = get_user_by_name_or_email("John Doe")
        
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        assert result["user_id"] == "user_001", f"Expected user_id='user_001', got '{result.get('user_id')}'"
        assert result["name"] == "John Doe", f"Expected name='John Doe', got '{result.get('name')}'"
        assert "email" in result, "Result must include email"
        assert "prescriptions" in result, "Result must include prescriptions list"
        assert isinstance(result["prescriptions"], list), "Prescriptions must be a list"
    
    def test_success_by_email(self):
        """
        Test finding user by exact email.
        
        Arrange: Valid user email
        Act: Call get_user_by_name_or_email with email
        Assert: Returns user with all required fields
        """
        result = get_user_by_name_or_email("john.doe@example.com")
        
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        assert result["user_id"] == "user_001", f"Expected user_id='user_001', got '{result.get('user_id')}'"
        assert result["email"] == "john.doe@example.com", f"Expected email='john.doe@example.com', got '{result.get('email')}'"
    
    def test_not_found_with_suggestions(self):
        """
        Test that error is returned with suggestions when user not found.
        
        Arrange: Non-existent user name
        Act: Call get_user_by_name_or_email with non-existent name
        Assert: Returns error with suggestions
        """
        result = get_user_by_name_or_email("NonExistent User")
        
        assert "error" in result, "Expected error when user not found"
        assert "searched_name_or_email" in result, "Error must include searched_name_or_email"
        assert "suggestions" in result, "Error must include suggestions"
        assert isinstance(result["suggestions"], list), "Suggestions must be a list"
    
    def test_case_insensitive_search(self):
        """
        Test that search is case-insensitive.
        
        Arrange: User name with different case
        Act: Call get_user_by_name_or_email with different case
        Assert: Returns user successfully
        """
        result = get_user_by_name_or_email("JOHN DOE")
        
        assert "error" not in result, f"Expected success with case-insensitive search but got error: {result.get('error', 'Unknown error')}"
        assert result["user_id"] == "user_001", f"Expected user_id='user_001', got '{result.get('user_id')}'"
    
    def test_partial_match(self):
        """
        Test that partial matching works.
        
        Arrange: Partial user name
        Act: Call get_user_by_name_or_email with partial name
        Assert: Returns user using partial matching
        """
        result = get_user_by_name_or_email("John")
        
        assert "error" not in result, f"Expected success with partial match but got error: {result.get('error', 'Unknown error')}"
        assert "user_id" in result, "Result must include user_id"
        assert "John" in result.get("name", ""), f"Expected name containing 'John', got {result.get('name')}"
    
    def test_empty_input(self):
        """
        Test that empty input returns error.
        
        Arrange: Empty string
        Act: Call get_user_by_name_or_email with empty string
        Assert: Returns error
        """
        result = get_user_by_name_or_email("")
        
        assert "error" in result, "Expected error for empty input"
        assert "searched_name_or_email" in result, "Error must include searched_name_or_email"


class TestGetUserPrescriptions:
    """Test suite for get_user_prescriptions tool."""
    
    def test_success_with_prescriptions(self):
        """
        Test retrieving prescriptions for user with prescriptions.
        
        Arrange: Valid user_id with prescriptions and authenticated_user_id
        Act: Call get_user_prescriptions with user_id and authenticated_user_id
        Assert: Returns user and prescriptions list
        """
        # Note: get_user_prescriptions now requires authentication
        result = get_user_prescriptions("user_001", authenticated_user_id="user_001")
        
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        assert result["user_id"] == "user_001", f"Expected user_id='user_001', got '{result.get('user_id')}'"
        assert "user_name" in result, "Result must include user_name"
        assert "prescriptions" in result, "Result must include prescriptions"
        assert isinstance(result["prescriptions"], list), "Prescriptions must be a list"
        assert len(result["prescriptions"]) > 0, "User should have at least one prescription"
        
        # Check prescription structure
        if result["prescriptions"]:
            prescription = result["prescriptions"][0]
            assert "prescription_id" in prescription, "Prescription must include prescription_id"
            assert "medication_id" in prescription, "Prescription must include medication_id"
            assert "medication_name_he" in prescription, "Prescription must include medication_name_he"
            assert "medication_name_en" in prescription, "Prescription must include medication_name_en"
    
    def test_success_no_prescriptions(self):
        """
        Test retrieving prescriptions for user without prescriptions.
        
        Arrange: Valid user_id without prescriptions and authenticated_user_id
        Act: Call get_user_prescriptions with user_id and authenticated_user_id
        Assert: Returns user with empty prescriptions list (not an error)
        """
        # Note: get_user_prescriptions now requires authentication
        result = get_user_prescriptions("user_006", authenticated_user_id="user_006")
        
        assert "error" not in result, f"Expected success (empty list) but got error: {result.get('error', 'Unknown error')}"
        assert result["user_id"] == "user_006", f"Expected user_id='user_006', got '{result.get('user_id')}'"
        assert "prescriptions" in result, "Result must include prescriptions"
        assert isinstance(result["prescriptions"], list), "Prescriptions must be a list"
        assert len(result["prescriptions"]) == 0, "User should have no prescriptions"
    
    def test_user_not_found(self):
        """
        Test that error is returned when user not found.
        
        Arrange: Non-existent user_id
        Act: Call get_user_prescriptions with non-existent user_id
        Assert: Returns error
        """
        result = get_user_prescriptions("user_nonexistent")
        
        assert "error" in result, "Expected error when user not found"
        assert "success" in result, "Error must include success field"
        assert result["success"] is False, "Success should be False for error"


class TestCheckUserPrescriptionForMedication:
    """Test suite for check_user_prescription_for_medication tool."""
    
    def test_has_active_prescription(self):
        """
        Test checking for active prescription when user has one.
        
        Arrange: Valid user_id and medication_id with active prescription and authenticated_user_id
        Act: Call check_user_prescription_for_medication with authenticated_user_id
        Assert: Returns has_active_prescription=true with prescription details
        """
        # Note: check_user_prescription_for_medication now requires authentication
        result = check_user_prescription_for_medication("user_001", "med_003", authenticated_user_id="user_001")
        
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        assert "has_active_prescription" in result, "Result must include has_active_prescription"
        assert result["has_active_prescription"] is True, "User should have active prescription"
        assert "prescription_details" in result, "Result must include prescription_details"
        assert result["prescription_details"] is not None, "Prescription details should not be None when active prescription exists"
        
        if result["prescription_details"]:
            details = result["prescription_details"]
            assert "prescription_id" in details, "Prescription details must include prescription_id"
            assert "medication_id" in details, "Prescription details must include medication_id"
            assert details["status"] == "active", "Prescription status should be 'active'"
    
    def test_no_active_prescription(self):
        """
        Test checking for active prescription when user doesn't have one.
        
        Arrange: Valid user_id and medication_id without active prescription and authenticated_user_id
        Act: Call check_user_prescription_for_medication with authenticated_user_id
        Assert: Returns has_active_prescription=false (not an error)
        """
        # Note: check_user_prescription_for_medication now requires authentication
        result = check_user_prescription_for_medication("user_006", "med_001", authenticated_user_id="user_006")
        
        assert "error" not in result, f"Expected success (no active prescription) but got error: {result.get('error', 'Unknown error')}"
        assert "has_active_prescription" in result, "Result must include has_active_prescription"
        assert result["has_active_prescription"] is False, "User should not have active prescription"
        assert "prescription_details" in result, "Result must include prescription_details"
        assert result["prescription_details"] is None, "Prescription details should be None when no active prescription"
    
    def test_user_not_found(self):
        """
        Test that error is returned when user not found.
        
        Arrange: Non-existent user_id
        Act: Call check_user_prescription_for_medication with non-existent user_id
        Assert: Returns error
        """
        result = check_user_prescription_for_medication("user_nonexistent", "med_001")
        
        assert "error" in result, "Expected error when user not found"
        assert "success" in result, "Error must include success field"
        assert result["success"] is False, "Success should be False for error"
    
    def test_medication_not_found(self):
        """
        Test that error is returned when medication not found.
        
        Arrange: Valid user_id and non-existent medication_id
        Act: Call check_user_prescription_for_medication with non-existent medication_id
        Assert: Returns error
        """
        result = check_user_prescription_for_medication("user_001", "med_nonexistent")
        
        assert "error" in result, "Expected error when medication not found"
        assert "success" in result, "Error must include success field"
        assert result["success"] is False, "Success should be False for error"
    
    def test_empty_user_id(self):
        """
        Test that empty user_id returns error.
        
        Arrange: Empty user_id
        Act: Call check_user_prescription_for_medication with empty user_id
        Assert: Returns error
        """
        result = check_user_prescription_for_medication("", "med_001")
        
        assert "error" in result, "Expected error for empty user_id"
        assert "success" in result, "Error must include success field"
    
    def test_empty_medication_id(self):
        """
        Test that empty medication_id returns error.
        
        Arrange: Empty medication_id
        Act: Call check_user_prescription_for_medication with empty medication_id
        Assert: Returns error
        """
        result = check_user_prescription_for_medication("user_001", "")
        
        assert "error" in result, "Expected error for empty medication_id"
        assert "success" in result, "Error must include success field"

