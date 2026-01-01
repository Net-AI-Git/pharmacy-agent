# JSON Structure Design - Task 2.1

## Overview

The JSON structure contains three main objects:
- `users`: List of 10 users
- `medications`: List of 5 medications
- `prescriptions`: List of prescriptions linking users to medications

## General Structure

```json
{
  "users": [...],
  "medications": [...],
  "prescriptions": [...]
}
```

## 1. User Structure

Each user contains:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | string | Yes | Unique user identifier (e.g., "user_001") |
| `name` | string | Yes | User full name (e.g., "John Doe") |
| `email` | string | Yes | Email address |
| `prescriptions` | array[string] | No | List of prescription IDs belonging to the user |

**Example:**
```json
{
  "user_id": "user_001",
  "name": "John Doe",
  "email": "john.doe@example.com",
  "prescriptions": ["prescription_001", "prescription_002"]
}
```

## 2. Medication Structure

Each medication contains:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `medication_id` | string | Yes | Unique medication identifier (e.g., "med_001") |
| `name_he` | string | Yes | Medication name in Hebrew |
| `name_en` | string | Yes | Medication name in English |
| `active_ingredients` | array[string] | **Yes** | List of active ingredients (**required**) |
| `dosage_forms` | array[string] | No | Available dosage forms (Tablets, Capsules, Syrup, etc.) |
| `dosage_instructions` | string | **Yes** | Detailed dosage instructions (**required**) |
| `usage_instructions` | string | No | Usage instructions - when to take, how many times per day |
| `requires_prescription` | boolean | Yes | Whether the medication requires a doctor's prescription |
| `description` | string | No | Medication description |
| `stock` | object | Yes | Stock information |

### Stock Structure

| Field | Type | Description |
|-------|------|-------------|
| `available` | boolean | Whether the medication is available in stock |
| `quantity_in_stock` | integer | Quantity available in stock |
| `last_restocked` | string | Last restock date (ISO format) |

**Example:**
```json
{
  "medication_id": "med_001",
  "name_he": "Acamol",
  "name_en": "Acetaminophen",
  "active_ingredients": ["Paracetamol 500mg"],
  "dosage_forms": ["Tablets", "Capsules"],
  "dosage_instructions": "500-1000mg every 4-6 hours, maximum 4g per day",
  "usage_instructions": "Take with or after food. Can be taken up to 4 times per day as needed",
  "requires_prescription": false,
  "description": "Pain reliever and fever reducer",
  "stock": {
    "available": true,
    "quantity_in_stock": 150,
    "last_restocked": "2024-01-15T10:30:00Z"
  }
}
```

## 3. Prescription Structure

Each prescription contains:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prescription_id` | string | Yes | Unique prescription identifier (e.g., "prescription_001") |
| `user_id` | string | Yes | User identifier |
| `medication_id` | string | Yes | Medication identifier |
| `prescribed_by` | string | Yes | Name of the prescribing doctor |
| `prescription_date` | string | Yes | Prescription date (ISO format) |
| `expiry_date` | string | Yes | Prescription expiry date (ISO format) |
| `quantity` | integer | Yes | Prescribed quantity |
| `refills_remaining` | integer | Yes | Number of remaining refills |
| `status` | string | Yes | Prescription status: "active", "expired", "fulfilled", "cancelled" |

**Example:**
```json
{
  "prescription_id": "prescription_001",
  "user_id": "user_001",
  "medication_id": "med_001",
  "prescribed_by": "Dr. Sarah Levy",
  "prescription_date": "2024-01-10T09:00:00Z",
  "expiry_date": "2024-04-10T09:00:00Z",
  "quantity": 30,
  "refills_remaining": 2,
  "status": "active"
}
```

## Important Points

1. **Active Ingredients (active_ingredients)**: Required field - every medication must include at least one active ingredient
2. **Dosage Instructions (dosage_instructions)**: Required field - every medication must include detailed dosage instructions
3. **Relationships**: Prescriptions link users to medications via `user_id` and `medication_id`
4. **Dates**: All dates in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
5. **Identifiers**: All identifiers are strings with prefixes (user_, med_, prescription_)

## Verification Checklist

- [x] Each user contains: user_id, name, email, prescriptions
- [x] Each medication contains: medication_id, name_he, name_en
- [x] Each medication contains: active_ingredients (list - **required**)
- [x] Each medication contains: dosage_forms (list)
- [x] Each medication contains: dosage_instructions (**required**)
- [x] Each medication contains: usage_instructions
- [x] Each medication contains: requires_prescription, description, stock
- [x] General structure is clear and understandable
