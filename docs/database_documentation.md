# Database Documentation

## Overview

The database layer (`app/database/`) provides a JSON-based storage solution for the pharmacy system. It manages loading, saving, and querying pharmacy data including users, medications, and prescriptions.

## DatabaseManager Class

**Location:** `app/database/db.py`

**Purpose (Why):**
Provides a centralized interface for loading, saving, and querying the pharmacy database. It manages the JSON file storage and provides type-safe access to users, medications, and prescriptions using Pydantic models.

**Implementation (What):**
Uses JSON file storage with Pydantic models for validation. Provides methods for loading/saving the database and querying by ID or name. Handles file I/O operations and converts between JSON and Pydantic models. Implements internal caching to avoid repeated file reads.

## Class Definition

```python
class DatabaseManager:
    def __init__(self, db_path: str = "data/database.json")
    def load_db(self) -> Dict[str, Any]
    def save_db(self, data: Optional[Dict[str, Any]] = None) -> None
    def get_medication_by_id(self, medication_id: str) -> Optional[Medication]
    def get_user_by_id(self, user_id: str) -> Optional[User]
    def get_prescriptions_by_user(self, user_id: str) -> List[Prescription]
    def search_medications_by_name(self, name: str, language: Optional[str] = None) -> List[Medication]
```

## Methods

### `__init__(db_path: str = "data/database.json")`

**Purpose (Why):**
Initializes the DatabaseManager with the path to the database JSON file. Sets up the internal cache for loaded data.

**Implementation (What):**
Takes an optional database path (defaults to "data/database.json"). Resolves the path relative to the project root directory. Initializes the internal `_data` cache as None.

**Parameters:**
- `db_path` (str, optional): Path to the database JSON file (default: "data/database.json")

**Example:**
```python
from app.database.db import DatabaseManager

# Use default path
db = DatabaseManager()

# Use custom path
db = DatabaseManager("custom/path/database.json")
```

---

### `load_db() -> Dict[str, Any]`

**Purpose (Why):**
Loads the pharmacy database from JSON storage into memory cache for fast access. This method provides the foundation for all database queries and operations.

**Implementation (What):**
Reads the JSON file from disk, parses it, and stores it in the internal cache (`_data`). Uses UTF-8 encoding to support Hebrew characters. Validates file existence before attempting to read. Logs the number of users, medications, and prescriptions loaded.

**Returns:**
- `Dict[str, Any]`: Dictionary containing 'users', 'medications', and 'prescriptions' lists

**Raises:**
- `FileNotFoundError`: If the database file doesn't exist
- `json.JSONDecodeError`: If the JSON file is invalid

**Example:**
```python
db = DatabaseManager()
data = db.load_db()
print(f"Loaded {len(data['users'])} users")
```

**Logging:**
- DEBUG: Logs when database is being loaded
- INFO: Logs count of users, medications, and prescriptions after successful load
- ERROR: Logs if file is not found

---

### `save_db(data: Optional[Dict[str, Any]] = None) -> None`

**Purpose (Why):**
Persists database changes to disk storage. Allows the system to maintain data consistency and recover state after application restarts.

**Implementation (What):**
Writes the database dictionary to JSON file with proper formatting (indent=2). Creates parent directories if they don't exist. Updates internal cache after successful save. Uses UTF-8 encoding to support Hebrew characters. If no data is provided, saves the cached `_data`.

**Parameters:**
- `data` (Optional[Dict[str, Any]]): Optional dictionary to save. If None, saves the cached `_data`.

**Raises:**
- `ValueError`: If no data is provided and `_data` is None
- `IOError`: If file write fails

**Example:**
```python
db = DatabaseManager()
db.load_db()

# Modify data
data = db._data
data['users'].append(new_user)

# Save changes
db.save_db(data)

# Or save cached data
db.save_db()
```

**Logging:**
- DEBUG: Logs when database is being saved
- INFO: Logs successful save
- ERROR: Logs if no data is available to save

---

### `get_medication_by_id(medication_id: str) -> Optional[Medication]`

