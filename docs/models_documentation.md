# Models Documentation

## Overview

The models package (`app/models/`) contains Pydantic-based data models that represent the core entities in the pharmacy system. These models provide type safety, automatic validation, and serialization capabilities.

## Models

### User Model (`app/models/user.py`)

**Purpose (Why):**
Represents a pharmacy customer in the system. Stores essential user information and maintains references to their prescriptions, enabling the system to track user-specific medication history.

**Implementation (What):**
Inherits from Pydantic BaseModel to provide automatic validation, serialization, and type checking. The model includes user identification, contact information, and a list of associated prescription IDs.

**Fields:**
- `user_id` (str, required): Unique identifier for the user in the system
- `name` (str, required): Full name of the user
- `email` (str, required): Email address for communication
- `prescriptions` (List[str], optional): List of prescription IDs associated with this user (default: empty list)

**Example:**
```python
from app.models.user import User

user = User(
    user_id="user_001",
    name="John Doe",
    email="john.doe@example.com",
    prescriptions=["prescription_001", "prescription_002"]
)
```

**Validation:**
- Email format validation (via Pydantic)
- All fields are required except `prescriptions`

**Raises:**
- `ValidationError`: If any field fails Pydantic validation (e.g., invalid email format)

---

### Stock Model (`app/models/medication.py`)

**Purpose (Why):**
Tracks the current inventory status of a medication, including availability, quantity, and restocking information. Enables the system to provide real-time stock information to users and manage inventory levels.

**Implementation (What):**
Inherits from Pydantic BaseModel to provide validation and serialization. Stores boolean availability flag, integer quantity, and ISO datetime string for the last restocking date.

**Fields:**
- `available` (bool, required): Whether the medication is currently available in stock
- `quantity_in_stock` (int, required): Current quantity of the medication in stock
- `last_restocked` (str, required): ISO format datetime string of when the medication was last restocked

**Example:**
```python
from app.models.medication import Stock

stock = Stock(
    available=True,
    quantity_in_stock=150,
    last_restocked="2024-01-15T10:30:00Z"
)
```

**Validation:**
- `quantity_in_stock` must be a non-negative integer
- `last_restocked` should be in ISO 8601 format

**Raises:**
- `ValidationError`: If any field fails Pydantic validation

---

### Medication Model (`app/models/medication.py`)

**Purpose (Why):**
Represents a complete medication record with all essential information needed for pharmacy operations. Stores medication details, active ingredients, dosage information, prescription requirements, and stock status. This enables the AI agent to provide accurate medication information, check availability, and verify prescription requirements.

**Implementation (What):**
Inherits from Pydantic BaseModel for validation and serialization. Includes bilingual names (Hebrew/English), active ingredients list, dosage and usage instructions, prescription requirements, and nested Stock model for inventory. The `active_ingredients` and `dosage_instructions` fields are marked as required as they are critical for medication safety and proper usage.

**Fields:**
- `medication_id` (str, required): Unique identifier for the medication
- `name_he` (str, required): Name of the medication in Hebrew
- `name_en` (str, required): Name of the medication in English
- `active_ingredients` (List[str], required): List of active ingredients (required for safety)
- `dosage_forms` (List[str], required): Available dosage forms (e.g., Tablets, Capsules, Syrup)
- `dosage_instructions` (str, required): Detailed dosage instructions including amount and frequency (required field)
- `usage_instructions` (str, required): Instructions on how to use the medication, including when to take it
- `requires_prescription` (bool, required): Whether a prescription is required to purchase this medication
- `description` (str, required): General description of what the medication is used for
- `stock` (Stock, required): Current stock information (nested Stock model)

**Example:**
```python
from app.models.medication import Medication, Stock

medication = Medication(
    medication_id="med_001",
    name_he="אקמול",
    name_en="Acetaminophen",
    active_ingredients=["Paracetamol 500mg"],
    dosage_forms=["Tablets", "Capsules"],
    dosage_instructions="500-1000mg every 4-6 hours, maximum 4g per day",
    usage_instructions="Take with or after food. Can be taken up to 4 times per day as needed",
    requires_prescription=False,
    description="Pain reliever and fever reducer",
    stock=Stock(
        available=True,
        quantity_in_stock=150,
        last_restocked="2024-01-15T10:30:00Z"
    )
)
```

