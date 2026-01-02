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

## Tool 1: get_medication_by_name

### Purpose
Search for a medication by name with fuzzy matching support. Supports both Hebrew and English names, handles partial matches, and provides helpful suggestions when no exact match is found.

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

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | The medication name to search for (case-insensitive, supports partial matches) |
| `language` | string ("he" \| "en") | No | Optional language filter. If not provided, searches both languages |

### Success Response

**Status:** 200 OK

**Schema:**
```json
{
  "medication_id": "string",
  "name_he": "string",
  "name_en": "string",
  "active_ingredients": ["string"],
  "dosage_forms": ["string"],
  "dosage_instructions": "string",
  "usage_instructions": "string",
  "description": "string"
}
```

**Note:** This tool does NOT return `requires_prescription`, `available`, or `quantity_in_stock`. For prescription information, use `check_prescription_requirement(medication_id)`. For stock information, use `check_stock_availability(medication_id)`.

**Example:**
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

### Error Response

**Status:** 404 Not Found

**Schema:**
```json
{
  "error": "string",
  "searched_name": "string",
  "suggestions": ["string"]
}
```

**Example:**
```json
{
  "error": "Medication 'InvalidMed' not found. Please check the spelling or try a different name.",
  "searched_name": "InvalidMed",
  "suggestions": ["Acamol", "Advil", "Aspirin"]
}
```

### Example Requests

**Request 1: Search in Hebrew**
```python
{
  "name": "אקמול",
  "language": "he"
}
```

**Request 2: Search in English**
```python
{
  "name": "Acetaminophen",
  "language": "en"
}
```

**Request 3: Search both languages (fuzzy match)**
```python
{
  "name": "acam"
}
```

### Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| 400 | Invalid parameters (empty name) | Provide a non-empty medication name |
| 404 | Medication not found | Check spelling or try suggested alternatives |
| 500 | Internal server error | Check logs for details |

### Notes

- **Fuzzy Matching**: Partial matches are supported (e.g., "acam" will find "Acamol")
- **Case Insensitive**: Search is case-insensitive
- **Required Fields**: Response always includes `active_ingredients` and `dosage_instructions` (required fields)
- **Suggestions**: Error responses include up to 5 suggested medication names

---

## Tool 2: check_stock_availability

### Purpose
Check stock availability for a medication by ID. Verifies if medications are in stock, how many units are available, and whether there is sufficient quantity for a specific request.

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

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `medication_id` | string | Yes | The unique identifier of the medication to check |
| `quantity` | integer | No | Optional quantity to check availability for. Must be positive if provided |

### Success Response

**Status:** 200 OK

**Schema:**
```json
{
  "medication_id": "string",
  "medication_name": "string",
  "available": boolean,
  "quantity_in_stock": integer,
  "last_restocked": "string",
  "sufficient_quantity": boolean,
  "requested_quantity": integer | null
}
```

**Example:**
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

### Error Response

**Status:** 404 Not Found

**Schema:**
```json
{
  "error": "string",
  "medication_id": "string",
  "available": false
}
```

**Example:**
```json
{
  "error": "Medication not found: med_999. Please verify the medication ID.",
  "medication_id": "med_999",
  "available": false
}
```

### Example Requests

**Request 1: Check general availability**
```python
{
  "medication_id": "med_001"
}
```

**Request 2: Check specific quantity**
```python
{
  "medication_id": "med_001",
  "quantity": 10
}
```

**Request 3: Check large quantity**
```python
{
  "medication_id": "med_001",
  "quantity": 200
}
```

### Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| 400 | Invalid parameters (empty medication_id or negative quantity) | Provide valid medication_id and non-negative quantity |
| 404 | Medication not found | Verify the medication_id is correct |
| 500 | Internal server error | Check logs for details |

### Notes

- **Safe Fallback**: On errors, always returns `available=false` (safe default)
- **Quantity Check**: If quantity is provided, `sufficient_quantity` indicates if stock is adequate
- **Date Format**: `last_restocked` is in ISO 8601 format

---

## Tool 3: check_prescription_requirement

### Purpose
Check prescription requirement for a medication by ID. Verifies whether medications require prescriptions, providing essential information for compliance with pharmacy regulations.

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

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `medication_id` | string | Yes | The unique identifier of the medication to check |

### Success Response (No Prescription Required)

**Status:** 200 OK

**Schema:**
```json
{
  "medication_id": "string",
  "medication_name": "string",
  "requires_prescription": boolean,
  "prescription_type": "not_required" | "prescription_required"
}
```

**Example:**
```json
{
  "medication_id": "med_001",
  "medication_name": "אקמול",
  "requires_prescription": false,
  "prescription_type": "not_required"
}
```

### Success Response (Prescription Required)

**Example:**
```json
{
  "medication_id": "med_003",
  "medication_name": "Amoxicillin",
  "requires_prescription": true,
  "prescription_type": "prescription_required"
}
```

### Error Response

**Status:** 404 Not Found

**Schema:**
```json
{
  "error": "string",
  "medication_id": "string",
  "requires_prescription": true,
  "prescription_type": "prescription_required"
}
```

**Example:**
```json
{
  "error": "Medication not found: med_999. Please verify the medication ID.",
  "medication_id": "med_999",
  "requires_prescription": true,
  "prescription_type": "prescription_required"
}
```

### Example Requests

**Request 1: Check prescription requirement**
```python
{
  "medication_id": "med_001"
}
```

**Request 2: Check for prescription medication**
```python
{
  "medication_id": "med_003"
}
```

### Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| 400 | Invalid parameters (empty medication_id) | Provide a non-empty medication_id |
| 404 | Medication not found | Verify the medication_id is correct |
| 500 | Internal server error | Check logs for details |

### Notes

- **Safety First**: On errors, always returns `requires_prescription=true` and `prescription_type="prescription_required"` (safe default)
- **Prescription Types**: 
  - `"not_required"`: Over-the-counter medication
  - `"prescription_required"`: Requires doctor's prescription
- **Compliance**: This tool is critical for pharmacy regulatory compliance

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

## Best Practices

1. **Always validate inputs**: Check parameters before processing
2. **Use safe fallbacks**: Default to safe values on errors
3. **Log appropriately**: Use correct log levels (DEBUG, INFO, WARNING, ERROR)
4. **Return structured errors**: Always return consistent error format
5. **Handle edge cases**: Consider all possible failure modes
6. **Document thoroughly**: Follow core-python-standards for documentation



