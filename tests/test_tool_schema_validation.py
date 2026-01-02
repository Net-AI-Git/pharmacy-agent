"""
Tests for tool schema validation and Pydantic models.

Purpose (Why):
Validates that all tool input/output schemas are correctly defined using Pydantic
models with proper Field descriptions, type hints, and validation. Ensures that
schemas follow data-schemas-and-interfaces standards.

Implementation (What):
Tests verify:
- All Pydantic models have Field descriptions
- Type hints are correct
- Validation works as expected
- Models can be serialized/deserialized
- Literal types are used where appropriate
"""

import pytest
from pydantic import ValidationError
from app.tools.medication_tools import (
    MedicationSearchInput,
    MedicationSearchResult,
    MedicationSearchError
)
from app.tools.inventory_tools import (
    StockCheckInput,
    StockCheckResult,
    StockCheckError
)
from app.tools.prescription_tools import (
    PrescriptionCheckInput,
    PrescriptionCheckResult,
    PrescriptionCheckError
)


class TestMedicationToolSchemas:
    """Test suite for medication tool schemas."""
    
    def test_medication_search_input_has_field_descriptions(self):
        """
        Test that MedicationSearchInput has Field descriptions for LLM understanding.
        
        Arrange: MedicationSearchInput model
        Act: Check model fields
        Assert: All fields have Field descriptions
        """
        # Arrange & Act
        model = MedicationSearchInput
        
        # Assert
        name_field = model.model_fields["name"]
        assert name_field.description, \
            f"name field must have description for LLM understanding, got: {name_field.description}"
        
        language_field = model.model_fields["language"]
        assert language_field.description, \
            f"language field must have description for LLM understanding, got: {language_field.description}"
    
    def test_medication_search_input_validation(self):
        """
        Test that MedicationSearchInput validates correctly.
        
        Arrange: Valid and invalid input data
        Act: Create MedicationSearchInput instances
        Assert: Valid data passes, invalid data raises ValidationError
        """
        # Arrange - Valid data
        valid_data = {
            "name": "Acamol",
            "language": "he"
        }
        
        # Act & Assert - Should not raise
        result = MedicationSearchInput(**valid_data)
        assert result.name == "Acamol", \
            f"Expected name='Acamol', got '{result.name}'"
        assert result.language == "he", \
            f"Expected language='he', got '{result.language}'"
        
        # Arrange - Invalid language
        invalid_data = {
            "name": "Acamol",
            "language": "invalid"
        }
        
        # Act & Assert - Should raise ValidationError
        with pytest.raises(ValidationError):
            MedicationSearchInput(**invalid_data)
    
    def test_medication_search_result_has_all_required_fields(self):
        """
        Test that MedicationSearchResult has all required fields with descriptions.
        
        Arrange: MedicationSearchResult model
        Act: Check model fields
        Assert: All fields have Field descriptions and correct types
        """
        # Arrange & Act
        model = MedicationSearchResult
        
        # Assert - Required fields
        required_fields = [
            "medication_id",
            "name_he",
            "name_en",
            "active_ingredients",
            "dosage_forms",
            "dosage_instructions",
            "usage_instructions",
            "description"
        ]
        
        for field_name in required_fields:
            assert field_name in model.model_fields, \
                f"Required field '{field_name}' missing from MedicationSearchResult"
            
            field = model.model_fields[field_name]
            assert field.description, \
                f"Field '{field_name}' must have description for LLM understanding"
        
        # Assert - Verify stock/prescription fields are NOT present
        forbidden_fields = ["requires_prescription", "available", "quantity_in_stock"]
        for field_name in forbidden_fields:
            assert field_name not in model.model_fields, \
                f"Forbidden field '{field_name}' should not be in MedicationSearchResult (use dedicated tools instead)"
    
    def test_medication_search_result_serialization(self):
        """
        Test that MedicationSearchResult can be serialized to dict.
        
        Arrange: Valid medication data
        Act: Create MedicationSearchResult and serialize
        Assert: Can be serialized to dict
        """
        # Arrange
        data = {
            "medication_id": "med_001",
            "name_he": "אקמול",
            "name_en": "Acetaminophen",
            "active_ingredients": ["Paracetamol 500mg"],
            "dosage_forms": ["Tablets"],
            "dosage_instructions": "500-1000mg every 4-6 hours",
            "usage_instructions": "Take with food",
            "description": "Pain reliever"
        }
        
        # Act
        result = MedicationSearchResult(**data)
        serialized = result.model_dump()
        
        # Assert
        assert isinstance(serialized, dict), \
            f"Expected dict after serialization, got {type(serialized)}"
        assert serialized["medication_id"] == "med_001", \
            f"Expected medication_id='med_001', got '{serialized.get('medication_id')}'"
        assert "active_ingredients" in serialized, \
            "Serialized result should include active_ingredients"


