# API Documentation

## Overview

This document provides comprehensive API documentation for all tools available in the Pharmacy AI Agent system. Each tool is designed to work with OpenAI's function calling API and follows consistent patterns for input, output, and error handling.

## Tool Registration

All tools are registered in `app/tools/registry.py` and can be retrieved using:

```python
from app.tools.registry import get_tools_for_openai

tools = get_tools_for_openai()
# Returns list of tool definitions for OpenAI API
```

### Tool Registry Details

The tool registry (`app/tools/registry.py`) provides two main functions:

#### `get_tools_for_openai() -> List[Dict[str, Any]]`

**Purpose:**
Returns tool definitions in JSON Schema format that OpenAI API understands. This is what the LLM "sees" - it receives these schemas to understand what tools are available and when to use them.

**Returns:**
- `List[Dict[str, Any]]`: List of tool definitions in OpenAI format
- Each tool definition contains:
  - `type`: "function" (OpenAI function calling type)
  - `function.name`: The tool name
  - `function.description`: What the tool does (from docstring)
  - `function.parameters`: JSON Schema describing the parameters

**Example:**
```python
from app.tools.registry import get_tools_for_openai

tools = get_tools_for_openai()
# Returns list of tool definitions for OpenAI API
```

#### `execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]`

**Purpose:**
Routes tool calls from OpenAI API to the correct Python function. When OpenAI decides to call a tool, it sends the tool name and arguments, and this function executes the corresponding Python function.

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

## Tool 1: get_medication_by_name

### Name and Purpose

**Tool Name:** `get_medication_by_name`

**Purpose:**
Searches for a medication in the database by name with fuzzy matching support. This tool enables the AI agent to find medications when users provide medication names in natural language. It supports both Hebrew and English names, handles partial matches (fuzzy matching), and provides helpful suggestions when no exact match is found. Returns basic medication information including active ingredients, dosage instructions, and description. Does NOT return stock availability or prescription requirements - use check_stock_availability and check_prescription_requirement for those.

### OpenAI Function Schema

```json
{
  "type": "function",
  "function": {
    "name": "get_medication_by_name",
    "description": "Search for a medication by name with fuzzy matching support. This tool enables the AI agent to find medications when users provide medication names in natural language. It supports both Hebrew and English names, handles partial matches (fuzzy matching), and provides helpful suggestions when no exact match is found. Returns basic medication information including active ingredients, dosage instructions, and description. Does NOT return stock availability or prescription requirements - use check_stock_availability and check_prescription_requirement for those.",
    "parameters": {
      "type": "object",
      "properties": {
        "name": {
          "type": "string",
          "description": "The medication name to search for. Supports partial matches and fuzzy matching. Case-insensitive. Examples: 'Acamol', 'paracet', 'אקמול'"
        },
        "language": {
          "type": "string",
          "enum": ["he", "en"],
          "description": "Optional language filter: 'he' for Hebrew, 'en' for English. If not provided, searches both languages. Use 'he' when the user asks in Hebrew, 'en' when in English."
        }
      },
      "required": ["name"]
    }
  }
}
```

### Input Schema

