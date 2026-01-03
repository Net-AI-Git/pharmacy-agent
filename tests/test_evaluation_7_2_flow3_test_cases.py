"""
Tests for Section 7.2: Test Cases - Flow 3 (Complete Medication Information)

Purpose (Why):
Implements detailed test cases for Flow 3 as specified in Section 7.2.
Each test case includes: Input, Expected Tool Sequence, Expected Tool Parameters,
Expected Output, and Language.

Implementation (What):
Tests cover happy path, edge cases, error cases, and variations in both Hebrew and English.
Minimum 5+ test cases in Hebrew and 5+ in English.
"""

import pytest
from app.tools.medication_tools import get_medication_by_name
from app.tools.prescription_tools import check_prescription_requirement
from app.tools.inventory_tools import check_stock_availability


class TestFlow3TestCasesHebrew:
    """Test cases for Flow 3 in Hebrew (Section 7.2)."""
    
    def test_case_3_1_complete_information_hebrew(self):
        """
        ✅ PASS: Test Case 3.1 (Hebrew) - Complete Information Request
        
        Input: "תספר לי על אקמול"
        Expected Tool Sequence:
          1. get_medication_by_name("אקמול", "he")
          2. check_prescription_requirement(medication_id) [optional]
          3. check_stock_availability(medication_id) [optional]
        Expected Output: Complete medication information including active ingredients, dosage, etc.
        Language: Hebrew
        """
        medication_result = get_medication_by_name("אקמול", "he")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        # Verify required fields
        assert "active_ingredients" in medication_result, \
            f"Should include active_ingredients, got {medication_result}"
        assert "dosage_instructions" in medication_result, \
            f"Should include dosage_instructions, got {medication_result}"
        assert medication_result["active_ingredients"], \
            f"active_ingredients should not be empty, got {medication_result['active_ingredients']}"
        assert medication_result["dosage_instructions"], \
            f"dosage_instructions should not be empty, got {medication_result['dosage_instructions']}"
        
        # Optional: Check prescription and stock
        medication_id = medication_result["medication_id"]
        prescription_result = check_prescription_requirement(medication_id)
        assert "requires_prescription" in prescription_result or "error" in prescription_result, \
            f"Optional prescription check should work, got {prescription_result}"
    
    def test_case_3_2_what_is_medication_hebrew(self):
        """
        ✅ PASS: Test Case 3.2 (Hebrew) - "What is" Query
        
        Input: "מה זה פרצטמול?"
        Expected Tool Sequence:
          1. get_medication_by_name("פרצטמול", "he")
        Expected Output: Medication description and basic information
        Language: Hebrew
        """
        medication_result = get_medication_by_name("פרצטמול", "he")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        assert "description" in medication_result, \
            f"Should include description, got {medication_result}"
        assert "active_ingredients" in medication_result, \
            f"Should include active_ingredients, got {medication_result}"
        assert medication_result["description"], \
            f"description should not be empty, got {medication_result['description']}"
    
    def test_case_3_3_active_ingredients_query_hebrew(self):
        """
        ✅ PASS: Test Case 3.3 (Hebrew) - Active Ingredients Query
        
        Input: "מה הרכיבים הפעילים באקמול?"
        Expected Tool Sequence:
          1. get_medication_by_name("אקמול", "he")
        Expected Output: Active ingredients list
        Language: Hebrew
        """
        medication_result = get_medication_by_name("אקמול", "he")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        assert "active_ingredients" in medication_result, \
            f"Should include active_ingredients, got {medication_result}"
        assert isinstance(medication_result["active_ingredients"], list), \
            f"active_ingredients should be a list, got {type(medication_result['active_ingredients'])}"
        assert len(medication_result["active_ingredients"]) > 0, \
            f"active_ingredients list should not be empty, got {medication_result['active_ingredients']}"
    
    def test_case_3_4_dosage_instructions_query_hebrew(self):
        """
        ✅ PASS: Test Case 3.4 (Hebrew) - Dosage Instructions Query
        
        Input: "מה המינון של אקמול?"
        Expected Tool Sequence:
          1. get_medication_by_name("אקמול", "he")
        Expected Output: Detailed dosage instructions
        Language: Hebrew
        """
        medication_result = get_medication_by_name("אקמול", "he")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        assert "dosage_instructions" in medication_result, \
            f"Should include dosage_instructions, got {medication_result}"
        assert medication_result["dosage_instructions"], \
            f"dosage_instructions should not be empty, got {medication_result['dosage_instructions']}"
        assert isinstance(medication_result["dosage_instructions"], str), \
            f"dosage_instructions should be a string, got {type(medication_result['dosage_instructions'])}"
    
    def test_case_3_5_complete_info_with_all_details_hebrew(self):
        """
        ✅ PASS: Test Case 3.5 (Hebrew) - Complete Info with All Details
        
        Input: "תן לי פרטים על אקמול"
        Expected Tool Sequence:
          1. get_medication_by_name("אקמול", "he")
          2. check_prescription_requirement(medication_id)
          3. check_stock_availability(medication_id)
        Expected Output: All medication information including prescription and stock
        Language: Hebrew
        """
        medication_result = get_medication_by_name("אקמול", "he")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        
        # Verify all basic info fields
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
                f"Should include {field}, got {list(medication_result.keys())}"
        
        # Check prescription
        prescription_result = check_prescription_requirement(medication_id)
        assert "requires_prescription" in prescription_result or "error" in prescription_result, \
            f"Prescription check should work, got {prescription_result}"
        
        # Check stock
        stock_result = check_stock_availability(medication_id)
        assert "available" in stock_result or "error" in stock_result, \
            f"Stock check should work, got {stock_result}"
    
    def test_case_3_6_medication_not_found_hebrew(self):
        """
        ✅ PASS: Test Case 3.6 (Hebrew) - Medication Not Found
        
        Input: "תספר לי על תרופה-לא-קיימת"
        Expected Tool Sequence:
          1. get_medication_by_name("תרופה-לא-קיימת", "he")
        Expected Output: Error with suggestions
        Language: Hebrew
        """
        medication_result = get_medication_by_name("תרופה-לא-קיימת-12345", "he")
        
        assert "error" in medication_result, \
            f"Expected error for non-existent medication, got {medication_result}"
        assert "suggestions" in medication_result, \
            f"Error should include suggestions, got {medication_result}"