**Purpose (Why):**
Retrieves a specific medication record by its unique identifier. This is the primary method for accessing medication details when the ID is known, enabling efficient lookups for tool operations.

**Implementation (What):**
Searches through the cached medications list for a matching ID. If data is not loaded, automatically loads the database. Returns a validated Pydantic Medication model instance if found.

**Parameters:**
- `medication_id` (str): The medication ID to search for

**Returns:**
- `Optional[Medication]`: Medication model instance if found, None otherwise

**Example:**
```python
db = DatabaseManager()
medication = db.get_medication_by_id("med_001")
if medication:
    print(f"Found: {medication.name_he}")
else:
    print("Medication not found")
```

**Logging:**
- DEBUG: Logs when medication is found
- WARNING: Logs when medication is not found

---

### `get_user_by_id(user_id: str) -> Optional[User]`

**Purpose (Why):**
Retrieves a specific user record by their unique identifier. Enables access to user information and their associated prescriptions for customer service operations.

**Implementation (What):**
Searches through the cached users list for a matching ID. If data is not loaded, automatically loads the database. Returns a validated Pydantic User model instance if found.

**Parameters:**
- `user_id` (str): The user ID to search for

**Returns:**
- `Optional[User]`: User model instance if found, None otherwise

**Example:**
```python
db = DatabaseManager()
user = db.get_user_by_id("user_001")
if user:
    print(f"User: {user.name}, Prescriptions: {len(user.prescriptions)}")
```

**Logging:**
- DEBUG: Logs when user is found
- WARNING: Logs when user is not found

---

### `get_prescriptions_by_user(user_id: str) -> List[Prescription]`

**Purpose (Why):**
Retrieves all prescription records associated with a user. This enables the system to provide users with their prescription history and verify prescription validity for medication purchases.

**Implementation (What):**
Filters the prescriptions list by `user_id` and returns all matching records as validated Pydantic Prescription model instances. If data is not loaded, automatically loads the database.

**Parameters:**
- `user_id` (str): The user ID to get prescriptions for

**Returns:**
- `List[Prescription]`: List of Prescription model instances for the user (empty list if none found)

**Example:**
```python
db = DatabaseManager()
prescriptions = db.get_prescriptions_by_user("user_001")
for presc in prescriptions:
    print(f"Prescription: {presc.prescription_id}, Status: {presc.status}")
```

**Logging:**
- DEBUG: Logs count of prescriptions found for the user

---

### `search_medications_by_name(name: str, language: Optional[str] = None) -> List[Medication]`

**Purpose (Why):**
Enables fuzzy search for medications by name in both Hebrew and English. This is the primary method for finding medications when users provide medication names rather than IDs, supporting natural language queries.

**Implementation (What):**
Performs case-insensitive partial matching against medication names in the specified language(s). Searches both Hebrew and English names if language is not specified. Prevents duplicate results by tracking already-added medications. If data is not loaded, automatically loads the database.

**Parameters:**
- `name` (str): The medication name to search for (case-insensitive, partial match)
- `language` (Optional[str]): Optional language filter ('he' for Hebrew, 'en' for English). If None, searches both languages.

**Returns:**
- `List[Medication]`: List of Medication model instances matching the search (empty list if none found)

**Example:**
```python
db = DatabaseManager()

# Search in both languages
results = db.search_medications_by_name("Acamol")

# Search only in Hebrew
results = db.search_medications_by_name("אקמול", language="he")

# Search only in English
results = db.search_medications_by_name("Acetaminophen", language="en")

# Partial match (fuzzy)
results = db.search_medications_by_name("acam")  # Will find "Acamol"
```

**Search Behavior:**
- Case-insensitive matching
- Partial string matching (substring search)
- Searches both `name_he` and `name_en` if language is None
- Prevents duplicate results (same medication_id)

**Logging:**
- DEBUG: Logs search query and number of results found
- WARNING: Logs if empty search name is provided

---

## Database Schema

The database JSON file follows this structure:

```json
{
  "users": [
    {
      "user_id": "user_001",
      "name": "John Doe",
      "email": "john.doe@example.com",
      "prescriptions": ["prescription_001", "prescription_002"]
    }
  ],
  "medications": [
    {
      "medication_id": "med_001",
      "name_he": "אקמול",
      "name_en": "Acetaminophen",
      "active_ingredients": ["Paracetamol 500mg"],
      "dosage_forms": ["Tablets", "Capsules"],
      "dosage_instructions": "500-1000mg every 4-6 hours, maximum 4g per day",
      "usage_instructions": "Take with or after food",
      "requires_prescription": false,
      "description": "Pain reliever and fever reducer",
      "stock": {
        "available": true,
        "quantity_in_stock": 150,
        "last_restocked": "2024-01-15T10:30:00Z"
      }
    }
  ],
  "prescriptions": [
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
  ]
}
```

For detailed schema documentation, see:
- `docs/database_schema.json` - JSON schema definition

## Database Structure Design

The JSON structure contains three main objects:
- `users`: List of 10 users
- `medications`: List of 5 medications
- `prescriptions`: List of prescriptions linking users to medications

### General Structure

```json
{
  "users": [...],
  "medications": [...],
  "prescriptions": [...]
}
```

### 1. User Structure

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

### 2. Medication Structure

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

#### Stock Structure

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

### 3. Prescription Structure

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

### Important Points

1. **Active Ingredients (active_ingredients)**: Required field - every medication must include at least one active ingredient
2. **Dosage Instructions (dosage_instructions)**: Required field - every medication must include detailed dosage instructions
3. **Relationships**: Prescriptions link users to medications via `user_id` and `medication_id`
4. **Dates**: All dates in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
5. **Identifiers**: All identifiers are strings with prefixes (user_, med_, prescription_)

### Verification Checklist

- [x] Each user contains: user_id, name, email, prescriptions
- [x] Each medication contains: medication_id, name_he, name_en
- [x] Each medication contains: active_ingredients (list - **required**)
- [x] Each medication contains: dosage_forms (list)
- [x] Each medication contains: dosage_instructions (**required**)
- [x] Each medication contains: usage_instructions
- [x] Each medication contains: requires_prescription, description, stock
- [x] General structure is clear and understandable

## Usage Patterns

### Basic Usage

```python
from app.database.db import DatabaseManager

# Initialize and load
db = DatabaseManager()
db.load_db()

# Query operations
medication = db.get_medication_by_id("med_001")
user = db.get_user_by_id("user_001")
prescriptions = db.get_prescriptions_by_user("user_001")
results = db.search_medications_by_name("Acamol")
```

### Caching Behavior

The DatabaseManager uses internal caching to avoid repeated file reads:

```python
db = DatabaseManager()

# First call loads from file
medication1 = db.get_medication_by_id("med_001")  # Loads database

# Subsequent calls use cache
medication2 = db.get_medication_by_id("med_002")  # Uses cached data
```

### Error Handling

```python
from app.database.db import DatabaseManager
import logging

db = DatabaseManager()

try:
    data = db.load_db()
except FileNotFoundError:
    logging.error("Database file not found")
except json.JSONDecodeError:
    logging.error("Invalid JSON in database file")
```

## Performance Considerations

1. **Caching**: Database is loaded once and cached in memory
2. **Lazy Loading**: Database is automatically loaded on first query if not already loaded
3. **File I/O**: Minimize `save_db()` calls to reduce disk writes
4. **Search Performance**: Linear search through medications list (acceptable for small datasets)

## Thread Safety

**Note:** The current implementation is not thread-safe. If multiple threads access the DatabaseManager simultaneously, use appropriate locking mechanisms.

## Best Practices

1. **Load once, use many**: Load the database once and reuse the DatabaseManager instance
2. **Handle errors**: Always handle FileNotFoundError and JSONDecodeError
3. **Save sparingly**: Only call `save_db()` when data has actually changed
4. **Use type hints**: All return values are properly typed
5. **Validate data**: Pydantic models automatically validate data when creating instances