The tool accepts the following parameters in JSON format:

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "The medication name to search for. Supports partial matches and fuzzy matching. Case-insensitive. Examples: 'Acamol', 'paracet', 'אקמול'",
      "required": true
    },
    "language": {
      "type": "string",
      "enum": ["he", "en"],
      "description": "Optional language filter: 'he' for Hebrew, 'en' for English. If not provided, searches both languages. Use 'he' when the user asks in Hebrew, 'en' when in English.",
      "required": false
    }
  },
  "required": ["name"]
}
```

### Parameter Details

- **name** (string, required):
  - The medication name to search for
  - Supports partial matches and fuzzy matching
  - Case-insensitive
  - Examples: "Acamol", "paracet", "אקמול", "Acetaminophen"

- **language** (string, optional):
  - Language filter to narrow search results
  - Valid values: "he" (Hebrew), "en" (English)
  - If not provided, searches both languages
  - Default: `null` (searches both languages)

### Output Schema

The tool returns a dictionary containing either a success result or an error result.

### Success Response Schema

When medication is found, returns `MedicationSearchResult`:

```json
{
  "type": "object",
  "properties": {
    "medication_id": {
      "type": "string",
      "description": "Unique identifier for the medication"
    },
    "name_he": {
      "type": "string",
      "description": "Name of the medication in Hebrew"
    },
    "name_en": {
      "type": "string",
      "description": "Name of the medication in English"
    },
    "active_ingredients": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List of active ingredients in the medication (required field)"
    },
    "dosage_forms": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Available dosage forms (e.g., Tablets, Capsules, Syrup)"
    },
    "dosage_instructions": {
      "type": "string",
      "description": "Detailed dosage instructions including amount and frequency (required field)"
    },
    "usage_instructions": {
      "type": "string",
      "description": "Instructions on how to use the medication, including when to take it"
    },
    "description": {
      "type": "string",
      "description": "General description of what the medication is used for"
    }
  },
  "required": ["medication_id", "name_he", "name_en", "active_ingredients", "dosage_forms", "dosage_instructions", "usage_instructions", "description"]
}
```

### Error Response Schema

When medication is not found or an error occurs, returns `MedicationSearchError`:

```json
{
  "type": "object",
  "properties": {
    "error": {
      "type": "string",
      "description": "Error message describing why the search failed"
    },
    "searched_name": {
      "type": "string",
      "description": "The medication name that was searched for"
    },
    "suggestions": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List of suggested medication names that might match the search query (up to 5 suggestions)"
    }
  },
  "required": ["error", "searched_name", "suggestions"]
}
```

### Example Request

#### Example 1: Search in Hebrew
```json
{
  "name": "אקמול",
  "language": "he"
}
```

#### Example 2: Search in English
```json
{
  "name": "Acetaminophen",
  "language": "en"
}
```

#### Example 3: Search Both Languages (Partial Match)
```json
{
  "name": "acam"
}
```

#### Example 4: Fuzzy Match
```json
{
  "name": "paracet",
  "language": "en"
}
```

### Example Response

#### Success Response Example

```json
{
  "medication_id": "med_001",
  "name_he": "אקמול",
  "name_en": "Acetaminophen",
  "active_ingredients": ["Paracetamol 500mg"],
  "dosage_forms": ["Tablets", "Capsules"],
  "dosage_instructions": "500-1000mg every 4-6 hours, maximum 4g per day",
  "usage_instructions": "Take with or after food. Can be taken up to 4 times per day as needed",
  "description": "Pain reliever and fever reducer"
}
```

#### Error Response Example (Medication Not Found)

```json
{
  "error": "Medication 'InvalidMed' not found. Please check the spelling or try a different name.",
  "searched_name": "InvalidMed",
  "suggestions": ["Acamol", "Advil", "Aspirin", "Ibuprofen", "Paracetamol"]
}
```

#### Error Response Example (Invalid Input)

```json
{
  "error": "Medication name cannot be empty",
  "searched_name": "",
  "suggestions": []
}
```

### Error Handling

The tool handles the following error scenarios:

#### 1. Medication Not Found (404 equivalent)
- **Error Code:** Not explicitly numbered, but represents a "not found" scenario
- **Error Message:** `"Medication '{name}' not found. Please check the spelling or try a different name."`
- **Response:** Returns `MedicationSearchError` with:
  - `error`: Error message
  - `searched_name`: The original search query
  - `suggestions`: List of up to 5 suggested medication names
- **Fallback Behavior:** Provides suggestions to help user find the correct medication

#### 2. Invalid Parameters (400 equivalent)
- **Error Code:** Not explicitly numbered, but represents a "bad request" scenario
- **Error Message:** `"Medication name cannot be empty"` or similar validation error
- **Response:** Returns `MedicationSearchError` with:
  - `error`: Validation error message
  - `searched_name`: The invalid input (or empty string)
  - `suggestions`: Empty list
- **Fallback Behavior:** Returns error without suggestions

#### 3. Invalid Language Parameter
- **Error Code:** Not explicitly numbered, treated as warning
- **Error Message:** Logged as warning, language parameter ignored
- **Response:** Tool continues with `language=None` (searches both languages)
- **Fallback Behavior:** Ignores invalid language parameter and searches both languages

#### 4. Database Error (500 equivalent)
- **Error Code:** Not explicitly numbered, but represents a "server error" scenario
- **Error Message:** `"An error occurred while searching for the medication: {error_message}"`
- **Response:** Returns `MedicationSearchError` with:
  - `error`: Error message describing the system error
  - `searched_name`: The original search query
  - `suggestions`: Empty list
- **Fallback Behavior:** Returns error without suggestions, logs full traceback

#### 5. Missing Required Fields in Medication Data
- **Error Code:** Not explicitly numbered, represents data integrity issue
- **Error Message:** `"Medication data is incomplete: missing active ingredients"` or `"Medication data is incomplete: missing dosage instructions"`
- **Response:** Returns `MedicationSearchError` with:
  - `error`: Data integrity error message
  - `searched_name`: The original search query
  - `suggestions`: Empty list
- **Fallback Behavior:** Returns error indicating data incompleteness

### Fallback Behavior

The tool implements the following fallback behaviors:

1. **No Medication Found:**
   - Returns error with helpful suggestions (up to 5 medication names)
   - Suggestions are generated by:
     - Searching without language filter
     - Trying partial matches with first 3 characters if no results
     - Extracting unique medication names from search results

2. **Invalid Input:**
   - Returns error message describing the validation failure
   - No suggestions provided for invalid input

3. **Database Errors:**
   - Returns error message with system error details
   - Logs full error traceback for debugging
   - No suggestions provided for system errors

4. **Invalid Language Parameter:**
   - Logs warning
   - Ignores invalid language parameter
   - Continues search with `language=None` (searches both languages)

5. **Missing Required Fields:**
   - Returns error indicating data incompleteness
   - Prevents returning incomplete medication information
   - Ensures safety by not returning medications without required fields (active_ingredients, dosage_instructions)

### Additional Notes

- **Fuzzy Matching:** The tool supports partial string matching. For example, searching "Acam" will find "Acamol", and searching "paracet" will find "Paracetamol". This is implemented using case-insensitive partial string matching.

- **Multiple Results:** If multiple medications match the search query, the tool returns the first match. In a production system, you might want to return all matches and let the agent choose.

- **Performance:** The tool uses module-level caching for DatabaseManager to improve performance and reduce token usage. The database is loaded once and reused for all tool calls.

- **Required Fields:** The tool validates that all required fields (active_ingredients, dosage_instructions) are present before returning medication information. This ensures data integrity and safety.

---

## Tool 2: check_stock_availability

### Name and Purpose

**Tool Name:** `check_stock_availability`

**Purpose:**
Checks stock availability for a medication by ID. This tool enables the AI agent to check medication stock availability when users ask about inventory. It verifies if medications are in stock, how many units are available, and whether there is sufficient quantity for a specific request. Returns complete stock information including availability status, quantity in stock, last restocked date, and whether sufficient quantity is available for the requested amount.

### OpenAI Function Schema

```json
{
  "type": "function",
  "function": {
    "name": "check_stock_availability",
    "description": "Check stock availability for a medication by ID. This tool enables the AI agent to check medication stock availability when users ask about inventory. It verifies if medications are in stock, how many units are available, and whether there is sufficient quantity for a specific request. Returns complete stock information including availability status, quantity in stock, last restocked date, and whether sufficient quantity is available for the requested amount.",
    "parameters": {
      "type": "object",
      "properties": {
        "medication_id": {
          "type": "string",
          "description": "The unique identifier of the medication to check stock for. This is typically obtained from a previous medication search. Example: 'med_001'"
        },
        "quantity": {
          "type": "integer",
          "description": "Optional quantity to check availability for. If provided, the tool will verify if there is enough stock to fulfill this quantity. If not provided, only checks general availability. Must be a positive integer. Example: 10"
        }
      },
      "required": ["medication_id"]
    }
  }
}
```

### Input Schema

The tool accepts the following parameters in JSON format:

```json
{
  "type": "object",
  "properties": {
    "medication_id": {
      "type": "string",
      "description": "The unique identifier of the medication to check stock for. This is typically obtained from a previous medication search. Example: 'med_001'",
      "required": true
    },
    "quantity": {
      "type": "integer",
      "description": "Optional quantity to check availability for. If provided, the tool will verify if there is enough stock to fulfill this quantity. If not provided, only checks general availability. Must be a positive integer. Example: 10",
      "required": false
    }
  },
  "required": ["medication_id"]
}
```

### Parameter Details

- **medication_id** (string, required):
  - The unique identifier of the medication to check stock for
  - Typically obtained from a previous medication search (e.g., from `get_medication_by_name`)
  - Example: "med_001", "med_002"

- **quantity** (integer, optional):
  - Optional quantity to check availability for
  - If provided, the tool verifies if there is enough stock to fulfill this quantity
  - Must be a positive integer (>= 0)
  - If not provided, only checks general availability
  - Example: 10, 50, 100

### Output Schema

The tool returns a dictionary containing either a success result or an error result.

### Success Response Schema

When medication is found and stock information is retrieved, returns `StockCheckResult`:

```json
{
  "type": "object",
  "properties": {
    "medication_id": {
      "type": "string",
      "description": "Unique identifier for the medication"
    },
    "medication_name": {
      "type": "string",
      "description": "Name of the medication (for display purposes)"
    },
    "available": {
      "type": "boolean",
      "description": "Whether the medication is currently available in stock"
    },
    "quantity_in_stock": {
      "type": "integer",
      "description": "Current quantity of the medication in stock"
    },
    "last_restocked": {
      "type": "string",
      "description": "ISO format datetime string of when the medication was last restocked"
    },
    "sufficient_quantity": {
      "type": "boolean",
      "description": "Whether there is enough stock for the requested quantity (True if quantity was not provided, or if quantity_in_stock >= requested_quantity)"
    },
    "requested_quantity": {
      "type": "integer",
      "description": "The quantity that was requested (None if not provided)",
      "nullable": true
    }
  },
  "required": ["medication_id", "medication_name", "available", "quantity_in_stock", "last_restocked", "sufficient_quantity", "requested_quantity"]
}
```

### Error Response Schema

When medication is not found or an error occurs, returns `StockCheckError`:

```json
{
  "type": "object",
  "properties": {
    "error": {
      "type": "string",
      "description": "Error message describing why the stock check failed"
    },
    "medication_id": {
      "type": "string",
      "description": "The medication ID that was searched for"
    },
    "available": {
      "type": "boolean",
      "description": "Fallback availability status (always False for errors, safe default)"
    }
  },
  "required": ["error", "medication_id", "available"]
}
```

### Example Request

#### Example 1: Check General Availability
```json
{
  "medication_id": "med_001"
}
```

#### Example 2: Check Specific Quantity
```json
{
  "medication_id": "med_001",
  "quantity": 10
}
```

#### Example 3: Check Large Quantity
```json
{
  "medication_id": "med_001",
  "quantity": 200
}
```

### Example Response

#### Success Response Example (Available)

```json
{
  "medication_id": "med_001",
  "medication_name": "אקמול",
  "available": true,
  "quantity_in_stock": 150,
  "last_restocked": "2024-01-15T10:30:00Z",
  "sufficient_quantity": true,
  "requested_quantity": 10
}
```

#### Success Response Example (Insufficient Quantity)

```json
{
  "medication_id": "med_001",
  "medication_name": "אקמול",
  "available": true,
  "quantity_in_stock": 50,
  "last_restocked": "2024-01-15T10:30:00Z",
  "sufficient_quantity": false,
  "requested_quantity": 100
}
```

#### Success Response Example (Out of Stock)

```json
{
  "medication_id": "med_002",
  "medication_name": "Advil",
  "available": false,
  "quantity_in_stock": 0,
  "last_restocked": "2024-01-10T08:00:00Z",
  "sufficient_quantity": false,
  "requested_quantity": 5
}
```

#### Success Response Example (No Quantity Requested)

```json
{
  "medication_id": "med_001",
  "medication_name": "אקמול",
  "available": true,
  "quantity_in_stock": 150,
  "last_restocked": "2024-01-15T10:30:00Z",
  "sufficient_quantity": true,
  "requested_quantity": null
}
```

#### Error Response Example (Medication Not Found)

```json
{
  "error": "Medication not found: med_999. Please verify the medication ID.",
  "medication_id": "med_999",
  "available": false
}
```

#### Error Response Example (Invalid Input)

```json
{
  "error": "Medication ID cannot be empty",
  "medication_id": "",
  "available": false
}
```

#### Error Response Example (Invalid Quantity)

```json
{
  "error": "Quantity cannot be negative",
  "medication_id": "med_001",
  "available": false
}
```

### Error Handling

The tool handles the following error scenarios:

#### 1. Medication Not Found (404 equivalent)
- **Error Code:** Not explicitly numbered, but represents a "not found" scenario
- **Error Message:** `"Medication not found: {medication_id}. Please verify the medication ID."`
- **Response:** Returns `StockCheckError` with:
  - `error`: Error message
  - `medication_id`: The medication ID that was searched
  - `available`: `false` (safe default)
- **Fallback Behavior:** Returns `available=false` as safe default

#### 2. Invalid Parameters (400 equivalent)
- **Error Code:** Not explicitly numbered, but represents a "bad request" scenario
- **Error Messages:**
  - `"Medication ID cannot be empty"` - if medication_id is empty
  - `"Quantity cannot be negative"` - if quantity is negative
- **Response:** Returns `StockCheckError` with:
  - `error`: Validation error message
  - `medication_id`: The invalid medication ID (or empty string)
  - `available`: `false` (safe default)
- **Fallback Behavior:** Returns `available=false` as safe default

#### 3. Database Error (500 equivalent)
- **Error Code:** Not explicitly numbered, but represents a "server error" scenario
- **Error Message:** `"An error occurred while checking stock: {error_message}"`
- **Response:** Returns `StockCheckError` with:
  - `error`: Error message describing the system error
  - `medication_id`: The medication ID that was being checked (or empty string)
  - `available`: `false` (safe default)
- **Fallback Behavior:** Returns `available=false` as safe default, logs full traceback

### Fallback Behavior

The tool implements the following fallback behaviors:

1. **Medication Not Found:**
   - Returns error with `available=false` as safe default
   - Prevents false positives (claiming medication is available when it doesn't exist)
   - Provides clear error message to help user verify medication ID

2. **Invalid Input:**
   - Returns error with `available=false` as safe default
   - Validates medication_id is not empty
   - Validates quantity is non-negative if provided

3. **Database Errors:**
   - Returns error with `available=false` as safe default
   - Logs full error traceback for debugging
   - Ensures system errors don't result in false availability claims

4. **Safe Default Principle:**
   - **Always returns `available=false` on errors** - This is a critical safety feature
   - Prevents false positives that could mislead users
   - Ensures conservative behavior when information is uncertain

### Additional Notes

- **Safety First:** The tool always defaults to `available=false` when errors occur. This prevents false positives and ensures users are not misled about medication availability.

- **Quantity Checking:** When a quantity is provided, the tool calculates `sufficient_quantity` by comparing `quantity_in_stock >= requested_quantity`. If quantity is not provided, `sufficient_quantity` is always `true` (since no specific requirement exists).

- **Performance:** The tool uses module-level caching for DatabaseManager to improve performance and reduce token usage. The database is loaded once and reused for all tool calls.

- **Date Format:** The `last_restocked` field is returned in ISO 8601 format (e.g., "2024-01-15T10:30:00Z").

- **Medication Name:** The tool returns the medication name (preferring Hebrew name if available, otherwise English name) for display purposes, making it easier for the agent to provide user-friendly responses.

---

## Tool 3: check_prescription_requirement

### Name and Purpose

**Tool Name:** `check_prescription_requirement`

**Purpose:**
Checks prescription requirement for a medication by ID. This tool enables the AI agent to verify whether medications require prescriptions when users ask about prescription requirements. It provides essential information for compliance with pharmacy regulations and helps customers understand what they need before attempting to purchase medications. Returns prescription requirement information including whether a prescription is required and the prescription type (not_required or prescription_required). Uses safe fallback values (requires_prescription=True) when medication is not found or errors occur to ensure safety.

### OpenAI Function Schema

```json
{
  "type": "function",
  "function": {
    "name": "check_prescription_requirement",
    "description": "Check prescription requirement for a medication by ID. This tool enables the AI agent to verify whether medications require prescriptions when users ask about prescription requirements. It provides essential information for compliance with pharmacy regulations and helps customers understand what they need before attempting to purchase medications. Returns prescription requirement information including whether a prescription is required and the prescription type (not_required or prescription_required). Uses safe fallback values (requires_prescription=True) when medication is not found or errors occur to ensure safety.",
    "parameters": {
      "type": "object",
      "properties": {
        "medication_id": {
          "type": "string",
          "description": "The unique identifier of the medication to check prescription requirements for. This is typically obtained from a previous medication search. Example: 'med_001'"
        }
      },
      "required": ["medication_id"]
    }
  }
}
```

### Input Schema

The tool accepts the following parameters in JSON format:

```json
{
  "type": "object",
  "properties": {
    "medication_id": {
      "type": "string",
      "description": "The unique identifier of the medication to check prescription requirements for. This is typically obtained from a previous medication search. Example: 'med_001'",
      "required": true
    }
  },
  "required": ["medication_id"]
}
```

### Parameter Details

- **medication_id** (string, required):
  - The unique identifier of the medication to check prescription requirements for
  - Typically obtained from a previous medication search (e.g., from `get_medication_by_name`)
  - Example: "med_001", "med_002"

### Output Schema

The tool returns a dictionary containing either a success result or an error result.

### Success Response Schema

When medication is found and prescription information is retrieved, returns `PrescriptionCheckResult`:

```json
{
  "type": "object",
  "properties": {
    "medication_id": {
      "type": "string",
      "description": "Unique identifier for the medication"
    },
    "medication_name": {
      "type": "string",
      "description": "Name of the medication (for display purposes)"
    },
    "requires_prescription": {
      "type": "boolean",
      "description": "Whether a prescription is required to purchase this medication"
    },
    "prescription_type": {
      "type": "string",
      "enum": ["not_required", "prescription_required"],
      "description": "Type of prescription requirement: 'not_required' for over-the-counter medications, 'prescription_required' for medications that need a prescription"
    }
  },
  "required": ["medication_id", "medication_name", "requires_prescription", "prescription_type"]
}
```

### Error Response Schema

When medication is not found or an error occurs, returns `PrescriptionCheckError`:

```json
{
  "type": "object",
  "properties": {
    "error": {
      "type": "string",
      "description": "Error message describing why the prescription check failed"
    },
    "medication_id": {
      "type": "string",
      "description": "The medication ID that was searched for"
    },
    "requires_prescription": {
      "type": "boolean",
      "description": "Fallback prescription requirement status (always True for errors, safe default)"
    },
    "prescription_type": {
      "type": "string",
      "enum": ["not_required", "prescription_required"],
      "description": "Fallback prescription type (always prescription_required for errors, safe default)"
    }
  },
  "required": ["error", "medication_id", "requires_prescription", "prescription_type"]
}
```

### Example Request

#### Example 1: Check Prescription Requirement
```json
{
  "medication_id": "med_001"
}
```

#### Example 2: Check Another Medication
```json
{
  "medication_id": "med_003"
}
```

### Example Response

#### Success Response Example (No Prescription Required)

```json
{
  "medication_id": "med_001",
  "medication_name": "אקמול",
  "requires_prescription": false,
  "prescription_type": "not_required"
}
```

#### Success Response Example (Prescription Required)

```json
{
  "medication_id": "med_003",
  "medication_name": "Amoxicillin",
  "requires_prescription": true,
  "prescription_type": "prescription_required"
}
```

#### Error Response Example (Medication Not Found)

```json
{
  "error": "Medication not found: med_999. Please verify the medication ID.",
  "medication_id": "med_999",
  "requires_prescription": true,
  "prescription_type": "prescription_required"
}
```

#### Error Response Example (Invalid Input)

```json
{
  "error": "Medication ID cannot be empty",
  "medication_id": "",
  "requires_prescription": true,
  "prescription_type": "prescription_required"
}
```

#### Error Response Example (Database Error)

```json
{
  "error": "An error occurred while checking prescription requirement: Database connection failed",
  "medication_id": "med_001",
  "requires_prescription": true,
  "prescription_type": "prescription_required"
}
```

### Error Handling

The tool handles the following error scenarios:

#### 1. Medication Not Found (404 equivalent)
- **Error Code:** Not explicitly numbered, but represents a "not found" scenario
- **Error Message:** `"Medication not found: {medication_id}. Please verify the medication ID."`
- **Response:** Returns `PrescriptionCheckError` with:
  - `error`: Error message
  - `medication_id`: The medication ID that was searched
  - `requires_prescription`: `true` (safe default)
  - `prescription_type`: `"prescription_required"` (safe default)
- **Fallback Behavior:** Returns `requires_prescription=true` and `prescription_type="prescription_required"` as safe defaults

#### 2. Invalid Parameters (400 equivalent)
- **Error Code:** Not explicitly numbered, but represents a "bad request" scenario
- **Error Message:** `"Medication ID cannot be empty"` - if medication_id is empty
- **Response:** Returns `PrescriptionCheckError` with:
  - `error`: Validation error message
  - `medication_id`: The invalid medication ID (or empty string)
  - `requires_prescription`: `true` (safe default)
  - `prescription_type`: `"prescription_required"` (safe default)
- **Fallback Behavior:** Returns `requires_prescription=true` and `prescription_type="prescription_required"` as safe defaults

#### 3. Database Error (500 equivalent)
- **Error Code:** Not explicitly numbered, but represents a "server error" scenario
- **Error Message:** `"An error occurred while checking prescription requirement: {error_message}"`
- **Response:** Returns `PrescriptionCheckError` with:
  - `error`: Error message describing the system error
  - `medication_id`: The medication ID that was being checked (or empty string)
  - `requires_prescription`: `true` (safe default)
  - `prescription_type`: `"prescription_required"` (safe default)
- **Fallback Behavior:** Returns `requires_prescription=true` and `prescription_type="prescription_required"` as safe defaults, logs full traceback

### Fallback Behavior

The tool implements the following fallback behaviors:

1. **Medication Not Found:**
   - Returns error with `requires_prescription=true` and `prescription_type="prescription_required"` as safe defaults
   - **Safety Principle:** When in doubt, require a prescription
   - Prevents illegal sales by defaulting to requiring a prescription when medication information is uncertain
   - Provides clear error message to help user verify medication ID

2. **Invalid Input:**
   - Returns error with `requires_prescription=true` and `prescription_type="prescription_required"` as safe defaults
   - Validates medication_id is not empty
   - Ensures safety by defaulting to requiring a prescription when input is invalid

3. **Database Errors:**
   - Returns error with `requires_prescription=true` and `prescription_type="prescription_required"` as safe defaults
   - Logs full error traceback for debugging
   - Ensures system errors don't result in unsafe medication sales

4. **Safe Default Principle:**
   - **Always returns `requires_prescription=true` on errors** - This is a critical safety feature
   - **Always returns `prescription_type="prescription_required"` on errors** - Ensures compliance
   - Prevents illegal sales by defaulting to requiring a prescription when information is uncertain
   - Ensures safety by defaulting to requiring a prescription when information is uncertain

### Additional Notes

- **Safety First:** The tool always defaults to `requires_prescription=true` and `prescription_type="prescription_required"` when errors occur. This is a critical safety feature that prevents illegal medication sales and ensures compliance with pharmacy regulations.

- **Prescription Types:**
  - `"not_required"`: Over-the-counter medications that can be purchased without a prescription
  - `"prescription_required"`: Medications that require a valid prescription from a healthcare professional

- **Compliance:** The safe fallback behavior ensures compliance with pharmacy regulations by defaulting to requiring a prescription when medication information is uncertain. This prevents accidental illegal sales.

- **Performance:** The tool uses module-level caching for DatabaseManager to improve performance and reduce token usage. The database is loaded once and reused for all tool calls.

- **Medication Name:** The tool returns the medication name (preferring Hebrew name if available, otherwise English name) for display purposes, making it easier for the agent to provide user-friendly responses.

- **Error Handling Philosophy:** The tool follows a "safety first" approach - when in doubt, require a prescription. This ensures patient safety and regulatory compliance.

---

## Tool 4: get_user_by_name_or_email

### Purpose
Search for a user by name or email address with case-insensitive partial matching support. Enables users to identify themselves naturally without requiring technical user IDs.

### OpenAI Function Schema

```json
{
  "type": "function",
  "function": {
    "name": "get_user_by_name_or_email",
    "description": "Search for a user by name or email address with case-insensitive partial matching support. This tool enables the AI agent to find users when they provide their name or email address instead of user_id. It supports natural language queries where users identify themselves by name or email, which is more user-friendly than requiring technical IDs. Returns user information including user_id (required for other user tools), name, email, and list of prescription IDs. If multiple users match, returns the first match. If no user is found, returns error with suggestions of similar names or emails.",
    "parameters": {
      "type": "object",
      "properties": {
        "name_or_email": {
          "type": "string",
          "description": "The user name or email address to search for. Supports partial matches and case-insensitive search. Examples: 'John Doe', 'john.doe@example.com', 'john'"
        }
      },
      "required": ["name_or_email"]
    }
  }
}
```

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name_or_email` | string | Yes | The user name or email address to search for |

