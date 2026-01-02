"""
Tests for tool separation of concerns and no duplication.

Purpose (Why):
Validates that each tool has a clear, unique responsibility and that there is no
duplication of functionality between tools. Ensures that get_medication_by_name
returns only basic medication information, while stock and prescription information
are provided by dedicated tools.

Implementation (What):
Tests verify that:
- get_medication_by_name does NOT return stock or prescription fields
- check_stock_availability provides detailed stock information
- check_prescription_requirement provides detailed prescription information
- Tools can be used together in multi-step flows without duplication
"""

import pytest
from app.tools.medication_tools import get_medication_by_name
from app.tools.inventory_tools import check_stock_availability
from app.tools.prescription_tools import check_prescription_requirement


class TestToolSeparationOfConcerns:
    """Test suite for tool separation of concerns."""
    
    def test_get_medication_by_name_does_not_return_stock_fields(self):
        """
        Test that get_medication_by_name does not return stock-related fields.
        
        Arrange: Valid medication name
        Act: Call get_medication_by_name
        Assert: Result does NOT contain available, quantity_in_stock, or last_restocked
        """
        # Arrange
        name = "אקמול"
        language = "he"
        
        # Act
        result = get_medication_by_name(name, language)
        
        # Assert
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        assert "available" not in result, \
            f"get_medication_by_name should NOT return 'available' field, but it was found. Use check_stock_availability instead."
        assert "quantity_in_stock" not in result, \
            f"get_medication_by_name should NOT return 'quantity_in_stock' field, but it was found. Use check_stock_availability instead."
        assert "last_restocked" not in result, \
            f"get_medication_by_name should NOT return 'last_restocked' field, but it was found. Use check_stock_availability instead."
    
    def test_get_medication_by_name_does_not_return_prescription_fields(self):
        """
        Test that get_medication_by_name does not return prescription-related fields.
        
        Arrange: Valid medication name
        Act: Call get_medication_by_name
        Assert: Result does NOT contain requires_prescription or prescription_type
        """
        # Arrange
        name = "אקמול"
        language = "he"
        
        # Act
        result = get_medication_by_name(name, language)
        
        # Assert
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        assert "requires_prescription" not in result, \
            f"get_medication_by_name should NOT return 'requires_prescription' field, but it was found. Use check_prescription_requirement instead."
        assert "prescription_type" not in result, \
            f"get_medication_by_name should NOT return 'prescription_type' field, but it was found. Use check_prescription_requirement instead."
    
    def test_get_medication_by_name_returns_only_basic_fields(self):
        """
        Test that get_medication_by_name returns only basic medication information.
        
        Arrange: Valid medication name
        Act: Call get_medication_by_name
        Assert: Result contains only expected basic fields
        """
        # Arrange
        name = "Acamol"
        language = "he"
        
        # Act
        result = get_medication_by_name(name, language)
        
        # Assert
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        
        # Expected basic fields
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
            assert field in result, \
                f"get_medication_by_name should return '{field}' field, but it's missing"
        
        # Verify no unexpected fields (excluding error-related fields)
        result_keys = set(result.keys())
        expected_keys = set(expected_fields)
        
        # Allow error-related fields if present, but not stock/prescription fields
        unexpected_fields = result_keys - expected_keys
        forbidden_fields = {"available", "quantity_in_stock", "last_restocked", 
                          "requires_prescription", "prescription_type", "sufficient_quantity"}
        
        unexpected_forbidden = unexpected_fields & forbidden_fields
        assert not unexpected_forbidden, \
            f"get_medication_by_name returned forbidden fields: {unexpected_forbidden}. These should be provided by dedicated tools."
    
    def test_check_stock_availability_returns_detailed_stock_info(self):
        """
        Test that check_stock_availability returns detailed stock information.
        
        Arrange: Valid medication_id
        Act: Call check_stock_availability
        Assert: Result contains all expected stock-related fields
        """
        # Arrange
        medication_id = "med_001"
        
        # Act
        result = check_stock_availability(medication_id)
        
        # Assert
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        
        # Expected stock fields
        expected_fields = [
            "medication_id",
            "medication_name",
            "available",
            "quantity_in_stock",
            "last_restocked",
            "sufficient_quantity",
            "requested_quantity"
        ]
        
        for field in expected_fields:
            assert field in result, \
                f"check_stock_availability should return '{field}' field, but it's missing"
    
    def test_check_prescription_requirement_returns_detailed_prescription_info(self):
        """
        Test that check_prescription_requirement returns detailed prescription information.
        
        Arrange: Valid medication_id
        Act: Call check_prescription_requirement
        Assert: Result contains all expected prescription-related fields
        """
        # Arrange
        medication_id = "med_001"
        
        # Act
        result = check_prescription_requirement(medication_id)
        
        # Assert
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        
        # Expected prescription fields
        expected_fields = [
            "medication_id",
            "medication_name",
            "requires_prescription",
            "prescription_type"
        ]
        
        for field in expected_fields:
            assert field in result, \
                f"check_prescription_requirement should return '{field}' field, but it's missing"
    
    def test_multi_step_flow_no_duplication(self):
        """
        Test that tools can be used together in multi-step flow without duplication.
        
        Arrange: Medication name
        Act: 
        1. Call get_medication_by_name to get medication_id
        2. Call check_stock_availability with medication_id
        3. Call check_prescription_requirement with medication_id
        Assert: Each tool provides unique information, no duplication
        """
        # Arrange
        name = "אקמול"
        language = "he"
        
        # Act - Step 1: Get basic medication info
        medication_result = get_medication_by_name(name, language)
        assert "error" not in medication_result, \
            f"Expected medication search to succeed, got error: {medication_result.get('error', 'Unknown error')}"
        
        medication_id = medication_result["medication_id"]
        
        # Act - Step 2: Get stock information
        stock_result = check_stock_availability(medication_id)
        assert "error" not in stock_result, \
            f"Expected stock check to succeed, got error: {stock_result.get('error', 'Unknown error')}"
        
        # Act - Step 3: Get prescription information
        prescription_result = check_prescription_requirement(medication_id)
        assert "error" not in prescription_result, \
            f"Expected prescription check to succeed, got error: {prescription_result.get('error', 'Unknown error')}"
        
        # Assert - Verify no duplication
        # medication_result should NOT have stock/prescription fields
        assert "available" not in medication_result, \
            "medication_result should not contain stock fields"
        assert "requires_prescription" not in medication_result, \
            "medication_result should not contain prescription fields"
        
        # stock_result should have stock fields but NOT prescription fields
        assert "available" in stock_result, \
            "stock_result should contain stock fields"
        assert "requires_prescription" not in stock_result, \
            "stock_result should not contain prescription fields"
        
        # prescription_result should have prescription fields but NOT stock fields
        assert "requires_prescription" in prescription_result, \
            "prescription_result should contain prescription fields"
        assert "available" not in prescription_result, \
            "prescription_result should not contain stock fields"
    
    def test_tool_medication_id_consistency(self):
        """
        Test that medication_id from get_medication_by_name can be used with other tools.
        
        Arrange: Medication name
        Act: 
        1. Get medication_id from get_medication_by_name
        2. Use same medication_id with check_stock_availability and check_prescription_requirement
        Assert: All tools work with the same medication_id
        """
        # Arrange
        name = "Acamol"
        language = "he"
        
        # Act - Get medication_id
        medication_result = get_medication_by_name(name, language)
        assert "error" not in medication_result, \
            f"Expected success but got error: {medication_result.get('error', 'Unknown error')}"
        
        medication_id = medication_result["medication_id"]
        assert medication_id, f"Expected medication_id to be present, got: {medication_id}"
        
        # Act - Use medication_id with stock tool
        stock_result = check_stock_availability(medication_id)
        assert "error" not in stock_result, \
            f"Expected stock check to succeed with medication_id '{medication_id}', got error: {stock_result.get('error', 'Unknown error')}"
        assert stock_result["medication_id"] == medication_id, \
            f"Expected stock_result.medication_id to match '{medication_id}', got '{stock_result.get('medication_id')}'"
        
        # Act - Use medication_id with prescription tool
        prescription_result = check_prescription_requirement(medication_id)
        assert "error" not in prescription_result, \
            f"Expected prescription check to succeed with medication_id '{medication_id}', got error: {prescription_result.get('error', 'Unknown error')}"
        assert prescription_result["medication_id"] == medication_id, \
            f"Expected prescription_result.medication_id to match '{medication_id}', got '{prescription_result.get('medication_id')}'"
    
    def test_separation_principle_clear_responsibilities(self):
        """
        Test that each tool has a clear, single responsibility.
        
        Arrange: Medication name
        Act: Call all three tools
        Assert: Each tool provides distinct, non-overlapping information
        """
        # Arrange
        name = "Aspirin"
        language = None
        
        # Act
        medication_result = get_medication_by_name(name, language)
        assert "error" not in medication_result, \
            f"Expected success but got error: {medication_result.get('error', 'Unknown error')}"
        
        medication_id = medication_result["medication_id"]
        stock_result = check_stock_availability(medication_id)
        prescription_result = check_prescription_requirement(medication_id)
        
        # Assert - Verify clear separation
        # get_medication_by_name: Basic info only
        basic_fields = {"medication_id", "name_he", "name_en", "active_ingredients", 
                       "dosage_forms", "dosage_instructions", "usage_instructions", "description"}
        medication_keys = set(medication_result.keys())
        assert medication_keys.issubset(basic_fields | {"error"}), \
            f"get_medication_by_name should only return basic fields, but got: {medication_keys - basic_fields}"
        
        # check_stock_availability: Stock info only
        stock_fields = {"medication_id", "medication_name", "available", "quantity_in_stock", 
                      "last_restocked", "sufficient_quantity", "requested_quantity"}
        stock_keys = set(stock_result.keys())
        assert stock_keys.issubset(stock_fields | {"error"}), \
            f"check_stock_availability should only return stock fields, but got: {stock_keys - stock_fields}"
        
        # check_prescription_requirement: Prescription info only
        prescription_fields = {"medication_id", "medication_name", "requires_prescription", "prescription_type"}
        prescription_keys = set(prescription_result.keys())
        assert prescription_keys.issubset(prescription_fields | {"error"}), \
            f"check_prescription_requirement should only return prescription fields, but got: {prescription_keys - prescription_fields}"

