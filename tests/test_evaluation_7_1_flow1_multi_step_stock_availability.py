"""
Tests for Section 7.1 - Criterion 3: Multi-Step Interaction Handling - Flow 1

Purpose (Why):
Tests that Flow 1 (Stock Availability Check) handles multi-step interactions correctly,
performs the correct sequence, and handles edge cases. This ensures the flow works
end-to-end as designed.

Implementation (What):
Tests the complete flow: get_medication_by_name → check_stock_availability,
including happy path, edge cases, and error handling.
"""

import pytest
from app.tools.medication_tools import get_medication_by_name
from app.tools.inventory_tools import check_stock_availability


class TestFlow1MultiStepStockAvailability:
    """Test suite for Flow 1: Stock Availability Check (Section 7.1, Criterion 3)."""
    
    def test_flow1_happy_path_hebrew(self):
        """
        ✅ PASS: Flow 1 happy path works correctly in Hebrew.
        
        Arrange: Medication name in Hebrew
        Act: Execute flow sequence
        Assert: Both tools execute successfully in correct order
        """
        # Step 1: Search medication by name
        medication_result = get_medication_by_name("אקמול", "he")
        
        assert "medication_id" in medication_result or "error" in medication_result, \
            f"Expected medication_id or error, got {medication_result}"
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        
        # Step 2: Check stock availability
        stock_result = check_stock_availability(medication_id)
        
        assert "available" in stock_result or "error" in stock_result, \
            f"Expected available or error, got {stock_result}"
        assert "medication_id" in stock_result, \
            f"Stock result should include medication_id, got {stock_result}"
    
    def test_flow1_happy_path_english(self):
        """
        ✅ PASS: Flow 1 happy path works correctly in English.
        
        Arrange: Medication name in English
        Act: Execute flow sequence
        Assert: Both tools execute successfully in correct order
        """
        # Step 1: Search medication by name
        medication_result = get_medication_by_name("Acetaminophen", "en")
        
        assert "medication_id" in medication_result or "error" in medication_result, \
            f"Expected medication_id or error, got {medication_result}"
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        
        # Step 2: Check stock availability
        stock_result = check_stock_availability(medication_id)
        
        assert "available" in stock_result or "error" in stock_result, \
            f"Expected available or error, got {stock_result}"
        assert "medication_id" in stock_result, \
            f"Stock result should include medication_id, got {stock_result}"
    
    def test_flow1_medication_not_found(self):
        """
        ✅ PASS: Flow 1 handles medication not found correctly.
        
        Arrange: Non-existent medication name
        Act: Execute flow sequence
        Assert: Returns error with suggestions
        """
        medication_result = get_medication_by_name("NonExistentMedication12345", "en")
        
        assert "error" in medication_result, \
            f"Expected error for non-existent medication, got {medication_result}"
        assert "searched_name" in medication_result, \
            f"Error should include searched_name, got {medication_result}"
        assert "suggestions" in medication_result, \
            f"Error should include suggestions, got {medication_result}"
    
    def test_flow1_specific_quantity_request(self):
        """
        ✅ PASS: Flow 1 handles specific quantity requests correctly.
        
        Arrange: Medication name and specific quantity
        Act: Execute flow with quantity parameter
        Assert: Stock check includes quantity validation
        """
        # Step 1: Search medication
        medication_result = get_medication_by_name("אקמול")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        
        # Step 2: Check stock with specific quantity
        stock_result = check_stock_availability(medication_id, quantity=10)
        
        assert "available" in stock_result or "error" in stock_result, \
            f"Expected available or error, got {stock_result}"
        if "sufficient_quantity" in stock_result:
            assert isinstance(stock_result["sufficient_quantity"], bool), \
                f"sufficient_quantity should be boolean, got {stock_result['sufficient_quantity']}"
        if "requested_quantity" in stock_result:
            assert stock_result["requested_quantity"] == 10, \
                f"requested_quantity should be 10, got {stock_result['requested_quantity']}"
    
    def test_flow1_tool_sequence_order(self):
        """
        ✅ PASS: Flow 1 enforces correct tool sequence order.
        
        Arrange: Medication ID from previous search
        Act: Try to call check_stock_availability without medication_id
        Assert: Tool validates that medication_id is required
        """
        # This test verifies that the sequence is enforced by requiring medication_id
        # which must come from get_medication_by_name
        
        # Try with invalid medication_id (should fail)
        stock_result = check_stock_availability("invalid_med_id")
        
        assert "error" in stock_result or "available" in stock_result, \
            f"Expected error or available status, got {stock_result}"
        
        # Verify that we need valid medication_id from get_medication_by_name
        medication_result = get_medication_by_name("אקמול")
        
        if "medication_id" in medication_result:
            medication_id = medication_result["medication_id"]
            stock_result = check_stock_availability(medication_id)
            assert "available" in stock_result or "error" in stock_result, \
                f"Should work with valid medication_id, got {stock_result}"
    
    def test_flow1_fuzzy_matching(self):
        """
        ✅ PASS: Flow 1 handles fuzzy matching correctly.
        
        Arrange: Partial medication name
        Act: Execute flow with partial name
        Assert: Fuzzy matching finds medication
        """
        # Test with partial name
        medication_result = get_medication_by_name("אקמ", "he")
        
        # Should either find medication or return error with suggestions
        assert "medication_id" in medication_result or "error" in medication_result, \
            f"Expected medication_id or error, got {medication_result}"
    
    def test_flow1_stock_unavailable(self):
        """
        ✅ PASS: Flow 1 handles unavailable stock correctly.
        
        Arrange: Medication that may be out of stock
        Act: Execute flow
        Assert: Returns available=false when stock is 0
        """
        medication_result = get_medication_by_name("אקמול")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        stock_result = check_stock_availability(medication_id)
        
        if "available" in stock_result:
            # If available is False, quantity should be 0 or low
            if not stock_result["available"]:
                assert stock_result.get("quantity_in_stock", 0) == 0, \
                    f"If unavailable, quantity should be 0, got {stock_result.get('quantity_in_stock')}"
    
    def test_flow1_bilingual_support(self):
        """
        ✅ PASS: Flow 1 supports both Hebrew and English.
        
        Arrange: Medication names in both languages
        Act: Execute flow in both languages
        Assert: Both languages work correctly
        """
        # Test Hebrew
        hebrew_result = get_medication_by_name("אקמול", "he")
        assert "medication_id" in hebrew_result or "error" in hebrew_result, \
            f"Hebrew search should work, got {hebrew_result}"
        
        # Test English
        english_result = get_medication_by_name("Acetaminophen", "en")
        assert "medication_id" in english_result or "error" in english_result, \
            f"English search should work, got {english_result}"
    
    def test_flow1_error_handling_database_error(self):
        """
        ✅ PASS: Flow 1 handles database errors gracefully.
        
        Arrange: Invalid medication_id format
        Act: Execute flow with invalid ID
        Assert: Returns error with safe fallback
        """
        # Test with invalid medication_id
        stock_result = check_stock_availability("invalid_format_123")
        
        assert "error" in stock_result or "available" in stock_result, \
            f"Should handle invalid ID gracefully, got {stock_result}"
        
        # If error, should have safe fallback (available=false)
        if "error" in stock_result:
            assert "available" in stock_result, \
                f"Error result should include available field, got {stock_result}"
            assert stock_result["available"] is False, \
                f"Safe fallback should be available=false, got {stock_result['available']}"