### Success Response

**Status:** 200 OK

**Schema:**
```json
{
  "user_id": "string",
  "name": "string",
  "email": "string",
  "prescriptions": ["string"]
}
```

### Error Response

**Status:** Error (but returns structured error)

**Schema:**
```json
{
  "error": "string",
  "searched_name_or_email": "string",
  "suggestions": ["string"]
}
```

**Notes:**
- **Case-Insensitive**: Search works regardless of case
- **Partial Matching**: Supports partial name/email matches
- **Multiple Results**: If multiple users match, returns first match
- **Suggestions**: Error response includes suggestions for similar names/emails

---

## Tool 5: get_user_prescriptions

### Purpose
Get all prescriptions for a specific user by user_id. Returns complete prescription information including medication names, dates, quantities, refills, and status.

### OpenAI Function Schema

```json
{
  "type": "function",
  "function": {
    "name": "get_user_prescriptions",
    "description": "Get all prescriptions for a specific user by user_id. This tool enables the AI agent to retrieve all prescriptions associated with a user. This allows users to view their prescription history and verify prescription details. Returns complete prescription information including medication names (Hebrew and English), prescription dates, expiry dates, quantities, refills remaining, and status. Returns empty list if user has no prescriptions (this is not an error). The user_id is typically obtained from get_user_by_name_or_email.",
    "parameters": {
      "type": "object",
      "properties": {
        "user_id": {
          "type": "string",
          "description": "The unique identifier of the user to get prescriptions for. This is typically obtained from get_user_by_name_or_email. Example: 'user_001'"
        }
      },
      "required": ["user_id"]
    }
  }
}
```

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | The unique identifier of the user to get prescriptions for |