**Validation:**
- `active_ingredients` must be a non-empty list (required field)
- `dosage_instructions` must be a non-empty string (required field)
- All other fields are required

**Raises:**
- `ValidationError`: If any field fails Pydantic validation, especially if required fields (`active_ingredients`, `dosage_instructions`) are missing

**Important Notes:**
- The `active_ingredients` field is critical for medication safety and must always be present
- The `dosage_instructions` field is required to ensure proper medication usage
- Both Hebrew and English names are required for bilingual support

---

### Prescription Model (`app/models/prescription.py`)

**Purpose (Why):**
Represents a prescription record that links a user to a medication prescribed by a doctor. Tracks prescription validity, quantity, refills, and status. This enables the system to verify prescription requirements, check prescription validity, and manage refill tracking.

**Implementation (What):**
Inherits from Pydantic BaseModel for validation and serialization. Stores prescription metadata including dates, quantities, refills, and status. The status field uses Literal type to enforce valid status values only.

**Fields:**
- `prescription_id` (str, required): Unique identifier for the prescription
- `user_id` (str, required): ID of the user who owns this prescription
- `medication_id` (str, required): ID of the prescribed medication
- `prescribed_by` (str, required): Name of the doctor who prescribed the medication
- `prescription_date` (str, required): ISO format datetime string of when the prescription was issued
- `expiry_date` (str, required): ISO format datetime string of when the prescription expires
- `quantity` (int, required): Quantity of medication prescribed
- `refills_remaining` (int, required): Number of refills remaining for this prescription
- `status` (Literal["active", "expired", "cancelled", "completed"], required): Current status of the prescription

**Example:**
```python
from app.models.prescription import Prescription

prescription = Prescription(
    prescription_id="prescription_001",
    user_id="user_001",
    medication_id="med_003",
    prescribed_by="Dr. Sarah Levy",
    prescription_date="2024-01-10T09:00:00Z",
    expiry_date="2024-04-10T09:00:00Z",
    quantity=30,
    refills_remaining=2,
    status="active"
)
```

**Validation:**
- `status` must be one of: "active", "expired", "cancelled", "completed"
- `quantity` must be a positive integer
- `refills_remaining` must be a non-negative integer
- Dates should be in ISO 8601 format

**Raises:**
- `ValidationError`: If any field fails Pydantic validation, especially if status value is not one of the allowed Literal values

**Status Values:**
- `"active"`: Prescription is currently valid and can be used
- `"expired"`: Prescription has passed its expiry date
- `"cancelled"`: Prescription was cancelled
- `"completed"`: Prescription has been fully fulfilled

---

## Model Relationships

### User ↔ Prescription
- One-to-many relationship
- User has a list of prescription IDs
- Prescription references a single user via `user_id`

### Prescription ↔ Medication
- Many-to-one relationship
- Multiple prescriptions can reference the same medication
- Prescription references a single medication via `medication_id`

### Medication ↔ Stock
- One-to-one relationship
- Each medication has exactly one Stock object
- Stock is nested within Medication model

## Usage Patterns

### Creating Models from JSON

```python
from app.models.medication import Medication

# From dictionary
med_data = {
    "medication_id": "med_001",
    "name_he": "אקמול",
    # ... other fields
}
medication = Medication(**med_data)

# From JSON string
import json
json_str = '{"medication_id": "med_001", ...}'
medication = Medication(**json.loads(json_str))
```

### Serializing Models to JSON

```python
# To dictionary
med_dict = medication.model_dump()

# To JSON string
import json
json_str = medication.model_dump_json()
```

### Validating Models

```python
from pydantic import ValidationError

try:
    medication = Medication(**invalid_data)
except ValidationError as e:
    print(f"Validation failed: {e}")
```

## Best Practices

1. **Always validate required fields**: Ensure `active_ingredients` and `dosage_instructions` are present for medications
2. **Use type hints**: All model fields are fully typed
3. **Handle ValidationError**: Always catch and handle ValidationError when creating models from external data
4. **Use model_dump()**: Use `model_dump()` instead of `dict()` for serialization
5. **ISO date format**: Always use ISO 8601 format for date strings



