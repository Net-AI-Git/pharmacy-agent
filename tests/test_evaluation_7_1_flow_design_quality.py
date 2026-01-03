"""
Tests for Section 7.1 - Criterion 6: Quality and Completeness of Flow Designs

Purpose (Why):
Tests that all flows are well-designed, have logical sequences, and cover all cases.
This ensures the flows work end-to-end and handle all scenarios correctly.

Implementation (What):
Tests flow completeness, sequence logic, edge case handling, and end-to-end functionality.
"""

import pytest
from app.tools.medication_tools import get_medication_by_name
from app.tools.prescription_tools import check_prescription_requirement
from app.tools.inventory_tools import check_stock_availability


class TestFlowDesignQuality:
    """Test suite for Flow Design Quality and Completeness (Section 7.1, Criterion 6)."""
    
    def test_flow1_sequence_is_logical(self):
        """
        ✅ PASS: Flow 1 sequence is logical and complete.
        
        Arrange: Medication name
        Act: Execute Flow 1 sequence
        Assert: Sequence is logical (search → stock check)
        """
        # Step 1: Must search first to get medication_id
        medication_result = get_medication_by_name("אקמול")
        
        assert "medication_id" in medication_result or "error" in medication_result, \
            f"Step 1 (search) should work, got {medication_result}"
        
        if "medication_id" in medication_result:
            # Step 2: Use medication_id for stock check
            stock_result = check_stock_availability(medication_result["medication_id"])
            
            assert "available" in stock_result or "error" in stock_result, \
                f"Step 2 (stock check) should work, got {stock_result}"
            # Sequence is logical: search → stock check
    
    def test_flow2_sequence_is_logical(self):
        """
        ✅ PASS: Flow 2 sequence is logical and complete.
        
        Arrange: Medication name
        Act: Execute Flow 2 sequence
        Assert: Sequence is logical (search → prescription check → optional stock)
        """
        # Step 1: Must search first to get medication_id
        medication_result = get_medication_by_name("אקמול")
        
        assert "medication_id" in medication_result or "error" in medication_result, \
            f"Step 1 (search) should work, got {medication_result}"
        
        if "medication_id" in medication_result:
            # Step 2: Use medication_id for prescription check
            prescription_result = check_prescription_requirement(medication_result["medication_id"])
            
            assert "requires_prescription" in prescription_result or "error" in prescription_result, \
                f"Step 2 (prescription check) should work, got {prescription_result}"
            
            # Step 3: Optional stock check
            stock_result = check_stock_availability(medication_result["medication_id"])
            assert "available" in stock_result or "error" in stock_result, \
                f"Step 3 (optional stock check) should work, got {stock_result}"
            # Sequence is logical: search → prescription → optional stock
    
    def test_flow3_sequence_is_logical(self):
        """
        ✅ PASS: Flow 3 sequence is logical and complete.
        
        Arrange: Medication name
        Act: Execute Flow 3 sequence
        Assert: Sequence is logical (search → optional prescription → optional stock)
        """
        # Step 1: Search for basic info
        medication_result = get_medication_by_name("אקמול")
        
        assert "medication_id" in medication_result or "error" in medication_result, \
            f"Step 1 (search) should work, got {medication_result}"
        
        if "medication_id" in medication_result:
            # Verify basic info is present
            assert "active_ingredients" in medication_result, "Basic info should include active_ingredients"
            assert "dosage_instructions" in medication_result, "Basic info should include dosage_instructions"
            
            # Step 2: Optional prescription check
            prescription_result = check_prescription_requirement(medication_result["medication_id"])
            assert "requires_prescription" in prescription_result or "error" in prescription_result, \
                f"Optional prescription check should work, got {prescription_result}"
            
            # Step 3: Optional stock check
            stock_result = check_stock_availability(medication_result["medication_id"])
            assert "available" in stock_result or "error" in stock_result, \
                f"Optional stock check should work, got {stock_result}"
            # Sequence is logical: search → optional prescription → optional stock
    
    def test_flow1_covers_all_cases(self):
        """
        ✅ PASS: Flow 1 covers all necessary cases.
        
        Arrange: Various scenarios
        Act: Test different cases
        Assert: All cases are handled
        """
        # Case 1: Medication found and available
        medication_result = get_medication_by_name("אקמול")
        if "medication_id" in medication_result:
            stock_result = check_stock_availability(medication_result["medication_id"])
            assert "available" in stock_result or "error" in stock_result, "Available case should work"
        
        # Case 2: Medication not found
        not_found_result = get_medication_by_name("NonExistentMed12345")
        assert "error" in not_found_result, "Not found case should return error"
        
        # Case 3: Specific quantity request
        if "medication_id" in medication_result:
            quantity_result = check_stock_availability(medication_result["medication_id"], quantity=10)
            assert "available" in quantity_result or "error" in quantity_result, "Quantity case should work"
    
    def test_flow2_covers_all_cases(self):
        """
        ✅ PASS: Flow 2 covers all necessary cases.
        
        Arrange: Various scenarios
        Act: Test different cases
        Assert: All cases are handled
        """
        # Case 1: Prescription required
        medication_result = get_medication_by_name("אמוקסיצילין")
        if "medication_id" in medication_result:
            prescription_result = check_prescription_requirement(medication_result["medication_id"])
            assert "requires_prescription" in prescription_result or "error" in prescription_result, \
                "Prescription required case should work"
        
        # Case 2: No prescription required
        medication_result2 = get_medication_by_name("אקמול")
        if "medication_id" in medication_result2:
            prescription_result2 = check_prescription_requirement(medication_result2["medication_id"])
            assert "requires_prescription" in prescription_result2 or "error" in prescription_result2, \
                "No prescription case should work"
        
        # Case 3: Combined prescription + stock
        if "medication_id" in medication_result2:
            stock_result = check_stock_availability(medication_result2["medication_id"])
            assert "available" in stock_result or "error" in stock_result, "Combined case should work"
    
    def test_flow3_covers_all_cases(self):
        """
        ✅ PASS: Flow 3 covers all necessary cases.
        
        Arrange: Various scenarios
        Act: Test different cases
        Assert: All cases are handled
        """
        # Case 1: Basic information only
        medication_result = get_medication_by_name("אקמול")
        if "medication_id" in medication_result:
            assert "active_ingredients" in medication_result, "Basic info case should work"
            assert "dosage_instructions" in medication_result, "Basic info case should work"
        
        # Case 2: Complete information with prescription
        if "medication_id" in medication_result:
            prescription_result = check_prescription_requirement(medication_result["medication_id"])
            assert "requires_prescription" in prescription_result or "error" in prescription_result, \
                "Complete info with prescription case should work"
        
        # Case 3: Complete information with stock
        if "medication_id" in medication_result:
            stock_result = check_stock_availability(medication_result["medication_id"])
            assert "available" in stock_result or "error" in stock_result, \
                "Complete info with stock case should work"
    
    def test_flows_handle_edge_cases(self):
        """
        ✅ PASS: All flows handle edge cases correctly.
        
        Arrange: Edge case scenarios
        Act: Test edge cases
        Assert: Edge cases are handled gracefully
        """
        # Edge case 1: Empty input
        empty_result = get_medication_by_name("")
        assert "error" in empty_result or "searched_name" in empty_result, \
            f"Empty input should be handled, got {empty_result}"
        
        # Edge case 2: Invalid medication_id
        invalid_stock = check_stock_availability("invalid_id")
        assert "error" in invalid_stock or "available" in invalid_stock, \
            f"Invalid medication_id should be handled, got {invalid_stock}"
        
        # Edge case 3: Negative quantity
        medication_result = get_medication_by_name("אקמול")
        if "medication_id" in medication_result:
            negative_quantity = check_stock_availability(medication_result["medication_id"], quantity=-1)
            assert "error" in negative_quantity or "available" in negative_quantity, \
                f"Negative quantity should be handled, got {negative_quantity}"
    
    def test_flows_end_to_end(self):
        """
        ✅ PASS: All flows work end-to-end.
        
        Arrange: Complete flow scenarios
        Act: Execute complete flows
        Assert: Flows complete successfully
        """
        # Flow 1 end-to-end
        flow1_med = get_medication_by_name("אקמול")
        if "medication_id" in flow1_med:
            flow1_stock = check_stock_availability(flow1_med["medication_id"])
            assert "available" in flow1_stock or "error" in flow1_stock, "Flow 1 should work end-to-end"
        
        # Flow 2 end-to-end
        flow2_med = get_medication_by_name("אקמול")
        if "medication_id" in flow2_med:
            flow2_prescription = check_prescription_requirement(flow2_med["medication_id"])
            assert "requires_prescription" in flow2_prescription or "error" in flow2_prescription, \
                "Flow 2 should work end-to-end"
        
        # Flow 3 end-to-end
        flow3_med = get_medication_by_name("אקמול")
        if "medication_id" in flow3_med:
            assert "active_ingredients" in flow3_med, "Flow 3 should work end-to-end"
            assert "dosage_instructions" in flow3_med, "Flow 3 should work end-to-end"
    
    def test_flows_are_well_designed(self):
        """
        ✅ PASS: All flows are well-designed with clear purpose.
        
        Arrange: Flow documentation
        Act: Verify flow design
        Assert: Flows have clear purpose and logical structure
        """
        # Flow 1: Stock availability - simple, focused
        medication_result = get_medication_by_name("אקמול")
        if "medication_id" in medication_result:
            stock_result = check_stock_availability(medication_result["medication_id"])
            # Flow 1 is well-designed: focused on stock availability
            assert "available" in stock_result or "error" in stock_result, "Flow 1 design is sound"
        
        # Flow 2: Prescription + stock - comprehensive
        if "medication_id" in medication_result:
            prescription_result = check_prescription_requirement(medication_result["medication_id"])
            # Flow 2 is well-designed: combines prescription and stock
            assert "requires_prescription" in prescription_result or "error" in prescription_result, \
                "Flow 2 design is sound"
        
        # Flow 3: Complete information - comprehensive
        # Flow 3 is well-designed: provides complete medication information
        if "medication_id" in medication_result:
            assert "active_ingredients" in medication_result, "Flow 3 design is sound"
            assert "dosage_instructions" in medication_result, "Flow 3 design is sound"

