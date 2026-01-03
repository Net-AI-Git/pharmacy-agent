# Tools Documentation

## Overview

The tools package (`app/tools/`) implements business logic functions that can be called by the AI agent through OpenAI function calling. Each tool provides a specific capability for the pharmacy assistant, such as searching medications, checking stock, or verifying prescription requirements.

## Tool Architecture

### Design Principles

1. **OpenAI Function Calling Compatible**: All tools are designed to work with OpenAI's function calling API
2. **Type Safety**: Full type hints and Pydantic models for input/output validation
3. **Error Handling**: Comprehensive error handling with safe fallback values
4. **Performance**: Module-level caching for DatabaseManager to reduce token usage
5. **Documentation**: Detailed docstrings following core-python-standards

### Common Patterns

All tools follow these patterns:
- Input validation and normalization
- Database lookup via DatabaseManager
- Success/error result building
- Structured error responses
- Logging at appropriate levels

## Tools

### 1. Medication Tools (`app/tools/medication_tools.py`)

#### `get_medication_by_name(name: str, language: Optional[str] = None) -> Dict[str, Any]`

**Purpose (Why):**
Enables the AI agent to find medications when users provide medication names in natural language. Supports both Hebrew and English names, handles partial matches (fuzzy matching), and provides helpful suggestions when no exact match is found.

**Implementation (What):**
Uses DatabaseManager to search the medication database by name. Supports case-insensitive partial matching in both Hebrew and English. Returns basic medication information including required fields (active_ingredients, dosage_instructions). Does NOT return stock availability or prescription requirements - use check_stock_availability and check_prescription_requirement for those. If no exact match is found, returns error with suggestions based on similar names. Uses module-level caching for DatabaseManager.

**Parameters:**
- `name` (str, required): The medication name to search for (case-insensitive, supports partial matches)
- `language` (Optional[str]): Optional language filter ('he' for Hebrew, 'en' for English). If None, searches both languages.

**Returns:**
- `Dict[str, Any]`: Dictionary containing either:
  - `MedicationSearchResult`: If medication is found (includes basic medication details only, no stock/prescription)
  - `MedicationSearchError`: If medication is not found (includes error message and suggestions)

**Success Response Schema:**
```python
{
    "medication_id": "med_001",
    "name_he": "אקמול",
    "name_en": "Acetaminophen",
    "active_ingredients": ["Paracetamol 500mg"],
    "dosage_forms": ["Tablets", "Capsules"],
    "dosage_instructions": "500-1000mg every 4-6 hours, maximum 4g per day",
    "usage_instructions": "Take with or after food",
    "description": "Pain reliever and fever reducer"
}
```

**Note:** This tool does NOT return `requires_prescription`, `available`, or `quantity_in_stock`. For prescription information, use `check_prescription_requirement(medication_id)`. For stock information, use `check_stock_availability(medication_id)`.

**Error Response Schema:**
```python
{
    "error": "Medication 'InvalidMed' not found. Please check the spelling or try a different name.",
    "searched_name": "InvalidMed",
    "suggestions": ["Acamol", "Advil", "Aspirin"]
}
```

**Raises:**
- `ValueError`: If name parameter is empty or invalid
- `RuntimeError`: If database cannot be loaded

**Example Usage:**
```python
from app.tools.medication_tools import get_medication_by_name

# Search in Hebrew
result = get_medication_by_name("אקמול", language="he")

# Search in English
result = get_medication_by_name("Acetaminophen", language="en")

# Search both languages
result = get_medication_by_name("Acamol")

# Partial match (fuzzy)
result = get_medication_by_name("acam")  # Will find "Acamol"
```

**Helper Functions:**
- `_validate_search_input()`: Validates and normalizes search input
- `_generate_suggestions()`: Generates medication name suggestions when search fails
- `_validate_medication_required_fields()`: Validates required fields (active_ingredients, dosage_instructions)
- `_build_success_result()`: Builds success result from medication data
- `_build_error_result()`: Builds error result with suggestions
- `_handle_no_medications_found()`: Handles case when no medications found
- `_handle_medication_found()`: Handles case when medication found

---

### 2. Inventory Tools (`app/tools/inventory_tools.py`)

#### `check_stock_availability(medication_id: str, quantity: Optional[int] = None) -> Dict[str, Any]`

**Purpose (Why):**
Enables the AI agent to check medication stock availability when users ask about inventory. Verifies if medications are in stock, how many units are available, and whether there is sufficient quantity for a specific request.