### Success Response

**Status:** 200 OK

**Schema:**
```json
{
  "user_id": "string",
  "user_name": "string",
  "prescriptions": [
    {
      "prescription_id": "string",
      "medication_id": "string",
      "medication_name_he": "string",
      "medication_name_en": "string",
      "prescribed_by": "string",
      "prescription_date": "string",
      "expiry_date": "string",
      "quantity": number,
      "refills_remaining": number,
      "status": "string"
    }
  ]
}
```

### Error Response

**Status:** Error (but returns structured error)

**Schema:**
```json
{
  "error": "string",
  "success": false
}
```

**Notes:**
- **Empty List**: If user has no prescriptions, returns empty list (not an error)
- **Medication Names**: Includes both Hebrew and English medication names
- **Status Values**: "active", "expired", "cancelled", or "completed"

---

## Tool 6: check_user_prescription_for_medication

### Purpose
Check if a user has an active prescription for a specific medication. Only returns active prescriptions (status="active").

### OpenAI Function Schema

```json
{
  "type": "function",
  "function": {
    "name": "check_user_prescription_for_medication",
    "description": "Check if a user has an active prescription for a specific medication. This tool enables the AI agent to verify whether a user has an active prescription for a specific medication. This is essential for prescription validation before medication purchases and helps users understand their prescription status. Only returns active prescriptions (status='active'). Returns has_active_prescription=false if no active prescription found (this is not an error). The user_id is typically obtained from get_user_by_name_or_email, and medication_id is typically obtained from get_medication_by_name.",
    "parameters": {
      "type": "object",
      "properties": {
        "user_id": {
          "type": "string",
          "description": "The unique identifier of the user to check prescription for. This is typically obtained from get_user_by_name_or_email. Example: 'user_001'"
        },
        "medication_id": {
          "type": "string",
          "description": "The unique identifier of the medication to check prescription for. This is typically obtained from get_medication_by_name. Example: 'med_001'"
        }
      },
      "required": ["user_id", "medication_id"]
    }
  }
}
```

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | The unique identifier of the user to check prescription for |
| `medication_id` | string | Yes | The unique identifier of the medication to check prescription for |

