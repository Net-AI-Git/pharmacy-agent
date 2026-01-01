from pydantic import BaseModel, Field
from typing import List


class Stock(BaseModel):
    """
    Stock information model for tracking medication inventory.
    
    Purpose (Why):
    This model tracks the current inventory status of a medication, including
    availability, quantity, and restocking information. It enables the system
    to provide real-time stock information to users and manage inventory levels.
    
    Implementation (What):
    Inherits from Pydantic BaseModel to provide validation and serialization.
    Stores boolean availability flag, integer quantity, and ISO datetime string
    for the last restocking date.
    
    Attributes:
        available: Whether the medication is currently available in stock
        quantity_in_stock: Current quantity of the medication in stock
        last_restocked: ISO format datetime string of when the medication was last restocked
    
    Raises:
        ValidationError: If any field fails Pydantic validation
    """
    available: bool = Field(description="Whether the medication is currently available in stock")
    quantity_in_stock: int = Field(description="Current quantity of the medication in stock")
    last_restocked: str = Field(description="ISO format datetime string of when the medication was last restocked")

    class Config:
        json_schema_extra = {
            "example": {
                "available": True,
                "quantity_in_stock": 150,
                "last_restocked": "2024-01-15T10:30:00Z"
            }
        }


class Medication(BaseModel):
    """
    Medication model representing a pharmaceutical product in the pharmacy system.
    
    Purpose (Why):
    This model represents a complete medication record with all essential information
    needed for pharmacy operations. It stores medication details, active ingredients,
    dosage information, prescription requirements, and stock status. This enables
    the AI agent to provide accurate medication information, check availability,
    and verify prescription requirements.
    
    Implementation (What):
    Inherits from Pydantic BaseModel for validation and serialization. Includes
    bilingual names (Hebrew/English), active ingredients list, dosage and usage
    instructions, prescription requirements, and nested Stock model for inventory.
    The active_ingredients and dosage_instructions fields are marked as required
    as they are critical for medication safety and proper usage.
    
    Attributes:
        medication_id: Unique identifier for the medication
        name_he: Name of the medication in Hebrew
        name_en: Name of the medication in English
        active_ingredients: List of active ingredients (required for safety)
        dosage_forms: Available dosage forms (e.g., Tablets, Capsules, Syrup)
        dosage_instructions: Detailed dosage instructions (required field)
        usage_instructions: Instructions on how to use the medication
        requires_prescription: Whether a prescription is required
        description: General description of what the medication is used for
        stock: Current stock information (nested Stock model)
    
    Raises:
        ValidationError: If any field fails Pydantic validation, especially if
                        required fields (active_ingredients, dosage_instructions) are missing
    """
    medication_id: str = Field(description="Unique identifier for the medication")
    name_he: str = Field(description="Name of the medication in Hebrew")
    name_en: str = Field(description="Name of the medication in English")
    active_ingredients: List[str] = Field(description="List of active ingredients in the medication (required field)")
    dosage_forms: List[str] = Field(description="Available dosage forms (e.g., Tablets, Capsules, Syrup)")
    dosage_instructions: str = Field(description="Detailed dosage instructions including amount and frequency (required field)")
    usage_instructions: str = Field(description="Instructions on how to use the medication, including when to take it")
    requires_prescription: bool = Field(description="Whether a prescription is required to purchase this medication")
    description: str = Field(description="General description of what the medication is used for")
    stock: Stock = Field(description="Current stock information for this medication")

    class Config:
        json_schema_extra = {
            "example": {
                "medication_id": "med_001",
                "name_he": "Acamol",
                "name_en": "Acetaminophen",
                "active_ingredients": ["Paracetamol 500mg"],
                "dosage_forms": ["Tablets", "Capsules"],
                "dosage_instructions": "500-1000mg every 4-6 hours, maximum 4g per day",
                "usage_instructions": "Take with or after food. Can be taken up to 4 times per day as needed",
                "requires_prescription": False,
                "description": "Pain reliever and fever reducer",
                "stock": {
                    "available": True,
                    "quantity_in_stock": 150,
                    "last_restocked": "2024-01-15T10:30:00Z"
                }
            }
        }