**Implementation (What):**
Uses DatabaseManager to retrieve medication by ID from the database. Extracts stock information including availability, quantity, and last restocked date. If a quantity is provided, verifies if there is sufficient stock. Returns complete stock information if medication is found, or error with fallback values (available=False) if not found. Uses module-level caching for DatabaseManager.

**Parameters:**
- `medication_id` (str, required): The unique identifier of the medication to check
- `quantity` (Optional[int]): Optional quantity to check availability for. If provided, verifies if there is enough stock to fulfill this quantity.

**Returns:**
- `Dict[str, Any]`: Dictionary containing either:
  - `StockCheckResult`: If medication is found (includes all stock details)
  - `StockCheckError`: If medication is not found or error occurs (includes error message and available=False as fallback)

**Success Response Schema:**
```python
{
    "medication_id": "med_001",
    "medication_name": "אקמול",
    "available": True,
    "quantity_in_stock": 150,
    "last_restocked": "2024-01-15T10:30:00Z",
    "sufficient_quantity": True,
    "requested_quantity": 10
}
```

**Error Response Schema:**
```python
{
    "error": "Medication not found: med_999. Please verify the medication ID.",
    "medication_id": "med_999",
    "available": False
}
```

**Raises:**
- `ValueError`: If medication_id parameter is empty or invalid, or if quantity is negative
- `RuntimeError`: If database cannot be loaded

**Example Usage:**
```python
from app.tools.inventory_tools import check_stock_availability

# Check general availability
result = check_stock_availability("med_001")

# Check specific quantity
result = check_stock_availability("med_001", quantity=10)

# Check if sufficient stock for large order
result = check_stock_availability("med_001", quantity=200)
if result.get("sufficient_quantity"):
    print("Enough stock available")
```

**Helper Functions:**
- `_validate_stock_input()`: Validates and normalizes stock check input
- `_build_success_result()`: Builds success result from medication stock data
- `_build_error_result()`: Builds error result with fallback values
- `_handle_medication_not_found_stock()`: Handles case when medication not found
- `_handle_stock_validation_error()`: Handles input validation errors
- `_handle_stock_unexpected_error()`: Handles unexpected errors

**Safety Features:**
- Always returns `available=False` on errors (safe default)
- Validates quantity is non-negative
- Provides clear error messages

---

### 3. Prescription Tools (`app/tools/prescription_tools.py`)

#### `check_prescription_requirement(medication_id: str) -> Dict[str, Any]`

**Purpose (Why):**
Enables the AI agent to verify whether medications require prescriptions when users ask about prescription requirements. Provides essential information for compliance with pharmacy regulations and helps customers understand what they need before attempting to purchase medications.

**Implementation (What):**
Uses DatabaseManager to retrieve medication by ID and check prescription requirement. Returns prescription requirement information including whether a prescription is required and the prescription type. Uses safe fallback values (requires_prescription=True) when medication is not found or errors occur to ensure safety.

**Parameters:**
- `medication_id` (str, required): The unique identifier of the medication to check prescription requirements for

**Returns:**
- `Dict[str, Any]`: Dictionary containing either:
  - `PrescriptionCheckResult`: If medication is found (includes requires_prescription, prescription_type)
  - `PrescriptionCheckError`: If medication is not found (includes error message and safe fallback values)

**Success Response Schema:**
```python
{
    "requires_prescription": false,
    "prescription_type": "not_required",
    "medication_name": "Acetaminophen"
}
```

**Error Response Schema:**
```python
{
    "error": "Medication 'med_invalid' not found",
    "requires_prescription": true,  # Safe fallback
    "prescription_type": "prescription_required"  # Safe fallback
}
```

**Raises:**
- `ValueError`: If medication_id parameter is empty or invalid
- `RuntimeError`: If database cannot be loaded

**Example Usage:**
```python
from app.tools.prescription_tools import check_prescription_requirement

# Check prescription requirement
result = check_prescription_requirement("med_001")
```

---

### 4. User Tools (`app/tools/user_tools.py`)

#### `get_user_by_name_or_email(name_or_email: str) -> Dict[str, Any]`

**Purpose (Why):**
Enables the AI agent to find users when they provide their name or email address instead of user_id. Supports natural language queries where users identify themselves by name or email, which is more user-friendly than requiring technical IDs. Supports case-insensitive partial matching for flexible search.

**Implementation (What):**
Validates input, searches database using DatabaseManager.search_users_by_name_or_email, handles multiple results (returns first match), and provides suggestions if no user is found. Uses module-level caching for DatabaseManager to improve performance. Returns UserSearchResult if user is found, UserSearchError if not found.

