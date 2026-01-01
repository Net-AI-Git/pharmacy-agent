"""
Tests for Task 2.3: Pydantic models validation.

Purpose (Why):
Validates that all Pydantic models are properly defined and can be imported and instantiated.

Implementation (What):
Attempts to import each model and create test instances with valid data.
"""

import pytest
from app.models.user import User
from app.models.medication import Medication, Stock
from app.models.prescription import Prescription


class TestPydanticModels:
    """Test suite for Pydantic models validation."""
    
    def test_user_model_import(self):
        """
        Test that User model can be imported.
        
        Arrange: Import statement
        Act: Import User
        Assert: Import succeeds
        """
        assert User is not None, "User model could not be imported"
    
    def test_user_model_instantiation(self):
        """
        Test that User model can be instantiated with valid data.
        
        Arrange: Valid user data
        Act: Create User instance
        Assert: Instance created successfully
        """
        user = User(
            user_id="test_001",
            name="Test User",
            email="test@example.com",
            prescriptions=[]
        )
        assert user.user_id == "test_001", f"Expected user_id='test_001', got '{user.user_id}'"
        assert user.name == "Test User", f"Expected name='Test User', got '{user.name}'"
        assert user.email == "test@example.com", f"Expected email='test@example.com', got '{user.email}'"
    
    def test_stock_model_import(self):
        """
        Test that Stock model can be imported.
        
        Arrange: Import statement
        Act: Import Stock
        Assert: Import succeeds
        """
        assert Stock is not None, "Stock model could not be imported"
    
    def test_stock_model_instantiation(self):
        """
        Test that Stock model can be instantiated with valid data.
        
        Arrange: Valid stock data
        Act: Create Stock instance
        Assert: Instance created successfully
        """
        stock = Stock(
            available=True,
            quantity_in_stock=100,
            last_restocked="2024-01-01T00:00:00Z"
        )
        assert stock.available is True, f"Expected available=True, got {stock.available}"
        assert stock.quantity_in_stock == 100, f"Expected quantity_in_stock=100, got {stock.quantity_in_stock}"
    
    def test_medication_model_import(self):
        """
        Test that Medication model can be imported.
        
        Arrange: Import statement
        Act: Import Medication
        Assert: Import succeeds
        """
        assert Medication is not None, "Medication model could not be imported"
    
    def test_medication_model_instantiation(self):
        """
        Test that Medication model can be instantiated with valid data.
        
        Arrange: Valid medication data with Stock
        Act: Create Medication instance
        Assert: Instance created successfully
        """
        stock = Stock(
            available=True,
            quantity_in_stock=100,
            last_restocked="2024-01-01T00:00:00Z"
        )
        medication = Medication(
            medication_id="test_med_001",
            name_he="תרופה בדיקה",
            name_en="Test Medication",
            active_ingredients=["Test Ingredient"],
            dosage_forms=["Tablets"],
            dosage_instructions="Test instructions",
            usage_instructions="Test usage",
            requires_prescription=False,
            description="Test description",
            stock=stock
        )
        assert medication.medication_id == "test_med_001", f"Expected medication_id='test_med_001', got '{medication.medication_id}'"
        assert len(medication.active_ingredients) > 0, "Medication must have active ingredients"
        assert len(medication.dosage_instructions) > 0, "Medication must have dosage instructions"
    
    def test_prescription_model_import(self):
        """
        Test that Prescription model can be imported.
        
        Arrange: Import statement
        Act: Import Prescription
        Assert: Import succeeds
        """
        assert Prescription is not None, "Prescription model could not be imported"
    
    def test_prescription_model_instantiation(self):
        """
        Test that Prescription model can be instantiated with valid data.
        
        Arrange: Valid prescription data
        Act: Create Prescription instance
        Assert: Instance created successfully
        """
        prescription = Prescription(
            prescription_id="test_presc_001",
            user_id="test_001",
            medication_id="test_med_001",
            prescribed_by="Dr. Test",
            prescription_date="2024-01-01T00:00:00Z",
            expiry_date="2024-04-01T00:00:00Z",
            quantity=30,
            refills_remaining=2,
            status="active"
        )
        assert prescription.prescription_id == "test_presc_001", f"Expected prescription_id='test_presc_001', got '{prescription.prescription_id}'"
        assert prescription.status == "active", f"Expected status='active', got '{prescription.status}'"
        assert prescription.status in ["active", "expired", "cancelled", "completed"], f"Status must be one of the allowed values, got '{prescription.status}'"