### Success Response (Active Prescription Found)

**Status:** 200 OK

**Schema:**
```json
{
  "has_active_prescription": true,
  "prescription_details": {
    "prescription_id": "string",
    "medication_id": "string",
    "medication_name_he": "string",
    "medication_name_en": "string",
    "prescribed_by": "string",
    "prescription_date": "string",
    "expiry_date": "string",
    "quantity": number,
    "refills_remaining": number,
    "status": "active"
  }
}
```

### Success Response (No Active Prescription)

**Status:** 200 OK

**Schema:**
```json
{
  "has_active_prescription": false,
  "prescription_details": null
}
```

### Error Response

**Status:** Error (but returns structured error)

**Schema:**
```json
{
  "error": "string",
  "success": false
}
```

**Notes:**
- **Active Only**: Only returns prescriptions with status="active"
- **No Prescription**: Returns has_active_prescription=false if no active prescription (not an error)
- **Both Required**: Both user_id and medication_id are required

---

## Common Patterns

### Tool Execution Flow

1. **Input Validation**: Validate and normalize input parameters
2. **Database Lookup**: Query database using DatabaseManager
3. **Result Building**: Build success or error result
4. **Response**: Return structured response dictionary

### Error Handling

All tools follow consistent error handling:

1. **Validation Errors**: Return error with clear message
2. **Not Found Errors**: Return error with safe fallback values
3. **Unexpected Errors**: Log error and return safe fallback