**Parameters:**
- `name_or_email` (str, required): The user name or email address to search for (case-insensitive, partial match)

**Returns:**
- `Dict[str, Any]`: Dictionary containing either:
  - `UserSearchResult`: If user is found (includes user_id, name, email, prescriptions)
  - `UserSearchError`: If user is not found (includes error message and suggestions)

**Success Response Schema:**
```python
{
    "user_id": "user_001",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "prescriptions": ["prescription_001"]
}
```

**Error Response Schema:**
```python
{
    "error": "User 'InvalidUser' not found. Please check the spelling or try a different name or email.",
    "searched_name_or_email": "InvalidUser",
    "suggestions": ["John Doe", "Jane Smith"]
}
```

**Raises:**
- `ValueError`: If name_or_email parameter is empty or invalid
- `RuntimeError`: If database cannot be loaded

**Example Usage:**
```python
from app.tools.user_tools import get_user_by_name_or_email

# Search by name
result = get_user_by_name_or_email("John Doe")

# Search by email
result = get_user_by_name_or_email("john.doe@example.com")

# Partial match
result = get_user_by_name_or_email("john")  # Will find "John Doe"
```

---

#### `get_user_prescriptions(user_id: str) -> Dict[str, Any]`

**Purpose (Why):**
Enables the AI agent to retrieve all prescriptions associated with a user. This allows users to view their prescription history and verify prescription details. Provides complete prescription information including medication names for better user experience.

**Implementation (What):**
Validates user_id, retrieves prescriptions using DatabaseManager.get_prescriptions_by_user, enriches prescription data with medication names, and returns formatted result. Returns empty list if user has no prescriptions (not an error). Uses module-level caching for DatabaseManager to improve performance.

**Parameters:**
- `user_id` (str, required): The unique identifier of the user to get prescriptions for

**Returns:**
- `Dict[str, Any]`: Dictionary containing either:
  - `UserPrescriptionsResult`: If user is found (includes user_id, user_name, prescriptions list)
  - Error dictionary: If user is not found (includes error message)

**Success Response Schema:**
```python
{
    "user_id": "user_001",
    "user_name": "John Doe",
    "prescriptions": [
        {
            "prescription_id": "prescription_001",
            "medication_id": "med_003",
            "medication_name_he": "אמוקסיצילין",
            "medication_name_en": "Amoxicillin",
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

**Error Response Schema:**
```python
{
    "error": "User 'user_invalid' not found",
    "success": false
}
```

**Raises:**
- `ValueError`: If user_id parameter is empty or invalid
- `RuntimeError`: If database cannot be loaded

**Example Usage:**
```python
from app.tools.user_tools import get_user_prescriptions

# Get all prescriptions for user
result = get_user_prescriptions("user_001")
```

---

#### `check_user_prescription_for_medication(user_id: str, medication_id: str) -> Dict[str, Any]`

**Purpose (Why):**
Enables the AI agent to verify whether a user has an active prescription for a specific medication. This is essential for prescription validation before medication purchases and helps users understand their prescription status. Only returns active prescriptions (status="active").

**Implementation (What):**
Validates inputs, retrieves user prescriptions, filters for active prescriptions matching the medication_id, and returns result. Returns has_active_prescription=false if no active prescription found (not an error). Uses module-level caching for DatabaseManager to improve performance.

**Parameters:**
- `user_id` (str, required): The unique identifier of the user to check prescription for
- `medication_id` (str, required): The unique identifier of the medication to check prescription for

**Returns:**
- `Dict[str, Any]`: Dictionary containing either:
  - `PrescriptionCheckResult`: Includes has_active_prescription and optional prescription_details
  - Error dictionary: If user or medication is not found (includes error message)

**Success Response Schema (Active Prescription Found):**
```python
{
    "has_active_prescription": true,
    "prescription_details": {
        "prescription_id": "prescription_001",
        "medication_id": "med_003",
        "medication_name_he": "אמוקסיצילין",
        "medication_name_en": "Amoxicillin",
        "prescribed_by": "Dr. Sarah Levy",
        "prescription_date": "2024-01-10T09:00:00Z",
        "expiry_date": "2024-04-10T09:00:00Z",
        "quantity": 30,
        "refills_remaining": 2,
        "status": "active"
    }
}
```

**Success Response Schema (No Active Prescription):**
```python
{
    "has_active_prescription": false,
    "prescription_details": null
}
```

**Error Response Schema:**
```python
{
    "error": "User 'user_invalid' not found",
    "success": false
}
```

**Raises:**
- `ValueError`: If user_id or medication_id parameter is empty or invalid
- `RuntimeError`: If database cannot be loaded

**Example Usage:**
```python
from app.tools.user_tools import check_user_prescription_for_medication

