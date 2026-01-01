from pydantic import BaseModel, Field
from typing import List


class User(BaseModel):
    """
    User model representing a pharmacy customer in the pharmacy system.
    
    Purpose (Why):
    This model represents a customer/user in the pharmacy database. It stores
    essential user information and maintains references to their prescriptions,
    enabling the system to track user-specific medication history and prescriptions.
    
    Implementation (What):
    Inherits from Pydantic BaseModel to provide automatic validation, serialization,
    and type checking. The model includes user identification, contact information,
    and a list of associated prescription IDs for quick reference.
    
    Attributes:
        user_id: Unique identifier for the user in the system
        name: Full name of the user
        email: Email address for communication
        prescriptions: List of prescription IDs associated with this user
    
    Raises:
        ValidationError: If any field fails Pydantic validation (e.g., invalid email format)
    """
    user_id: str = Field(description="Unique identifier for the user")
    name: str = Field(description="Full name of the user")
    email: str = Field(description="Email address of the user")
    prescriptions: List[str] = Field(default=[], description="List of prescription IDs associated with this user")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_001",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "prescriptions": ["prescription_001"]
            }
        }

