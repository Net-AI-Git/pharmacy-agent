"""
Tests for user tools authentication fixes.

Purpose (Why):
Validates that user tools correctly use authenticated_user_id when provided,
ensuring that authenticated users can access their own data without errors.
This tests the critical fix where authenticated_user_id takes precedence over
user_id parameter.

Implementation (What):
Tests the authentication fixes in:
- get_user_prescriptions: Should use authenticated_user_id if provided
- check_user_prescription_for_medication: Should use authenticated_user_id if provided
"""

import pytest
from app.tools.user_tools import (
    get_user_prescriptions,
    check_user_prescription_for_medication
)


class TestGetUserPrescriptionsAuthentication:
    """Test suite for get_user_prescriptions authentication fix."""
    
    def test_uses_authenticated_user_id_when_provided(self):
        """
        Test that authenticated_user_id must match user_id parameter for security.
        
        Arrange: authenticated_user_id provided, matching user_id in parameter
        Act: Call get_user_prescriptions with both
        Assert: Succeeds when they match
        """
        # Arrange
        authenticated_user_id = "user_001"
        user_id_param = "user_001"  # Must match authenticated_user_id
        
        # Act
        result = get_user_prescriptions(
            user_id=user_id_param,
            authenticated_user_id=authenticated_user_id
        )
        
        # Assert
        assert "error" not in result, \
            f"Expected success when user_id matches authenticated_user_id, but got error: {result.get('error', 'Unknown error')}"
        assert result["user_id"] == authenticated_user_id, \
            f"Expected user_id='{authenticated_user_id}', got '{result.get('user_id')}'"
    
    def test_uses_authenticated_user_id_ignores_parameter(self):
        """
        Test that user_id parameter must match authenticated_user_id for security.
        
        Arrange: authenticated_user_id provided, user_id parameter with different value
        Act: Call get_user_prescriptions
        Assert: Access denied when they don't match
        """
        # Arrange
        authenticated_user_id = "user_001"
        user_id_param = "user_999"  # Different from authenticated_user_id
        
        # Act
        result = get_user_prescriptions(
            user_id=user_id_param,
            authenticated_user_id=authenticated_user_id
        )
        
        # Assert
        assert "error" in result, \
            f"Expected access denied when user_id doesn't match authenticated_user_id, but got success"
        assert "Access denied" in result["error"], \
            f"Expected access denied error, got: {result.get('error', 'Unknown error')}"
    
    def test_requires_authentication_when_no_authenticated_user_id(self):
        """
        Test that authentication is required when authenticated_user_id is None.
        
        Arrange: No authenticated_user_id provided
        Act: Call get_user_prescriptions
        Assert: Returns authentication error
        """
        # Arrange
        user_id = "user_001"
        
        # Act
        result = get_user_prescriptions(
            user_id=user_id,
            authenticated_user_id=None
        )
        
        # Assert
        assert "error" in result, "Expected error when authenticated_user_id is None"
        assert "Authentication required" in result["error"], \
            f"Expected authentication error, got: {result.get('error', 'Unknown error')}"
        assert result.get("success") is False, "Expected success=False for authentication error"
    
    def test_authenticated_user_id_must_match_for_security(self):
        """
        Test that authenticated_user_id must match user_id for security.
        
        Arrange: authenticated_user_id different from user_id
        Act: Call get_user_prescriptions
        Assert: Access denied when they don't match
        """
        # Arrange
        authenticated_user_id = "user_001"
        user_id_param = "user_002"  # Different from authenticated_user_id
        
        # Act
        result = get_user_prescriptions(
            user_id=user_id_param,
            authenticated_user_id=authenticated_user_id
        )
        
        # Assert - Access should be denied when user_id doesn't match authenticated_user_id
        assert "error" in result, \
            f"Expected access denied when user_id doesn't match authenticated_user_id, but got success"
        assert "Access denied" in result["error"], \
            f"Expected access denied error, got: {result.get('error', 'Unknown error')}"


