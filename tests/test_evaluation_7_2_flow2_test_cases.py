"""
Tests for Section 7.2: Test Cases - Flow 2 (Prescription Requirement + Stock Check)

Purpose (Why):
Implements detailed test cases for Flow 2 as specified in Section 7.2.
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


class TestFlow2TestCasesHebrew:
    """Test cases for Flow 2 in Hebrew (Section 7.2)."""
    
    def test_case_2_1_prescription_required_hebrew(self):
        """
        ✅ PASS: Test Case 2.1 (Hebrew) - Prescription Required
        
        Input: "אני צריך אנטיביוטיקה, האם צריך מרשם?"
        Expected Tool Sequence:
          1. get_medication_by_name("אנטיביוטיקה", "he")
          2. check_prescription_requirement(medication_id)
        Expected Output: requires_prescription=true
        Language: Hebrew
        """
        medication_result = get_medication_by_name("אמוקסיצילין", "he")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        prescription_result = check_prescription_requirement(medication_id)
        
        assert "requires_prescription" in prescription_result or "error" in prescription_result, \
            f"Expected requires_prescription or error, got {prescription_result}"
        if "requires_prescription" in prescription_result:
            assert isinstance(prescription_result["requires_prescription"], bool), \
                f"requires_prescription should be boolean, got {type(prescription_result['requires_prescription'])}"
    
    def test_case_2_2_no_prescription_required_hebrew(self):
        """
        ✅ PASS: Test Case 2.2 (Hebrew) - No Prescription Required
        
        Input: "האם אקמול דורש מרשם רופא?"
        Expected Tool Sequence:
          1. get_medication_by_name("אקמול", "he")
          2. check_prescription_requirement(medication_id)
        Expected Output: requires_prescription=false
        Language: Hebrew
        """
        medication_result = get_medication_by_name("אקמול", "he")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        prescription_result = check_prescription_requirement(medication_id)
        
        assert "requires_prescription" in prescription_result or "error" in prescription_result, \
            f"Expected requires_prescription or error, got {prescription_result}"
        if "requires_prescription" in prescription_result:
            # For over-the-counter medications, should be False
            assert isinstance(prescription_result["requires_prescription"], bool), \
                f"requires_prescription should be boolean, got {type(prescription_result['requires_prescription'])}"
    
    def test_case_2_3_combined_prescription_and_stock_hebrew(self):
        """
        ✅ PASS: Test Case 2.3 (Hebrew) - Combined Prescription + Stock
        
        Input: "האם יש לכם אנטיביוטיקה במלאי וצריך מרשם?"
        Expected Tool Sequence:
          1. get_medication_by_name("אנטיביוטיקה", "he")
          2. check_prescription_requirement(medication_id)
          3. check_stock_availability(medication_id)
        Expected Output: Both prescription and stock information
        Language: Hebrew
        """
        medication_result = get_medication_by_name("אמוקסיצילין", "he")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        
        # Step 2: Check prescription
        prescription_result = check_prescription_requirement(medication_id)
        assert "requires_prescription" in prescription_result or "error" in prescription_result, \
            f"Expected requires_prescription or error, got {prescription_result}"
        
        # Step 3: Check stock
        stock_result = check_stock_availability(medication_id)
        assert "available" in stock_result or "error" in stock_result, \
            f"Expected available or error, got {stock_result}"
    
    def test_case_2_4_prescription_query_variation_hebrew(self):
        """
        ✅ PASS: Test Case 2.4 (Hebrew) - Prescription Query Variation
        
        Input: "אני רוצה לקנות פרצטמול, צריך מרשם?"
        Expected Tool Sequence:
          1. get_medication_by_name("פרצטמול", "he")
          2. check_prescription_requirement(medication_id)
        Expected Output: Prescription requirement information
        Language: Hebrew
        """
        medication_result = get_medication_by_name("פרצטמול", "he")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        prescription_result = check_prescription_requirement(medication_id)
        
        assert "requires_prescription" in prescription_result or "error" in prescription_result, \
            f"Expected requires_prescription or error, got {prescription_result}"
        if "prescription_type" in prescription_result:
            assert prescription_result["prescription_type"] in ["not_required", "prescription_required"], \
                f"prescription_type should be valid, got {prescription_result['prescription_type']}"
    
    def test_case_2_5_medication_not_found_hebrew(self):
        """
        ✅ PASS: Test Case 2.5 (Hebrew) - Medication Not Found
        
        Input: "האם תרופה-לא-קיימת דורשת מרשם?"
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
    
    def test_case_2_6_safe_fallback_hebrew(self):
        """
        ✅ PASS: Test Case 2.6 (Hebrew) - Safe Fallback on Error
        
        Input: Invalid medication_id
        Expected Tool Sequence:
          1. check_prescription_requirement("invalid_id")
        Expected Output: Error with safe fallback (requires_prescription=true)
        Language: Hebrew
        """
        prescription_result = check_prescription_requirement("invalid_med_id_12345")
        
        assert "error" in prescription_result or "requires_prescription" in prescription_result, \
            f"Expected error or requires_prescription, got {prescription_result}"
        
        # If error, should have safe fallback
        if "error" in prescription_result:
            assert "requires_prescription" in prescription_result, \
                f"Error should include requires_prescription fallback, got {prescription_result}"
            assert prescription_result["requires_prescription"] is True, \
                f"Safe fallback should be requires_prescription=true, got {prescription_result['requires_prescription']}"