### Safe Fallback Values

| Tool | Fallback Value | Reason |
|------|----------------|--------|
| `check_stock_availability` | `available=false` | Safe default - assume not available |
| `check_prescription_requirement` | `requires_prescription=true` | Safety first - require prescription when uncertain |

---

## Integration with OpenAI

### Using StreamingAgent

The recommended way to use tools is through the `StreamingAgent` class, which handles tool calling automatically:

```python
from app.agent import StreamingAgent

# Initialize the agent (automatically loads tools)
agent = StreamingAgent(model="gpt-5")

# Stream response - agent will call tools automatically when needed
user_message = "Tell me about Acamol and check if it's in stock"
for chunk in agent.stream_response(user_message):
    print(chunk, end="", flush=True)
```

The `StreamingAgent` automatically:
- Registers all available tools with OpenAI
- Handles tool calls during streaming
- **Executes independent tools in parallel** using ThreadPoolExecutor for improved performance
- Preserves tool call order in results (maintains OpenAI API expected order)
- Isolates errors (one tool's failure doesn't prevent others from completing)
- Executes tools and feeds results back to the model
- Continues streaming with tool results

**Performance Note:** When multiple independent tools are requested simultaneously, they execute in parallel, reducing total execution time. For example, if 3 tools each take 300ms sequentially (900ms total), parallel execution reduces this to approximately 600ms (~33% improvement).

