from pydantic import BaseModel, Field
from typing import Literal


class Prescription(BaseModel):
    """
    Prescription model representing a medication prescription in the pharmacy system.
    
    Purpose (Why):
    This model represents a prescription record that links a user to a medication
    prescribed by a doctor. It tracks prescription validity, quantity, refills,
    and status. This enables the system to verify prescription requirements,
    check prescription validity, and manage refill tracking.
    
    Implementation (What):
    Inherits from Pydantic BaseModel for validation and serialization. Stores
    prescription metadata including dates, quantities, refills, and status.
    The status field uses Literal type to enforce valid status values only.
    
    Attributes:
        prescription_id: Unique identifier for the prescription
        user_id: ID of the user who owns this prescription
        medication_id: ID of the prescribed medication
        prescribed_by: Name of the doctor who prescribed the medication
        prescription_date: ISO format datetime string of when the prescription was issued
        expiry_date: ISO format datetime string of when the prescription expires
        quantity: Quantity of medication prescribed
        refills_remaining: Number of refills remaining for this prescription
        status: Current status of the prescription (active, expired, cancelled, completed)
    
    Raises:
        ValidationError: If any field fails Pydantic validation, especially if
                        status value is not one of the allowed Literal values
    """
    prescription_id: str = Field(description="Unique identifier for the prescription")
    user_id: str = Field(description="ID of the user who owns this prescription")
    medication_id: str = Field(description="ID of the prescribed medication")
    prescribed_by: str = Field(description="Name of the doctor who prescribed the medication")
    prescription_date: str = Field(description="ISO format datetime string of when the prescription was issued")
    expiry_date: str = Field(description="ISO format datetime string of when the prescription expires")
    quantity: int = Field(description="Quantity of medication prescribed")
    refills_remaining: int = Field(description="Number of refills remaining for this prescription")
    status: Literal["active", "expired", "cancelled", "completed"] = Field(description="Current status of the prescription")

    class Config:
        json_schema_extra = {
            "example": {
                "prescription_id": "prescription_001",
                "user_id": "user_001",
                "medication_id": "med_003",
                "prescribed_by": "Dr. Sarah Levy",
                "prescription_date": "2024-01-10T09:00:00Z",
                "expiry_date": "2024-04-10T09:00:00Z",
                "quantity": 30,
                "refills_remaining": 2,
                "status": "active"
            }
        }

