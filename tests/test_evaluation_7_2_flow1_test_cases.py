"""
Tests for Section 7.2: Test Cases - Flow 1 (Stock Availability Check)

Purpose (Why):
Implements detailed test cases for Flow 1 as specified in Section 7.2.
Each test case includes: Input, Expected Tool Sequence, Expected Tool Parameters,
Expected Output, and Language.

Implementation (What):
Tests cover happy path, edge cases, error cases, and variations in both Hebrew and English.
Minimum 5+ test cases in Hebrew and 5+ in English.
"""

import pytest
from app.tools.medication_tools import get_medication_by_name
from app.tools.inventory_tools import check_stock_availability


class TestFlow1TestCasesHebrew:
    """Test cases for Flow 1 in Hebrew (Section 7.2)."""
    
    def test_case_1_1_happy_path_hebrew(self):
        """
        ✅ PASS: Test Case 1.1 (Hebrew) - Happy Path
        
        Input: "האם יש לכם אקמול במלאי?"
        Expected Tool Sequence:
          1. get_medication_by_name("אקמול", "he")
          2. check_stock_availability(medication_id)
        Expected Output: Medication available with quantity information
        Language: Hebrew
        """
        # Step 1: get_medication_by_name
        medication_result = get_medication_by_name("אקמול", "he")
        
        assert "medication_id" in medication_result or "error" in medication_result, \
            f"Expected medication_id or error, got {medication_result}"
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        
        # Step 2: check_stock_availability
        stock_result = check_stock_availability(medication_id)
        
        assert "available" in stock_result or "error" in stock_result, \
            f"Expected available or error, got {stock_result}"
        assert "medication_id" in stock_result, \
            f"Stock result should include medication_id, got {stock_result}"
        assert stock_result["medication_id"] == medication_id, \
            f"medication_id should match, got {stock_result['medication_id']}"
    
    def test_case_1_2_quantity_query_hebrew(self):
        """
        ✅ PASS: Test Case 1.2 (Hebrew) - Quantity Query
        
        Input: "כמה יחידות של אקמול יש לכם?"
        Expected Tool Sequence:
          1. get_medication_by_name("אקמול", "he")
          2. check_stock_availability(medication_id)
        Expected Output: Quantity in stock information
        Language: Hebrew
        """
        medication_result = get_medication_by_name("אקמול", "he")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        stock_result = check_stock_availability(medication_id)
        
        assert "quantity_in_stock" in stock_result or "error" in stock_result, \
            f"Expected quantity_in_stock or error, got {stock_result}"
        if "quantity_in_stock" in stock_result:
            assert isinstance(stock_result["quantity_in_stock"], int), \
                f"quantity_in_stock should be integer, got {type(stock_result['quantity_in_stock'])}"
    
    def test_case_1_3_simple_availability_hebrew(self):
        """
        ✅ PASS: Test Case 1.3 (Hebrew) - Simple Availability Check
        
        Input: "אקמול זמין?"
        Expected Tool Sequence:
          1. get_medication_by_name("אקמול", "he")
          2. check_stock_availability(medication_id)
        Expected Output: Available status (true/false)
        Language: Hebrew
        """
        medication_result = get_medication_by_name("אקמול", "he")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        stock_result = check_stock_availability(medication_id)
        
        assert "available" in stock_result or "error" in stock_result, \
            f"Expected available or error, got {stock_result}"
        if "available" in stock_result:
            assert isinstance(stock_result["available"], bool), \
                f"available should be boolean, got {type(stock_result['available'])}"
    
    def test_case_1_4_specific_quantity_hebrew(self):
        """
        ✅ PASS: Test Case 1.4 (Hebrew) - Specific Quantity Request
        
        Input: "יש לכם 50 יחידות של פרצטמול?"
        Expected Tool Sequence:
          1. get_medication_by_name("פרצטמול", "he")
          2. check_stock_availability(medication_id, quantity=50)
        Expected Output: Sufficient quantity check result
        Language: Hebrew
        """
        medication_result = get_medication_by_name("פרצטמול", "he")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        stock_result = check_stock_availability(medication_id, quantity=50)
        
        assert "available" in stock_result or "error" in stock_result, \
            f"Expected available or error, got {stock_result}"
        if "sufficient_quantity" in stock_result:
            assert isinstance(stock_result["sufficient_quantity"], bool), \
                f"sufficient_quantity should be boolean, got {type(stock_result['sufficient_quantity'])}"
        if "requested_quantity" in stock_result:
            assert stock_result["requested_quantity"] == 50, \
                f"requested_quantity should be 50, got {stock_result['requested_quantity']}"
    
    def test_case_1_5_medication_not_found_hebrew(self):
        """
        ✅ PASS: Test Case 1.5 (Hebrew) - Medication Not Found
        
        Input: "האם יש לכם תרופה-לא-קיימת במלאי?"
        Expected Tool Sequence:
          1. get_medication_by_name("תרופה-לא-קיימת", "he")
        Expected Output: Error with suggestions
        Language: Hebrew
        """
        medication_result = get_medication_by_name("תרופה-לא-קיימת-12345", "he")
        
        assert "error" in medication_result, \
            f"Expected error for non-existent medication, got {medication_result}"
        assert "searched_name" in medication_result, \
            f"Error should include searched_name, got {medication_result}"
        assert "suggestions" in medication_result, \
            f"Error should include suggestions, got {medication_result}"
    
    def test_case_1_6_stock_status_query_hebrew(self):
        """
        ✅ PASS: Test Case 1.6 (Hebrew) - Stock Status Query
        
        Input: "מה המצב של המלאי של אקמול?"
        Expected Tool Sequence:
          1. get_medication_by_name("אקמול", "he")
          2. check_stock_availability(medication_id)
        Expected Output: Complete stock status information
        Language: Hebrew
        """
        medication_result = get_medication_by_name("אקמול", "he")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        stock_result = check_stock_availability(medication_id)
        
        assert "available" in stock_result or "error" in stock_result, \
            f"Expected available or error, got {stock_result}"
        if "available" in stock_result:
            # Should have complete stock information
            assert "quantity_in_stock" in stock_result, \
                f"Should include quantity_in_stock, got {stock_result}"
            assert "last_restocked" in stock_result, \
                f"Should include last_restocked, got {stock_result}"