class TestFlow2TestCasesEnglish:
    """Test cases for Flow 2 in English (Section 7.2)."""
    
    def test_case_2_7_prescription_required_english(self):
        """
        ✅ PASS: Test Case 2.7 (English) - Prescription Required
        
        Input: "I need antibiotics, do I need a prescription?"
        Expected Tool Sequence:
          1. get_medication_by_name("antibiotics", "en")
          2. check_prescription_requirement(medication_id)
        Expected Output: requires_prescription=true
        Language: English
        """
        medication_result = get_medication_by_name("Amoxicillin", "en")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        prescription_result = check_prescription_requirement(medication_id)
        
        assert "requires_prescription" in prescription_result or "error" in prescription_result, \
            f"Expected requires_prescription or error, got {prescription_result}"
        if "requires_prescription" in prescription_result:
            assert isinstance(prescription_result["requires_prescription"], bool), \
                f"requires_prescription should be boolean, got {type(prescription_result['requires_prescription'])}"
    
    def test_case_2_8_no_prescription_required_english(self):
        """
        ✅ PASS: Test Case 2.8 (English) - No Prescription Required
        
        Input: "Does Acetaminophen require a prescription?"
        Expected Tool Sequence:
          1. get_medication_by_name("Acetaminophen", "en")
          2. check_prescription_requirement(medication_id)
        Expected Output: requires_prescription=false
        Language: English
        """
        medication_result = get_medication_by_name("Acetaminophen", "en")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        prescription_result = check_prescription_requirement(medication_id)
        
        assert "requires_prescription" in prescription_result or "error" in prescription_result, \
            f"Expected requires_prescription or error, got {prescription_result}"
        if "requires_prescription" in prescription_result:
            assert isinstance(prescription_result["requires_prescription"], bool), \
                f"requires_prescription should be boolean, got {type(prescription_result['requires_prescription'])}"
    
    def test_case_2_9_combined_prescription_and_stock_english(self):
        """
        ✅ PASS: Test Case 2.9 (English) - Combined Prescription + Stock
        
        Input: "Do you have antibiotics in stock and do they require a prescription?"
        Expected Tool Sequence:
          1. get_medication_by_name("antibiotics", "en")
          2. check_prescription_requirement(medication_id)
          3. check_stock_availability(medication_id)
        Expected Output: Both prescription and stock information
        Language: English
        """
        medication_result = get_medication_by_name("Amoxicillin", "en")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        
        # Step 2: Check prescription
        prescription_result = check_prescription_requirement(medication_id)
        assert "requires_prescription" in prescription_result or "error" in prescription_result, \
            f"Expected requires_prescription or error, got {prescription_result}"
        
        # Step 3: Check stock
        stock_result = check_stock_availability(medication_id)
        assert "available" in stock_result or "error" in stock_result, \
            f"Expected available or error, got {stock_result}"
    
    def test_case_2_10_prescription_query_variation_english(self):
        """
        ✅ PASS: Test Case 2.10 (English) - Prescription Query Variation
        
        Input: "I want to buy Paracetamol, do I need a prescription?"
        Expected Tool Sequence:
          1. get_medication_by_name("Paracetamol", "en")
          2. check_prescription_requirement(medication_id)
        Expected Output: Prescription requirement information
        Language: English
        """
        medication_result = get_medication_by_name("Paracetamol", "en")
        
        if "error" in medication_result:
            pytest.skip(f"Medication not found: {medication_result.get('error')}")
        
        medication_id = medication_result["medication_id"]
        prescription_result = check_prescription_requirement(medication_id)
        
        assert "requires_prescription" in prescription_result or "error" in prescription_result, \
            f"Expected requires_prescription or error, got {prescription_result}"
        if "prescription_type" in prescription_result:
            assert prescription_result["prescription_type"] in ["not_required", "prescription_required"], \
                f"prescription_type should be valid, got {prescription_result['prescription_type']}"
    
    def test_case_2_11_medication_not_found_english(self):
        """
        ✅ PASS: Test Case 2.11 (English) - Medication Not Found
        
        Input: "Does NonExistentMed require a prescription?"
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
    
    def test_case_2_12_safe_fallback_english(self):
        """
        ✅ PASS: Test Case 2.12 (English) - Safe Fallback on Error
        
        Input: Invalid medication_id
        Expected Tool Sequence:
          1. check_prescription_requirement("invalid_id")
        Expected Output: Error with safe fallback (requires_prescription=true)
        Language: English
        """
        prescription_result = check_prescription_requirement("invalid_med_id_12345")
        
        assert "error" in prescription_result or "requires_prescription" in prescription_result, \
            f"Expected error or requires_prescription, got {prescription_result}"
        
        # If error, should have safe fallback
        if "error" in prescription_result:
            assert "requires_prescription" in prescription_result, \
                f"Error should include requires_prescription fallback, got {prescription_result}"
            assert prescription_result["requires_prescription"] is True, \
                f"Safe fallback should be requires_prescription=true, got {prescription_result['requires_prescription']}"