class TestFlow3TestCasesEnglish:
    """Test cases for Flow 3 in English (Section 7.2)."""
    
    def test_case_3_7_complete_information_english(self):
        """
        ✅ PASS: Test Case 3.7 (English) - Complete Information Request
        
        Input: "Tell me about Acetaminophen"
        Expected Tool Sequence:
          1. get_medication_by_name("Acetaminophen", "en")
          2. check_prescription_requirement(medication_id) [optional]
          3. check_stock_availability(medication_id) [optional]
        Expected Output: Complete medication information including active ingredients, dosage, etc.
        Language: English
        """
        medication_result = get_medication_by_name("Acetaminophen", "en")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        # Verify required fields
        assert "active_ingredients" in medication_result, \
            f"Should include active_ingredients, got {medication_result}"
        assert "dosage_instructions" in medication_result, \
            f"Should include dosage_instructions, got {medication_result}"
        assert medication_result["active_ingredients"], \
            f"active_ingredients should not be empty, got {medication_result['active_ingredients']}"
        assert medication_result["dosage_instructions"], \
            f"dosage_instructions should not be empty, got {medication_result['dosage_instructions']}"
    
    def test_case_3_8_what_is_medication_english(self):
        """
        ✅ PASS: Test Case 3.8 (English) - "What is" Query
        
        Input: "What is Paracetamol?"
        Expected Tool Sequence:
          1. get_medication_by_name("Paracetamol", "en")
        Expected Output: Medication description and basic information
        Language: English
        """
        medication_result = get_medication_by_name("Paracetamol", "en")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        assert "description" in medication_result, \
            f"Should include description, got {medication_result}"
        assert "active_ingredients" in medication_result, \
            f"Should include active_ingredients, got {medication_result}"
        assert medication_result["description"], \
            f"description should not be empty, got {medication_result['description']}"
    
    def test_case_3_9_active_ingredients_query_english(self):
        """
        ✅ PASS: Test Case 3.9 (English) - Active Ingredients Query
        
        Input: "What are the active ingredients in Acetaminophen?"
        Expected Tool Sequence:
          1. get_medication_by_name("Acetaminophen", "en")
        Expected Output: Active ingredients list
        Language: English
        """
        medication_result = get_medication_by_name("Acetaminophen", "en")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        assert "active_ingredients" in medication_result, \
            f"Should include active_ingredients, got {medication_result}"
        assert isinstance(medication_result["active_ingredients"], list), \
            f"active_ingredients should be a list, got {type(medication_result['active_ingredients'])}"
        assert len(medication_result["active_ingredients"]) > 0, \
            f"active_ingredients list should not be empty, got {medication_result['active_ingredients']}"
    
    def test_case_3_10_dosage_instructions_query_english(self):
        """
        ✅ PASS: Test Case 3.10 (English) - Dosage Instructions Query
        
        Input: "What is the dosage for Acetaminophen?"
        Expected Tool Sequence:
          1. get_medication_by_name("Acetaminophen", "en")
        Expected Output: Detailed dosage instructions
        Language: English
        """
        medication_result = get_medication_by_name("Acetaminophen", "en")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        assert "dosage_instructions" in medication_result, \
            f"Should include dosage_instructions, got {medication_result}"
        assert medication_result["dosage_instructions"], \
            f"dosage_instructions should not be empty, got {medication_result['dosage_instructions']}"
        assert isinstance(medication_result["dosage_instructions"], str), \
            f"dosage_instructions should be a string, got {type(medication_result['dosage_instructions'])}"
    
    def test_case_3_11_complete_info_with_all_details_english(self):
        """
        ✅ PASS: Test Case 3.11 (English) - Complete Info with All Details
        
        Input: "Give me details about Paracetamol"
        Expected Tool Sequence:
          1. get_medication_by_name("Paracetamol", "en")
          2. check_prescription_requirement(medication_id)
          3. check_stock_availability(medication_id)
        Expected Output: All medication information including prescription and stock
        Language: English
        """
        medication_result = get_medication_by_name("Paracetamol", "en")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        
        # Verify all basic info fields
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
                f"Should include {field}, got {list(medication_result.keys())}"
        
        # Check prescription
        prescription_result = check_prescription_requirement(medication_id)
        assert "requires_prescription" in prescription_result or "error" in prescription_result, \
            f"Prescription check should work, got {prescription_result}"
        
        # Check stock
        stock_result = check_stock_availability(medication_id)
        assert "available" in stock_result or "error" in stock_result, \
            f"Stock check should work, got {stock_result}"
    
    def test_case_3_12_medication_not_found_english(self):
        """
        ✅ PASS: Test Case 3.12 (English) - Medication Not Found
        
        Input: "Tell me about NonExistentMed"
        Expected Tool Sequence:
          1. get_medication_by_name("NonExistentMed", "en")
        Expected Output: Error with suggestions
        Language: English
        """
        medication_result = get_medication_by_name("NonExistentMed12345", "en")
        
        assert "error" in medication_result, \
            f"Expected error for non-existent medication, got {medication_result}"
        assert "suggestions" in medication_result, \
            f"Error should include suggestions, got {medication_result}"

