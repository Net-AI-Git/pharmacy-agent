# check_stock_availability

## Name and Purpose

**Tool Name:** `check_stock_availability`

**Purpose:**
Checks stock availability for a medication by ID. This tool enables the AI agent to check medication stock availability when users ask about inventory. It verifies if medications are in stock, how many units are available, and whether there is sufficient quantity for a specific request. Returns complete stock information including availability status, quantity in stock, last restocked date, and whether sufficient quantity is available for the requested amount.

## Input Schema

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

## Output Schema

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

## Example Request

### Example 1: Check General Availability
```json
{
  "medication_id": "med_001"
}
```

### Example 2: Check Specific Quantity
```json
{
  "medication_id": "med_001",
  "quantity": 10
}
```

### Example 3: Check Large Quantity
```json
{
  "medication_id": "med_001",
  "quantity": 200
}
```

## Example Response

### Success Response Example (Available)

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

### Success Response Example (Insufficient Quantity)

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

### Success Response Example (Out of Stock)

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

### Success Response Example (No Quantity Requested)

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

### Error Response Example (Medication Not Found)

```json
{
  "error": "Medication not found: med_999. Please verify the medication ID.",
  "medication_id": "med_999",
  "available": false
}
```

### Error Response Example (Invalid Input)

```json
{
  "error": "Medication ID cannot be empty",
  "medication_id": "",
  "available": false
}
```

### Error Response Example (Invalid Quantity)

```json
{
  "error": "Quantity cannot be negative",
  "medication_id": "med_001",
  "available": false
}
```

## Error Handling

The tool handles the following error scenarios:

### 1. Medication Not Found (404 equivalent)
- **Error Code:** Not explicitly numbered, but represents a "not found" scenario
- **Error Message:** `"Medication not found: {medication_id}. Please verify the medication ID."`
- **Response:** Returns `StockCheckError` with:
  - `error`: Error message
  - `medication_id`: The medication ID that was searched
  - `available`: `false` (safe default)
- **Fallback Behavior:** Returns `available=false` as safe default

### 2. Invalid Parameters (400 equivalent)
- **Error Code:** Not explicitly numbered, but represents a "bad request" scenario
- **Error Messages:**
  - `"Medication ID cannot be empty"` - if medication_id is empty
  - `"Quantity cannot be negative"` - if quantity is negative
- **Response:** Returns `StockCheckError` with:
  - `error`: Validation error message
  - `medication_id`: The invalid medication ID (or empty string)
  - `available`: `false` (safe default)
- **Fallback Behavior:** Returns `available=false` as safe default

### 3. Database Error (500 equivalent)
- **Error Code:** Not explicitly numbered, but represents a "server error" scenario
- **Error Message:** `"An error occurred while checking stock: {error_message}"`
- **Response:** Returns `StockCheckError` with:
  - `error`: Error message describing the system error
  - `medication_id`: The medication ID that was being checked (or empty string)
  - `available`: `false` (safe default)
- **Fallback Behavior:** Returns `available=false` as safe default, logs full traceback

## Fallback Behavior

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

## Additional Notes

- **Safety First:** The tool always defaults to `available=false` when errors occur. This prevents false positives and ensures users are not misled about medication availability.

- **Quantity Checking:** When a quantity is provided, the tool calculates `sufficient_quantity` by comparing `quantity_in_stock >= requested_quantity`. If quantity is not provided, `sufficient_quantity` is always `true` (since no specific requirement exists).

- **Performance:** The tool uses module-level caching for DatabaseManager to improve performance and reduce token usage. The database is loaded once and reused for all tool calls.

- **Date Format:** The `last_restocked` field is returned in ISO 8601 format (e.g., "2024-01-15T10:30:00Z").

- **Medication Name:** The tool returns the medication name (preferring Hebrew name if available, otherwise English name) for display purposes, making it easier for the agent to provide user-friendly responses.

