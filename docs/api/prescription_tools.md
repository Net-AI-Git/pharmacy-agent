# check_prescription_requirement

## Name and Purpose

**Tool Name:** `check_prescription_requirement`

**Purpose:**
Checks prescription requirement for a medication by ID. This tool enables the AI agent to verify whether medications require prescriptions when users ask about prescription requirements. It provides essential information for compliance with pharmacy regulations and helps customers understand what they need before attempting to purchase medications. Returns prescription requirement information including whether a prescription is required and the prescription type (not_required or prescription_required). Uses safe fallback values (requires_prescription=True) when medication is not found or errors occur to ensure safety.

## Input Schema

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

## Output Schema

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

## Example Request

### Example 1: Check Prescription Requirement
```json
{
  "medication_id": "med_001"
}
```

### Example 2: Check Another Medication
```json
{
  "medication_id": "med_003"
}
```

## Example Response

### Success Response Example (No Prescription Required)

```json
{
  "medication_id": "med_001",
  "medication_name": "אקמול",
  "requires_prescription": false,
  "prescription_type": "not_required"
}
```

### Success Response Example (Prescription Required)

```json
{
  "medication_id": "med_003",
  "medication_name": "Amoxicillin",
  "requires_prescription": true,
  "prescription_type": "prescription_required"
}
```

### Error Response Example (Medication Not Found)

```json
{
  "error": "Medication not found: med_999. Please verify the medication ID.",
  "medication_id": "med_999",
  "requires_prescription": true,
  "prescription_type": "prescription_required"
}
```

### Error Response Example (Invalid Input)

```json
{
  "error": "Medication ID cannot be empty",
  "medication_id": "",
  "requires_prescription": true,
  "prescription_type": "prescription_required"
}
```

### Error Response Example (Database Error)

```json
{
  "error": "An error occurred while checking prescription requirement: Database connection failed",
  "medication_id": "med_001",
  "requires_prescription": true,
  "prescription_type": "prescription_required"
}
```

## Error Handling

The tool handles the following error scenarios:

### 1. Medication Not Found (404 equivalent)
- **Error Code:** Not explicitly numbered, but represents a "not found" scenario
- **Error Message:** `"Medication not found: {medication_id}. Please verify the medication ID."`
- **Response:** Returns `PrescriptionCheckError` with:
  - `error`: Error message
  - `medication_id`: The medication ID that was searched
  - `requires_prescription`: `true` (safe default)
  - `prescription_type`: `"prescription_required"` (safe default)
- **Fallback Behavior:** Returns `requires_prescription=true` and `prescription_type="prescription_required"` as safe defaults

### 2. Invalid Parameters (400 equivalent)
- **Error Code:** Not explicitly numbered, but represents a "bad request" scenario
- **Error Message:** `"Medication ID cannot be empty"` - if medication_id is empty
- **Response:** Returns `PrescriptionCheckError` with:
  - `error`: Validation error message
  - `medication_id`: The invalid medication ID (or empty string)
  - `requires_prescription`: `true` (safe default)
  - `prescription_type`: `"prescription_required"` (safe default)
- **Fallback Behavior:** Returns `requires_prescription=true` and `prescription_type="prescription_required"` as safe defaults

### 3. Database Error (500 equivalent)
- **Error Code:** Not explicitly numbered, but represents a "server error" scenario
- **Error Message:** `"An error occurred while checking prescription requirement: {error_message}"`
- **Response:** Returns `PrescriptionCheckError` with:
  - `error`: Error message describing the system error
  - `medication_id`: The medication ID that was being checked (or empty string)
  - `requires_prescription`: `true` (safe default)
  - `prescription_type`: `"prescription_required"` (safe default)
- **Fallback Behavior:** Returns `requires_prescription=true` and `prescription_type="prescription_required"` as safe defaults, logs full traceback

## Fallback Behavior

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

## Additional Notes

- **Safety First:** The tool always defaults to `requires_prescription=true` and `prescription_type="prescription_required"` when errors occur. This is a critical safety feature that prevents illegal medication sales and ensures compliance with pharmacy regulations.

- **Prescription Types:**
  - `"not_required"`: Over-the-counter medications that can be purchased without a prescription
  - `"prescription_required"`: Medications that require a valid prescription from a healthcare professional

- **Compliance:** The safe fallback behavior ensures compliance with pharmacy regulations by defaulting to requiring a prescription when medication information is uncertain. This prevents accidental illegal sales.

- **Performance:** The tool uses module-level caching for DatabaseManager to improve performance and reduce token usage. The database is loaded once and reused for all tool calls.

- **Medication Name:** The tool returns the medication name (preferring Hebrew name if available, otherwise English name) for display purposes, making it easier for the agent to provide user-friendly responses.

- **Error Handling Philosophy:** The tool follows a "safety first" approach - when in doubt, require a prescription. This ensures patient safety and regulatory compliance.