class TestCheckUserPrescriptionForMedicationAuthentication:
    """Test suite for check_user_prescription_for_medication authentication fix."""
    
    def test_uses_authenticated_user_id_when_provided(self):
        """
        Test that authenticated_user_id must match user_id parameter for security.
        
        Arrange: authenticated_user_id provided, matching user_id in parameter
        Act: Call check_user_prescription_for_medication with both
        Assert: Succeeds when they match
        """
        # Arrange
        authenticated_user_id = "user_001"
        user_id_param = "user_001"  # Must match authenticated_user_id
        medication_id = "med_001"
        
        # Act
        result = check_user_prescription_for_medication(
            user_id=user_id_param,
            medication_id=medication_id,
            authenticated_user_id=authenticated_user_id
        )
        
        # Assert
        # Should succeed when user_id matches authenticated_user_id
        assert "error" not in result, \
            f"Expected success when user_id matches authenticated_user_id, but got error: {result.get('error', 'Unknown error')}"
        assert "has_active_prescription" in result, \
            "Expected has_active_prescription field in result"
    
    def test_uses_authenticated_user_id_ignores_parameter(self):
        """
        Test that user_id parameter must match authenticated_user_id for security.
        
        Arrange: authenticated_user_id provided, user_id parameter with different value
        Act: Call check_user_prescription_for_medication
        Assert: Access denied when they don't match
        """
        # Arrange
        authenticated_user_id = "user_001"
        user_id_param = "user_999"  # Different from authenticated_user_id
        medication_id = "med_001"
        
        # Act
        result = check_user_prescription_for_medication(
            user_id=user_id_param,
            medication_id=medication_id,
            authenticated_user_id=authenticated_user_id
        )
        
        # Assert
        # Should deny access when user_id doesn't match authenticated_user_id
        assert "error" in result, \
            f"Expected access denied when user_id doesn't match authenticated_user_id, but got success"
        assert "Access denied" in result["error"], \
            f"Expected access denied error, got: {result.get('error', 'Unknown error')}"
    
    def test_requires_authentication_when_no_authenticated_user_id(self):
        """
        Test that authentication is required when authenticated_user_id is None.
        
        Arrange: No authenticated_user_id provided
        Act: Call check_user_prescription_for_medication
        Assert: Returns authentication error
        """
        # Arrange
        user_id = "user_001"
        medication_id = "med_001"
        
        # Act
        result = check_user_prescription_for_medication(
            user_id=user_id,
            medication_id=medication_id,
            authenticated_user_id=None
        )
        
        # Assert
        assert "error" in result, "Expected error when authenticated_user_id is None"
        assert "Authentication required" in result["error"], \
            f"Expected authentication error, got: {result.get('error', 'Unknown error')}"
        assert result.get("success") is False, "Expected success=False for authentication error"
    
    def test_authenticated_user_id_with_valid_medication(self):
        """
        Test that authenticated_user_id works with valid medication check when user_id matches.
        
        Arrange: authenticated_user_id and valid medication_id, matching user_id
        Act: Call check_user_prescription_for_medication
        Assert: Returns prescription check result (may be has_active_prescription=false)
        """
        # Arrange
        authenticated_user_id = "user_001"
        user_id_param = "user_001"  # Must match authenticated_user_id
        medication_id = "med_001"
        
        # Act
        result = check_user_prescription_for_medication(
            user_id=user_id_param,
            medication_id=medication_id,
            authenticated_user_id=authenticated_user_id
        )
        
        # Assert
        assert "error" not in result, \
            f"Expected prescription check result, but got error: {result.get('error', 'Unknown error')}"
        assert "has_active_prescription" in result, \
            "Expected has_active_prescription field in result"
        assert isinstance(result["has_active_prescription"], bool), \
            "has_active_prescription must be a boolean"

