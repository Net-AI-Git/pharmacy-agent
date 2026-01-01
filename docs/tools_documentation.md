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
Uses DatabaseManager to search the medication database by name. Supports case-insensitive partial matching in both Hebrew and English. Returns complete medication information including required fields (active_ingredients, dosage_instructions). If no exact match is found, returns error with suggestions based on similar names. Uses module-level caching for DatabaseManager.

**Parameters:**
- `name` (str, required): The medication name to search for (case-insensitive, supports partial matches)
- `language` (Optional[str]): Optional language filter ('he' for Hebrew, 'en' for English). If None, searches both languages.

**Returns:**
- `Dict[str, Any]`: Dictionary containing either:
  - `MedicationSearchResult`: If medication is found (includes all medication details)
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
    "requires_prescription": False,
    "description": "Pain reliever and fever reducer",
    "available": True,
    "quantity_in_stock": 150
}
```

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
Uses DatabaseManager to retrieve medication by ID from the database. Extracts prescription requirement information including requires_prescription status and determines prescription_type. Returns complete prescription requirement information if medication is found, or error with safe fallback values (requires_prescription=True, prescription_type="prescription_required") if not found. Uses module-level caching for DatabaseManager.

**Parameters:**
- `medication_id` (str, required): The unique identifier of the medication to check

**Returns:**
- `Dict[str, Any]`: Dictionary containing either:
  - `PrescriptionCheckResult`: If medication is found (includes prescription requirement details)
  - `PrescriptionCheckError`: If medication is not found or error occurs (includes error message and safe fallback values)

**Success Response Schema (No Prescription Required):**
```python
{
    "medication_id": "med_001",
    "medication_name": "אקמול",
    "requires_prescription": False,
    "prescription_type": "not_required"
}
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

---

## Input/Output Models

### Medication Tools Models

#### `MedicationSearchInput`
- `name` (str, required): Medication name to search for
- `language` (Optional[Literal["he", "en"]]): Language filter

#### `MedicationSearchResult`
- All medication fields plus stock information
- Includes required fields: `active_ingredients`, `dosage_instructions`

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



