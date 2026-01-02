"""
Tests for tool integration and multi-step flows.

Purpose (Why):
Validates that tools work together correctly in real-world multi-step flows.
Ensures that the agent can use tools sequentially to answer complex queries
without duplication or missing information.

Implementation (What):
Tests various multi-step flows:
- General medication query (only get_medication_by_name)
- Stock availability query (get_medication_by_name + check_stock_availability)
- Prescription query (get_medication_by_name + check_prescription_requirement)
- Complex query (all three tools)
"""

import pytest
from app.tools.medication_tools import get_medication_by_name
from app.tools.inventory_tools import check_stock_availability
from app.tools.prescription_tools import check_prescription_requirement


class TestToolIntegrationFlows:
    """Test suite for tool integration and multi-step flows."""
    
    def test_flow_general_medication_query(self):
        """
        Test Flow 1: General medication question (only get_medication_by_name needed).
        
        Scenario: User asks "מה זה אקמול?" (What is Acamol?)
        Expected: Only get_medication_by_name is called, returns basic info
        
        Arrange: Medication name
        Act: Call get_medication_by_name
        Assert: Returns complete basic information, no need for other tools
        """
        # Arrange
        name = "אקמול"
        language = "he"
        
        # Act
        result = get_medication_by_name(name, language)
        
        # Assert
        assert "error" not in result, \
            f"Expected success but got error: {result.get('error', 'Unknown error')}"
        
        # Verify basic information is present
        assert "medication_id" in result, "Result must include medication_id"
        assert "name_he" in result, "Result must include Hebrew name"
        assert "name_en" in result, "Result must include English name"
        assert "active_ingredients" in result, "Result must include active ingredients"
        assert "dosage_instructions" in result, "Result must include dosage instructions"
        assert "description" in result, "Result must include description"
        
        # Verify no stock/prescription fields (not needed for general query)
        assert "available" not in result, \
            "General query should not require stock information"
        assert "requires_prescription" not in result, \
            "General query should not require prescription information"
    
    def test_flow_stock_availability_query(self):
        """
        Test Flow 2: Stock availability question (get_medication_by_name + check_stock_availability).
        
        Scenario: User asks "האם יש אקמול במלאי?" (Do you have Acamol in stock?)
        Expected: 
        1. get_medication_by_name to get medication_id
        2. check_stock_availability to get detailed stock info
        
        Arrange: Medication name
        Act: Call both tools in sequence
        Assert: Both tools provide their respective information
        """
        # Arrange
        name = "אקמול"
        language = "he"
        
        # Act - Step 1: Get medication_id
        medication_result = get_medication_by_name(name, language)
        assert "error" not in medication_result, \
            f"Expected medication search to succeed, got error: {medication_result.get('error', 'Unknown error')}"
        
        medication_id = medication_result["medication_id"]
        assert medication_id, f"Expected medication_id, got: {medication_id}"
        
        # Act - Step 2: Get stock information
        stock_result = check_stock_availability(medication_id)
        assert "error" not in stock_result, \
            f"Expected stock check to succeed, got error: {stock_result.get('error', 'Unknown error')}"
        
        # Assert - Verify we have all needed information
        # Basic medication info from step 1
        assert "name_he" in medication_result, "Should have medication name"
        assert "active_ingredients" in medication_result, "Should have active ingredients"
        
        # Stock info from step 2
        assert "available" in stock_result, "Should have stock availability"
        assert "quantity_in_stock" in stock_result, "Should have stock quantity"
        assert "last_restocked" in stock_result, "Should have last restocked date"
        
        # Verify medication_id matches
        assert stock_result["medication_id"] == medication_id, \
            f"Stock result medication_id should match, expected '{medication_id}', got '{stock_result.get('medication_id')}'"
    
    def test_flow_prescription_requirement_query(self):
        """
        Test Flow 3: Prescription requirement question (get_medication_by_name + check_prescription_requirement).
        
        Scenario: User asks "האם אקמול דורש מרשם?" (Does Acamol require a prescription?)
        Expected:
        1. get_medication_by_name to get medication_id
        2. check_prescription_requirement to get detailed prescription info
        
        Arrange: Medication name
        Act: Call both tools in sequence
        Assert: Both tools provide their respective information
        """
        # Arrange
        name = "אקמול"
        language = "he"
        
        # Act - Step 1: Get medication_id
        medication_result = get_medication_by_name(name, language)
        assert "error" not in medication_result, \
            f"Expected medication search to succeed, got error: {medication_result.get('error', 'Unknown error')}"
        
        medication_id = medication_result["medication_id"]
        assert medication_id, f"Expected medication_id, got: {medication_id}"
        
        # Act - Step 2: Get prescription information
        prescription_result = check_prescription_requirement(medication_id)
        assert "error" not in prescription_result, \
            f"Expected prescription check to succeed, got error: {prescription_result.get('error', 'Unknown error')}"
        
        # Assert - Verify we have all needed information
        # Basic medication info from step 1
        assert "name_he" in medication_result, "Should have medication name"
        assert "active_ingredients" in medication_result, "Should have active ingredients"
        
        # Prescription info from step 2
        assert "requires_prescription" in prescription_result, "Should have prescription requirement"
        assert "prescription_type" in prescription_result, "Should have prescription type"
        assert prescription_result["prescription_type"] in ["not_required", "prescription_required"], \
            f"Invalid prescription_type: {prescription_result.get('prescription_type')}"
        
        # Verify medication_id matches
        assert prescription_result["medication_id"] == medication_id, \
            f"Prescription result medication_id should match, expected '{medication_id}', got '{prescription_result.get('medication_id')}'"
    
    def test_flow_complex_query_all_tools(self):
        """
        Test Flow 4: Complex query requiring all tools.
        
        Scenario: User asks "תגיד לי על אקמול, האם יש במלאי והאם דורש מרשם?"
        (Tell me about Acamol, is it in stock and does it require a prescription?)
        Expected:
        1. get_medication_by_name to get medication_id + basic info
        2. check_stock_availability to get stock info
        3. check_prescription_requirement to get prescription info
        
        Arrange: Medication name
        Act: Call all three tools in sequence
        Assert: All tools provide their respective information without duplication
        """
        # Arrange
        name = "אקמול"
        language = "he"
        
        # Act - Step 1: Get basic medication info
        medication_result = get_medication_by_name(name, language)
        assert "error" not in medication_result, \
            f"Expected medication search to succeed, got error: {medication_result.get('error', 'Unknown error')}"
        
        medication_id = medication_result["medication_id"]
        assert medication_id, f"Expected medication_id, got: {medication_id}"
        
        # Act - Step 2: Get stock information
        stock_result = check_stock_availability(medication_id)
        assert "error" not in stock_result, \
            f"Expected stock check to succeed, got error: {stock_result.get('error', 'Unknown error')}"
        
        # Act - Step 3: Get prescription information
        prescription_result = check_prescription_requirement(medication_id)
        assert "error" not in prescription_result, \
            f"Expected prescription check to succeed, got error: {prescription_result.get('error', 'Unknown error')}"
        
        # Assert - Verify complete information from all tools
        # From get_medication_by_name
        assert "name_he" in medication_result, "Should have medication name"
        assert "active_ingredients" in medication_result, "Should have active ingredients"
        assert "dosage_instructions" in medication_result, "Should have dosage instructions"
        
        # From check_stock_availability
        assert "available" in stock_result, "Should have stock availability"
        assert "quantity_in_stock" in stock_result, "Should have stock quantity"
        assert isinstance(stock_result["available"], bool), \
            f"available should be bool, got {type(stock_result['available'])}"
        assert isinstance(stock_result["quantity_in_stock"], int), \
            f"quantity_in_stock should be int, got {type(stock_result['quantity_in_stock'])}"
        
        # From check_prescription_requirement
        assert "requires_prescription" in prescription_result, "Should have prescription requirement"
        assert "prescription_type" in prescription_result, "Should have prescription type"
        assert isinstance(prescription_result["requires_prescription"], bool), \
            f"requires_prescription should be bool, got {type(prescription_result['requires_prescription'])}"
        
        # Verify no duplication
        assert "available" not in medication_result, "medication_result should not have stock fields"
        assert "requires_prescription" not in medication_result, "medication_result should not have prescription fields"
        assert "requires_prescription" not in stock_result, "stock_result should not have prescription fields"
        assert "available" not in prescription_result, "prescription_result should not have stock fields"
        
        # Verify medication_id consistency
        assert stock_result["medication_id"] == medication_id, \
            f"Stock medication_id mismatch: expected '{medication_id}', got '{stock_result.get('medication_id')}'"
        assert prescription_result["medication_id"] == medication_id, \
            f"Prescription medication_id mismatch: expected '{medication_id}', got '{prescription_result.get('medication_id')}'"
    
    def test_flow_stock_quantity_check(self):
        """
        Test Flow: Stock quantity check with specific quantity.
        
        Scenario: User asks "האם יש מספיק כמות ל-10 יחידות?" (Is there enough quantity for 10 units?)
        Expected:
        1. get_medication_by_name to get medication_id
        2. check_stock_availability with quantity parameter
        
        Arrange: Medication name and requested quantity
        Act: Call tools in sequence with quantity parameter
        Assert: Stock tool correctly checks if sufficient quantity is available
        """
        # Arrange
        name = "אקמול"
        language = "he"
        requested_quantity = 10
        
        # Act - Step 1: Get medication_id
        medication_result = get_medication_by_name(name, language)
        assert "error" not in medication_result, \
            f"Expected medication search to succeed, got error: {medication_result.get('error', 'Unknown error')}"
        
        medication_id = medication_result["medication_id"]
        
        # Act - Step 2: Check stock with quantity
        stock_result = check_stock_availability(medication_id, quantity=requested_quantity)
        assert "error" not in stock_result, \
            f"Expected stock check to succeed, got error: {stock_result.get('error', 'Unknown error')}"
        
        # Assert
        assert "sufficient_quantity" in stock_result, \
            "Stock result should include sufficient_quantity when quantity is requested"
        assert "requested_quantity" in stock_result, \
            "Stock result should include requested_quantity"
        assert stock_result["requested_quantity"] == requested_quantity, \
            f"Expected requested_quantity={requested_quantity}, got {stock_result.get('requested_quantity')}"
        assert isinstance(stock_result["sufficient_quantity"], bool), \
            f"sufficient_quantity should be bool, got {type(stock_result['sufficient_quantity'])}"
        
        # Verify logic: sufficient_quantity should be True if quantity_in_stock >= requested_quantity
        if stock_result["sufficient_quantity"]:
            assert stock_result["quantity_in_stock"] >= requested_quantity, \
                f"If sufficient_quantity is True, quantity_in_stock ({stock_result['quantity_in_stock']}) should be >= requested_quantity ({requested_quantity})"
        else:
            assert stock_result["quantity_in_stock"] < requested_quantity, \
                f"If sufficient_quantity is False, quantity_in_stock ({stock_result['quantity_in_stock']}) should be < requested_quantity ({requested_quantity})"
    
    def test_flow_error_handling_medication_not_found(self):
        """
        Test Flow: Error handling when medication is not found.
        
        Scenario: User asks about non-existent medication
        Expected: get_medication_by_name returns error with suggestions
        
        Arrange: Non-existent medication name
        Act: Call get_medication_by_name
        Assert: Returns error with suggestions, subsequent tools should not be called
        """
        # Arrange
        name = "NonExistentMedication123"
        language = None
        
        # Act
        result = get_medication_by_name(name, language)
        
        # Assert
        assert "error" in result, \
            f"Expected error for non-existent medication, but got success: {result}"
        assert "searched_name" in result, \
            "Error result should include searched_name"
        assert "suggestions" in result, \
            "Error result should include suggestions"
        assert isinstance(result["suggestions"], list), \
            f"suggestions should be a list, got {type(result['suggestions'])}"
        
        # Verify that we cannot proceed to other tools without medication_id
        assert "medication_id" not in result, \
            "Error result should not include medication_id"
    
    def test_flow_error_handling_invalid_medication_id(self):
        """
        Test Flow: Error handling when invalid medication_id is used.
        
        Scenario: Invalid medication_id passed to stock/prescription tools
        Expected: Tools return error with safe fallback values
        
        Arrange: Invalid medication_id
        Act: Call check_stock_availability and check_prescription_requirement
        Assert: Both return errors with safe fallback values
        """
        # Arrange
        invalid_medication_id = "med_invalid_999"
        
        # Act - Test stock tool
        stock_result = check_stock_availability(invalid_medication_id)
        
        # Assert - Stock tool should return error with safe fallback
        assert "error" in stock_result, \
            f"Expected error for invalid medication_id, but got success: {stock_result}"
        assert "available" in stock_result, \
            "Error result should include available field"
        assert stock_result["available"] is False, \
            f"Error result should have available=False (safe fallback), got {stock_result.get('available')}"
        
        # Act - Test prescription tool
        prescription_result = check_prescription_requirement(invalid_medication_id)
        
        # Assert - Prescription tool should return error with safe fallback
        assert "error" in prescription_result, \
            f"Expected error for invalid medication_id, but got success: {prescription_result}"
        assert "requires_prescription" in prescription_result, \
            "Error result should include requires_prescription field"
        assert prescription_result["requires_prescription"] is True, \
            f"Error result should have requires_prescription=True (safe fallback), got {prescription_result.get('requires_prescription')}"
        assert prescription_result["prescription_type"] == "prescription_required", \
            f"Error result should have prescription_type='prescription_required' (safe fallback), got {prescription_result.get('prescription_type')}"

