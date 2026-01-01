"""
Tests for Task 3.2: inventory_tools.py

Purpose (Why):
Validates that stock availability check tool works correctly with various inputs,
handles edge cases, and provides proper error messages with safe fallback values.

Implementation (What):
Tests the check_stock_availability function with:
- Valid medication IDs
- Quantity checks
- Non-existent medications
- Empty/invalid inputs
- Safe fallback behavior
"""

import pytest
from app.tools.inventory_tools import (
    check_stock_availability,
    StockCheckInput,
    StockCheckResult,
    StockCheckError
)


class TestInventoryTools:
    """Test suite for inventory tools."""
    
    def test_check_stock_availability_valid_medication_id(self):
        """
        Test checking stock for valid medication ID.
        
        Arrange: Valid medication ID
        Act: Call check_stock_availability with medication ID
        Assert: Returns stock information with all required fields
        """
        # Arrange
        medication_id = "med_001"
        quantity = None
        
        # Act
        result = check_stock_availability(medication_id, quantity)
        
        # Assert
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        assert result["medication_id"] == medication_id, \
            f"Expected medication_id='{medication_id}', got '{result.get('medication_id')}'"
        assert "available" in result, "Result must include available field"
        assert isinstance(result["available"], bool), \
            f"Expected available to be bool, got {type(result['available'])}"
        assert "quantity_in_stock" in result, "Result must include quantity_in_stock field"
        assert isinstance(result["quantity_in_stock"], int), \
            f"Expected quantity_in_stock to be int, got {type(result['quantity_in_stock'])}"
        assert "last_restocked" in result, "Result must include last_restocked field"
    
    def test_check_stock_availability_with_quantity_sufficient(self):
        """
        Test checking stock with quantity when sufficient stock exists.
        
        Arrange: Valid medication ID and quantity less than stock
        Act: Call check_stock_availability with quantity
        Assert: Returns sufficient_quantity=True
        """
        # Arrange
        medication_id = "med_001"  # Has 150 in stock
        quantity = 10
        
        # Act
        result = check_stock_availability(medication_id, quantity)
        
        # Assert
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        assert "sufficient_quantity" in result, "Result must include sufficient_quantity field"
        assert result["sufficient_quantity"] is True, \
            f"Expected sufficient_quantity=True for quantity={quantity}, got {result.get('sufficient_quantity')}"
        assert result["requested_quantity"] == quantity, \
            f"Expected requested_quantity={quantity}, got {result.get('requested_quantity')}"
    
    def test_check_stock_availability_with_quantity_insufficient(self):
        """
        Test checking stock with quantity when insufficient stock exists.
        
        Arrange: Valid medication ID and quantity greater than stock
        Act: Call check_stock_availability with large quantity
        Assert: Returns sufficient_quantity=False
        """
        # Arrange
        medication_id = "med_001"  # Has 150 in stock
        quantity = 200  # More than available
        
        # Act
        result = check_stock_availability(medication_id, quantity)
        
        # Assert
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        assert "sufficient_quantity" in result, "Result must include sufficient_quantity field"
        assert result["sufficient_quantity"] is False, \
            f"Expected sufficient_quantity=False for quantity={quantity}, got {result.get('sufficient_quantity')}"
    
    def test_check_stock_availability_medication_not_found(self):
        """
        Test error handling when medication ID is not found.
        
        Arrange: Non-existent medication ID
        Act: Call check_stock_availability with invalid ID
        Assert: Returns error with available=False (safe fallback)
        """
        # Arrange
        medication_id = "med_999"
        quantity = None
        
        # Act
        result = check_stock_availability(medication_id, quantity)
        
        # Assert
        assert "error" in result, f"Expected error but got success: {result}"
        assert result["error"], f"Expected non-empty error message, got '{result.get('error')}'"
        assert result["medication_id"] == medication_id, \
            f"Expected medication_id='{medication_id}', got '{result.get('medication_id')}'"
        assert result["available"] is False, \
            f"Expected available=False (safe fallback), got {result.get('available')}"
    
    def test_check_stock_availability_empty_medication_id(self):
        """
        Test validation with empty medication ID.
        
        Arrange: Empty string as medication ID
        Act: Call check_stock_availability with empty ID
        Assert: Returns error for empty input
        """
        # Arrange
        medication_id = ""
        quantity = None
        
        # Act
        result = check_stock_availability(medication_id, quantity)
        
        # Assert
        assert "error" in result, f"Expected error for empty ID but got success: {result}"
        assert "cannot be empty" in result["error"].lower() or "empty" in result["error"].lower(), \
            f"Expected error message about empty ID, got '{result.get('error')}'"
        assert result["available"] is False, \
            f"Expected available=False (safe fallback), got {result.get('available')}"
    
    def test_check_stock_availability_whitespace_medication_id(self):
        """
        Test validation with whitespace-only medication ID.
        
        Arrange: String with only whitespace
        Act: Call check_stock_availability with whitespace
        Assert: Returns error for invalid input
        """
        # Arrange
        medication_id = "   "
        quantity = None
        
        # Act
        result = check_stock_availability(medication_id, quantity)
        
        # Assert
        assert "error" in result, f"Expected error for whitespace-only ID but got success: {result}"
        assert result["available"] is False, \
            f"Expected available=False (safe fallback), got {result.get('available')}"
    
    def test_check_stock_availability_negative_quantity(self):
        """
        Test validation with negative quantity.
        
        Arrange: Valid medication ID with negative quantity
        Act: Call check_stock_availability with negative quantity
        Assert: Returns error for invalid quantity
        """
        # Arrange
        medication_id = "med_001"
        quantity = -5
        
        # Act
        result = check_stock_availability(medication_id, quantity)
        
        # Assert
        assert "error" in result, f"Expected error for negative quantity but got success: {result}"
        assert "negative" in result["error"].lower() or "cannot" in result["error"].lower(), \
            f"Expected error message about negative quantity, got '{result.get('error')}'"
        assert result["available"] is False, \
            f"Expected available=False (safe fallback), got {result.get('available')}"
    
    def test_check_stock_availability_zero_quantity(self):
        """
        Test checking stock with zero quantity (edge case).
        
        Arrange: Valid medication ID with quantity=0
        Act: Call check_stock_availability with zero quantity
        Assert: Returns success with sufficient_quantity=True (0 is always sufficient)
        """
        # Arrange
        medication_id = "med_001"
        quantity = 0
        
        # Act
        result = check_stock_availability(medication_id, quantity)
        
        # Assert
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        assert result["sufficient_quantity"] is True, \
            f"Expected sufficient_quantity=True for quantity=0, got {result.get('sufficient_quantity')}"
    
    def test_check_stock_availability_result_contains_all_fields(self):
        """
        Test that successful result contains all required fields.
        
        Arrange: Valid medication ID
        Act: Call check_stock_availability
        Assert: Result contains all expected fields
        """
        # Arrange
        medication_id = "med_002"
        quantity = None
        
        # Act
        result = check_stock_availability(medication_id, quantity)
        
        # Assert
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        required_fields = [
            "medication_id", "medication_name", "available",
            "quantity_in_stock", "last_restocked", "sufficient_quantity", "requested_quantity"
        ]
        for field in required_fields:
            assert field in result, f"Result must include field '{field}', but it's missing"
    
    def test_check_stock_availability_unavailable_medication(self):
        """
        Test checking stock for medication that is out of stock.
        
        Arrange: Medication ID for out-of-stock medication
        Act: Call check_stock_availability
        Assert: Returns available=False
        """
        # Arrange
        medication_id = "med_005"  # Metformin - available=False, quantity_in_stock=0
        quantity = None
        
        # Act
        result = check_stock_availability(medication_id, quantity)
        
        # Assert
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        assert result["available"] is False, \
            f"Expected available=False for out-of-stock medication, got {result.get('available')}"
        assert result["quantity_in_stock"] == 0, \
            f"Expected quantity_in_stock=0, got {result.get('quantity_in_stock')}"
    
    def test_check_stock_availability_fallback_on_error(self):
        """
        Test that errors return safe fallback values (available=False).
        
        Arrange: Invalid medication ID
        Act: Call check_stock_availability
        Assert: Error result has available=False as safe fallback
        """
        # Arrange
        medication_id = "invalid_id_123"
        quantity = None
        
        # Act
        result = check_stock_availability(medication_id, quantity)
        
        # Assert
        assert "error" in result, f"Expected error but got success: {result}"
        assert result["available"] is False, \
            f"Expected available=False (safe fallback), got {result.get('available')}"
    
    def test_check_stock_availability_very_large_quantity(self):
        """
        Test handling of very large quantity value (edge case - boundary).
        
        Arrange: Valid medication ID with very large quantity
        Act: Call check_stock_availability with very large quantity
        Assert: Handles large number correctly
        """
        # Arrange
        medication_id = "med_001"  # Has 150 in stock
        quantity = 999999999  # Very large number
        
        # Act
        result = check_stock_availability(medication_id, quantity)
        
        # Assert
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        assert "sufficient_quantity" in result, "Result must include sufficient_quantity field"
        assert result["sufficient_quantity"] is False, \
            f"Expected sufficient_quantity=False for very large quantity, got {result.get('sufficient_quantity')}"
    
    def test_check_stock_availability_exact_stock_boundary(self):
        """
        Test checking stock with quantity exactly equal to stock (edge case - boundary).
        
        Arrange: Valid medication ID with quantity equal to stock
        Act: Call check_stock_availability with exact stock quantity
        Assert: Returns sufficient_quantity=True (>= check)
        """
        # Arrange
        medication_id = "med_001"  # Has 150 in stock
        quantity = 150  # Exactly equal to stock
        
        # Act
        result = check_stock_availability(medication_id, quantity)
        
        # Assert
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        assert result["sufficient_quantity"] is True, \
            f"Expected sufficient_quantity=True for quantity equal to stock, got {result.get('sufficient_quantity')}"
    
    def test_check_stock_availability_one_less_than_stock(self):
        """
        Test checking stock with quantity one less than stock (edge case - boundary).
        
        Arrange: Valid medication ID with quantity = stock - 1
        Act: Call check_stock_availability
        Assert: Returns sufficient_quantity=True
        """
        # Arrange
        medication_id = "med_001"  # Has 150 in stock
        quantity = 149  # One less than stock
        
        # Act
        result = check_stock_availability(medication_id, quantity)
        
        # Assert
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        assert result["sufficient_quantity"] is True, \
            f"Expected sufficient_quantity=True for quantity < stock, got {result.get('sufficient_quantity')}"
    
    def test_check_stock_availability_one_more_than_stock(self):
        """
        Test checking stock with quantity one more than stock (edge case - boundary).
        
        Arrange: Valid medication ID with quantity = stock + 1
        Act: Call check_stock_availability
        Assert: Returns sufficient_quantity=False
        """
        # Arrange
        medication_id = "med_001"  # Has 150 in stock
        quantity = 151  # One more than stock
        
        # Act
        result = check_stock_availability(medication_id, quantity)
        
        # Assert
        assert "error" not in result, f"Expected success but got error: {result.get('error', 'Unknown error')}"
        assert result["sufficient_quantity"] is False, \
            f"Expected sufficient_quantity=False for quantity > stock, got {result.get('sufficient_quantity')}"
    
    def test_check_stock_availability_special_characters_in_id(self):
        """
        Test handling of special characters in medication ID (edge case).
        
        Arrange: Medication ID with special characters
        Act: Call check_stock_availability with special characters
        Assert: Returns error (invalid ID format)
        """
        # Arrange
        medication_id = "med_@#$%"
        quantity = None
        
        # Act
        result = check_stock_availability(medication_id, quantity)
        
        # Assert
        # Should return error (medication not found or invalid)
        assert "error" in result or result.get("medication_id") != medication_id, \
            f"Expected error or different medication_id for invalid ID, got {result}"
    
    def test_check_stock_availability_very_long_medication_id(self):
        """
        Test handling of very long medication ID (edge case).
        
        Arrange: Very long medication ID string
        Act: Call check_stock_availability with very long ID
        Assert: Returns error (medication not found)
        """
        # Arrange
        medication_id = "med_" + "x" * 1000
        quantity = None
        
        # Act
        result = check_stock_availability(medication_id, quantity)
        
        # Assert
        assert "error" in result, f"Expected error for very long ID but got success: {result}"
        assert result["available"] is False, \
            f"Expected available=False (safe fallback), got {result.get('available')}"