class TestInventoryToolSchemas:
    """Test suite for inventory tool schemas."""
    
    def test_stock_check_input_has_field_descriptions(self):
        """
        Test that StockCheckInput has Field descriptions.
        
        Arrange: StockCheckInput model
        Act: Check model fields
        Assert: All fields have Field descriptions
        """
        # Arrange & Act
        model = StockCheckInput
        
        # Assert
        medication_id_field = model.model_fields["medication_id"]
        assert medication_id_field.description, \
            f"medication_id field must have description, got: {medication_id_field.description}"
        
        quantity_field = model.model_fields["quantity"]
        assert quantity_field.description, \
            f"quantity field must have description, got: {quantity_field.description}"
    
    def test_stock_check_result_has_all_required_fields(self):
        """
        Test that StockCheckResult has all required fields.
        
        Arrange: StockCheckResult model
        Act: Check model fields
        Assert: All fields have Field descriptions
        """
        # Arrange & Act
        model = StockCheckResult
        
        # Assert - Required fields
        required_fields = [
            "medication_id",
            "medication_name",
            "available",
            "quantity_in_stock",
            "last_restocked",
            "sufficient_quantity",
            "requested_quantity"
        ]
        
        for field_name in required_fields:
            assert field_name in model.model_fields, \
                f"Required field '{field_name}' missing from StockCheckResult"
            
            field = model.model_fields[field_name]
            assert field.description, \
                f"Field '{field_name}' must have description"


class TestPrescriptionToolSchemas:
    """Test suite for prescription tool schemas."""
    
    def test_prescription_check_input_has_field_descriptions(self):
        """
        Test that PrescriptionCheckInput has Field descriptions.
        
        Arrange: PrescriptionCheckInput model
        Act: Check model fields
        Assert: All fields have Field descriptions
        """
        # Arrange & Act
        model = PrescriptionCheckInput
        
        # Assert
        medication_id_field = model.model_fields["medication_id"]
        assert medication_id_field.description, \
            f"medication_id field must have description, got: {medication_id_field.description}"
    
    def test_prescription_check_result_uses_literal_type(self):
        """
        Test that PrescriptionCheckResult uses Literal type for prescription_type.
        
        Arrange: PrescriptionCheckResult model
        Act: Check prescription_type field
        Assert: Uses Literal type with restricted values
        """
        # Arrange & Act
        model = PrescriptionCheckResult
        
        # Assert
        prescription_type_field = model.model_fields["prescription_type"]
        
        # Check that it's a Literal type (Pydantic handles this)
        # Valid values should be "not_required" or "prescription_required"
        valid_data = {
            "medication_id": "med_001",
            "medication_name": "Test",
            "requires_prescription": False,
            "prescription_type": "not_required"
        }
        
        result = PrescriptionCheckResult(**valid_data)
        assert result.prescription_type == "not_required", \
            f"Expected prescription_type='not_required', got '{result.prescription_type}'"
        
        # Test invalid value
        invalid_data = {
            "medication_id": "med_001",
            "medication_name": "Test",
            "requires_prescription": False,
            "prescription_type": "invalid_type"
        }
        
        with pytest.raises(ValidationError):
            PrescriptionCheckResult(**invalid_data)
    
    def test_prescription_check_result_has_all_required_fields(self):
        """
        Test that PrescriptionCheckResult has all required fields.
        
        Arrange: PrescriptionCheckResult model
        Act: Check model fields
        Assert: All fields have Field descriptions
        """
        # Arrange & Act
        model = PrescriptionCheckResult
        
        # Assert - Required fields
        required_fields = [
            "medication_id",
            "medication_name",
            "requires_prescription",
            "prescription_type"
        ]
        
        for field_name in required_fields:
            assert field_name in model.model_fields, \
                f"Required field '{field_name}' missing from PrescriptionCheckResult"
            
            field = model.model_fields[field_name]
            assert field.description, \
                f"Field '{field_name}' must have description"


class TestErrorSchemas:
    """Test suite for error schemas."""
    
    def test_medication_search_error_has_suggestions(self):
        """
        Test that MedicationSearchError includes suggestions field.
        
        Arrange: MedicationSearchError model
        Act: Create error instance
        Assert: Has suggestions field
        """
        # Arrange
        data = {
            "error": "Medication not found",
            "searched_name": "InvalidMed",
            "suggestions": ["Acamol", "Advil"]
        }
        
        # Act
        error = MedicationSearchError(**data)
        
        # Assert
        assert error.suggestions == ["Acamol", "Advil"], \
            f"Expected suggestions=['Acamol', 'Advil'], got {error.suggestions}"
        assert isinstance(error.suggestions, list), \
            f"suggestions should be a list, got {type(error.suggestions)}"
    
    def test_stock_check_error_has_safe_fallback(self):
        """
        Test that StockCheckError has safe fallback (available=False).
        
        Arrange: StockCheckError model
        Act: Create error instance
        Assert: Has available=False as safe fallback
        """
        # Arrange
        data = {
            "error": "Medication not found",
            "medication_id": "med_999",
            "available": False
        }
        
        # Act
        error = StockCheckError(**data)
        
        # Assert
        assert error.available is False, \
            f"Error should have available=False (safe fallback), got {error.available}"
    
    def test_prescription_check_error_has_safe_fallback(self):
        """
        Test that PrescriptionCheckError has safe fallback (requires_prescription=True).
        
        Arrange: PrescriptionCheckError model
        Act: Create error instance
        Assert: Has requires_prescription=True and prescription_type="prescription_required" as safe fallback
        """
        # Arrange
        data = {
            "error": "Medication not found",
            "medication_id": "med_999",
            "requires_prescription": True,
            "prescription_type": "prescription_required"
        }
        
        # Act
        error = PrescriptionCheckError(**data)
        
        # Assert
        assert error.requires_prescription is True, \
            f"Error should have requires_prescription=True (safe fallback), got {error.requires_prescription}"
        assert error.prescription_type == "prescription_required", \
            f"Error should have prescription_type='prescription_required' (safe fallback), got {error.prescription_type}"