# Check if user has active prescription
result = check_user_prescription_for_medication("user_001", "med_003")
```

---
```

**Success Response Schema (Prescription Required):**
```python
{
    "medication_id": "med_003",
    "medication_name": "Amoxicillin",
    "requires_prescription": True,
    "prescription_type": "prescription_required"
}
```

**Error Response Schema:**
```python
{
    "error": "Medication not found: med_999. Please verify the medication ID.",
    "medication_id": "med_999",
    "requires_prescription": True,
    "prescription_type": "prescription_required"
}
```

**Raises:**
- `ValueError`: If medication_id parameter is empty or invalid
- `RuntimeError`: If database cannot be loaded

**Example Usage:**
```python
from app.tools.prescription_tools import check_prescription_requirement

# Check prescription requirement
result = check_prescription_requirement("med_001")

if result.get("requires_prescription"):
    print("Prescription required")
else:
    print("Over-the-counter medication")
```

**Helper Functions:**
- `_validate_prescription_input()`: Validates and normalizes prescription check input
- `_determine_prescription_type()`: Determines prescription type from boolean status
- `_build_success_result()`: Builds success result from medication prescription data
- `_build_error_result()`: Builds error result with safe fallback values
- `_handle_medication_not_found()`: Handles case when medication not found
- `_handle_validation_error()`: Handles input validation errors
- `_handle_unexpected_error()`: Handles unexpected errors
- `_handle_prescription_found()`: Handles case when medication found

**Safety Features:**
- Always returns `requires_prescription=True` on errors (safe default)
- Always returns `prescription_type="prescription_required"` on errors
- Ensures safety by defaulting to requiring a prescription when information is uncertain

---

## Tool Registry (`app/tools/registry.py`)

### `get_tools_for_openai() -> List[Dict[str, Any]]`

**Purpose (Why):**
Returns tool definitions in JSON Schema format that OpenAI API understands. This is what the LLM "sees" - it receives these schemas to understand what tools are available and when to use them.

**Implementation (What):**
Returns a list of tool definitions, each containing:
- `type`: "function" (OpenAI function calling type)
- `function.name`: The tool name
- `function.description`: What the tool does (from docstring)
- `function.parameters`: JSON Schema describing the parameters

**Returns:**
- `List[Dict[str, Any]]`: List of tool definitions in OpenAI format

**Example:**
```python
from app.tools.registry import get_tools_for_openai

tools = get_tools_for_openai()
# Returns list of 3 tool definitions for OpenAI API
```

---

### `execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]`

**Purpose (Why):**
Routes tool calls from OpenAI API to the correct Python function. When OpenAI decides to call a tool, it sends the tool name and arguments, and this function executes the corresponding Python function.

**Implementation (What):**
Looks up the tool function in the registry, calls it with the provided arguments, and returns the result. Handles errors gracefully with logging.

**Parameters:**
- `tool_name` (str): Name of the tool to execute (must match a key in _TOOL_FUNCTIONS)
- `arguments` (Dict[str, Any]): Dictionary of arguments to pass to the tool function

**Returns:**
- `Dict[str, Any]`: Dictionary containing the tool execution result

**Raises:**
- `ValueError`: If tool_name is not found in registry
- `Exception`: Any exception raised by the tool function

**Example:**
```python
from app.tools.registry import execute_tool

# Execute medication search
result = execute_tool(
    "get_medication_by_name",
    {"name": "Acamol", "language": "he"}
)

# Execute stock check
result = execute_tool(
    "check_stock_availability",
    {"medication_id": "med_001", "quantity": 10}
)
```

**Registered Tools:**
- `"get_medication_by_name"`: Maps to `get_medication_by_name()` function
- `"check_stock_availability"`: Maps to `check_stock_availability()` function
- `"check_prescription_requirement"`: Maps to `check_prescription_requirement()` function
- `"get_user_by_name_or_email"`: Maps to `get_user_by_name_or_email()` function
- `"get_user_prescriptions"`: Maps to `get_user_prescriptions()` function
- `"check_user_prescription_for_medication"`: Maps to `check_user_prescription_for_medication()` function

---

## Input/Output Models

### Medication Tools Models