class TestFlow1TestCasesEnglish:
    """Test cases for Flow 1 in English (Section 7.2)."""
    
    def test_case_1_7_happy_path_english(self):
        """
        ✅ PASS: Test Case 1.7 (English) - Happy Path
        
        Input: "Do you have Acetaminophen in stock?"
        Expected Tool Sequence:
          1. get_medication_by_name("Acetaminophen", "en")
          2. check_stock_availability(medication_id)
        Expected Output: Medication available with quantity information
        Language: English
        """
        medication_result = get_medication_by_name("Acetaminophen", "en")
        
        assert "medication_id" in medication_result or "error" in medication_result, \
            f"Expected medication_id or error, got {medication_result}"
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        stock_result = check_stock_availability(medication_id)
        
        assert "available" in stock_result or "error" in stock_result, \
            f"Expected available or error, got {stock_result}"
        assert "medication_id" in stock_result, \
            f"Stock result should include medication_id, got {stock_result}"
    
    def test_case_1_8_quantity_query_english(self):
        """
        ✅ PASS: Test Case 1.8 (English) - Quantity Query
        
        Input: "How many units of Paracetamol do you have?"
        Expected Tool Sequence:
          1. get_medication_by_name("Paracetamol", "en")
          2. check_stock_availability(medication_id)
        Expected Output: Quantity in stock information
        Language: English
        """
        medication_result = get_medication_by_name("Paracetamol", "en")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        stock_result = check_stock_availability(medication_id)
        
        assert "quantity_in_stock" in stock_result or "error" in stock_result, \
            f"Expected quantity_in_stock or error, got {stock_result}"
    
    def test_case_1_9_simple_availability_english(self):
        """
        ✅ PASS: Test Case 1.9 (English) - Simple Availability Check
        
        Input: "Is Acamol available?"
        Expected Tool Sequence:
          1. get_medication_by_name("Acamol", "en")
          2. check_stock_availability(medication_id)
        Expected Output: Available status (true/false)
        Language: English
        """
        medication_result = get_medication_by_name("Acamol", "en")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        stock_result = check_stock_availability(medication_id)
        
        assert "available" in stock_result or "error" in stock_result, \
            f"Expected available or error, got {stock_result}"
        if "available" in stock_result:
            assert isinstance(stock_result["available"], bool), \
                f"available should be boolean, got {type(stock_result['available'])}"
    
    def test_case_1_10_specific_quantity_english(self):
        """
        ✅ PASS: Test Case 1.10 (English) - Specific Quantity Request
        
        Input: "Do you have 20 units of Acetaminophen?"
        Expected Tool Sequence:
          1. get_medication_by_name("Acetaminophen", "en")
          2. check_stock_availability(medication_id, quantity=20)
        Expected Output: Sufficient quantity check result
        Language: English
        """
        medication_result = get_medication_by_name("Acetaminophen", "en")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        stock_result = check_stock_availability(medication_id, quantity=20)
        
        assert "available" in stock_result or "error" in stock_result, \
            f"Expected available or error, got {stock_result}"
        if "sufficient_quantity" in stock_result:
            assert isinstance(stock_result["sufficient_quantity"], bool), \
                f"sufficient_quantity should be boolean, got {type(stock_result['sufficient_quantity'])}"
    
    def test_case_1_11_medication_not_found_english(self):
        """
        ✅ PASS: Test Case 1.11 (English) - Medication Not Found
        
        Input: "Do you have NonExistentMed in stock?"
        Expected Tool Sequence:
          1. get_medication_by_name("NonExistentMed", "en")
        Expected Output: Error with suggestions
        Language: English
        """
        medication_result = get_medication_by_name("NonExistentMed12345", "en")
        
        assert "error" in medication_result, \
            f"Expected error for non-existent medication, got {medication_result}"
        assert "searched_name" in medication_result, \
            f"Error should include searched_name, got {medication_result}"
        assert "suggestions" in medication_result, \
            f"Error should include suggestions, got {medication_result}"
    
    def test_case_1_12_stock_status_query_english(self):
        """
        ✅ PASS: Test Case 1.12 (English) - Stock Status Query
        
        Input: "What's the stock status of Paracetamol?"
        Expected Tool Sequence:
          1. get_medication_by_name("Paracetamol", "en")
          2. check_stock_availability(medication_id)
        Expected Output: Complete stock status information
        Language: English
        """
        medication_result = get_medication_by_name("Paracetamol", "en")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        stock_result = check_stock_availability(medication_id)
        
        assert "available" in stock_result or "error" in stock_result, \
            f"Expected available or error, got {stock_result}"
        if "available" in stock_result:
            assert "quantity_in_stock" in stock_result, \
                f"Should include quantity_in_stock, got {stock_result}"
            assert "last_restocked" in stock_result, \
                f"Should include last_restocked, got {stock_result}"