### Registering Tools Manually

If you need to register tools manually (for custom implementations):

```python
from app.tools.registry import get_tools_for_openai
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
tools = get_tools_for_openai()

response = client.chat.completions.create(
    model="gpt-5",
    messages=[...],
    tools=tools,
    stream=True  # Enable streaming
)
```

### Executing Tool Calls Manually

```python
from app.tools.registry import execute_tool

# When OpenAI requests a tool call
tool_call = response.choices[0].message.tool_calls[0]
result = execute_tool(
    tool_call.function.name,
    json.loads(tool_call.function.arguments)
)
```

---

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

## Input/Output Models (Pydantic)

All tools use Pydantic models for type-safe input/output validation:

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

#### `PrescriptionCheckInput` (User Prescription)
- `user_id` (str, required): User ID to check prescription for
- `medication_id` (str, required): Medication ID to check prescription for

#### `PrescriptionCheckResult` (User Prescription)
- `has_active_prescription` (bool): Whether user has active prescription
- `prescription_details` (Optional[PrescriptionInfo]): Prescription details if active prescription exists, None otherwise

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

## Best Practices

1. **Always validate inputs**: Use helper functions for validation
2. **Use safe fallbacks**: Default to safe values on errors
3. **Log appropriately**: Use correct log levels (DEBUG, INFO, WARNING, ERROR)
4. **Return structured errors**: Always return consistent error format
5. **Handle edge cases**: Consider all possible failure modes
6. **Document thoroughly**: Follow core-python-standards for documentation