#### `MedicationSearchInput`
- `name` (str, required): Medication name to search for
- `language` (Optional[Literal["he", "en"]]): Language filter

#### `MedicationSearchResult`
- Basic medication fields only (no stock or prescription information)
- Includes required fields: `active_ingredients`, `dosage_instructions`
- Fields: `medication_id`, `name_he`, `name_en`, `active_ingredients`, `dosage_forms`, `dosage_instructions`, `usage_instructions`, `description`
- Does NOT include: `requires_prescription`, `available`, `quantity_in_stock` (use separate tools for these)

#### `MedicationSearchError`
- `error` (str): Error message
- `searched_name` (str): Original search query
- `suggestions` (List[str]): Suggested medication names

### Inventory Tools Models

#### `StockCheckInput`
- `medication_id` (str, required): Medication ID
- `quantity` (Optional[int]): Quantity to check

#### `StockCheckResult`
- `medication_id`, `medication_name`
- `available`, `quantity_in_stock`, `last_restocked`
- `sufficient_quantity`, `requested_quantity`

#### `StockCheckError`
- `error` (str): Error message
- `medication_id` (str): Medication ID searched
- `available` (bool): Always False for errors

### User Tools Models

#### `UserSearchInput`
- `name_or_email` (str, required): User name or email to search for

#### `UserSearchResult`
- `user_id` (str): Unique identifier for the user (use for other user tools)
- `name` (str): Full name of the user
- `email` (str): Email address of the user
- `prescriptions` (List[str]): List of prescription IDs associated with this user

#### `UserSearchError`
- `error` (str): Error message
- `searched_name_or_email` (str): Original search query
- `suggestions` (List[str]): Suggested user names or emails

#### `UserPrescriptionsInput`
- `user_id` (str, required): User ID to get prescriptions for

#### `UserPrescriptionsResult`
- `user_id` (str): Unique identifier for the user
- `user_name` (str): Full name of the user
- `prescriptions` (List[PrescriptionInfo]): List of prescription information (empty if no prescriptions)

#### `PrescriptionInfo`
- All prescription fields plus medication names (Hebrew and English)
- Fields: `prescription_id`, `medication_id`, `medication_name_he`, `medication_name_en`, `prescribed_by`, `prescription_date`, `expiry_date`, `quantity`, `refills_remaining`, `status`

#### `PrescriptionCheckInput`
- `user_id` (str, required): User ID to check prescription for
- `medication_id` (str, required): Medication ID to check prescription for

#### `PrescriptionCheckResult`
- `has_active_prescription` (bool): Whether user has active prescription
- `prescription_details` (Optional[PrescriptionInfo]): Prescription details if active prescription exists, None otherwise

### Prescription Tools Models

#### `PrescriptionCheckInput`
- `medication_id` (str, required): Medication ID

#### `PrescriptionCheckResult`
- `medication_id`, `medication_name`
- `requires_prescription` (bool)
- `prescription_type` (Literal["not_required", "prescription_required"])

#### `PrescriptionCheckError`
- `error` (str): Error message
- `medication_id` (str): Medication ID searched
- `requires_prescription` (bool): Always True for errors (safe default)
- `prescription_type` (Literal): Always "prescription_required" for errors

---

## Error Handling Patterns

All tools follow consistent error handling:

1. **Input Validation**: Validate and normalize inputs first
2. **Database Lookup**: Attempt database lookup
3. **Success Path**: Build and return success result
4. **Error Path**: Build and return error result with safe fallbacks
5. **Logging**: Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)

### Safe Fallback Values

- **Stock Tools**: `available=False` on errors
- **Prescription Tools**: `requires_prescription=True` on errors (safety first)
- **Medication Tools**: Error with suggestions (no fallback, user must retry)

---

## Performance Optimization

### Module-Level Caching

All tools use module-level caching for DatabaseManager:

```python
_db_manager: Optional[DatabaseManager] = None

def _get_db_manager() -> DatabaseManager:
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
        _db_manager.load_db()
    return _db_manager
```

**Benefits:**
- Reduces token usage (database loaded once)
- Improves performance (no repeated file reads)
- Maintains database state across tool calls

---

## Best Practices

1. **Always validate inputs**: Use helper functions for validation
2. **Use safe fallbacks**: Default to safe values on errors
3. **Log appropriately**: Use correct log levels
4. **Return structured errors**: Always return consistent error format
5. **Handle edge cases**: Consider all possible failure modes
6. **Document thoroughly**: Follow core-python-standards for docstrings



