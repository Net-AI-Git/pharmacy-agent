# get_medication_by_name

## Name and Purpose

**Tool Name:** `get_medication_by_name`

**Purpose:**
Searches for a medication in the database by name with fuzzy matching support. This tool enables the AI agent to find medications when users provide medication names in natural language. It supports both Hebrew and English names, handles partial matches (fuzzy matching), and provides helpful suggestions when no exact match is found. Returns basic medication information including active ingredients, dosage instructions, and description. Does NOT return stock availability or prescription requirements - use check_stock_availability and check_prescription_requirement for those.

## Input Schema

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

## Output Schema

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

## Example Request

### Example 1: Search in Hebrew
```json
{
  "name": "אקמול",
  "language": "he"
}
```

### Example 2: Search in English
```json
{
  "name": "Acetaminophen",
  "language": "en"
}
```

### Example 3: Search Both Languages (Partial Match)
```json
{
  "name": "acam"
}
```

### Example 4: Fuzzy Match
```json
{
  "name": "paracet",
  "language": "en"
}
```

## Example Response

### Success Response Example

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

### Error Response Example (Medication Not Found)

```json
{
  "error": "Medication 'InvalidMed' not found. Please check the spelling or try a different name.",
  "searched_name": "InvalidMed",
  "suggestions": ["Acamol", "Advil", "Aspirin", "Ibuprofen", "Paracetamol"]
}
```

### Error Response Example (Invalid Input)

```json
{
  "error": "Medication name cannot be empty",
  "searched_name": "",
  "suggestions": []
}
```

## Error Handling

The tool handles the following error scenarios:

### 1. Medication Not Found (404 equivalent)
- **Error Code:** Not explicitly numbered, but represents a "not found" scenario
- **Error Message:** `"Medication '{name}' not found. Please check the spelling or try a different name."`
- **Response:** Returns `MedicationSearchError` with:
  - `error`: Error message
  - `searched_name`: The original search query
  - `suggestions`: List of up to 5 suggested medication names
- **Fallback Behavior:** Provides suggestions to help user find the correct medication

### 2. Invalid Parameters (400 equivalent)
- **Error Code:** Not explicitly numbered, but represents a "bad request" scenario
- **Error Message:** `"Medication name cannot be empty"` or similar validation error
- **Response:** Returns `MedicationSearchError` with:
  - `error`: Validation error message
  - `searched_name`: The invalid input (or empty string)
  - `suggestions`: Empty list
- **Fallback Behavior:** Returns error without suggestions

### 3. Invalid Language Parameter
- **Error Code:** Not explicitly numbered, treated as warning
- **Error Message:** Logged as warning, language parameter ignored
- **Response:** Tool continues with `language=None` (searches both languages)
- **Fallback Behavior:** Ignores invalid language parameter and searches both languages

### 4. Database Error (500 equivalent)
- **Error Code:** Not explicitly numbered, but represents a "server error" scenario
- **Error Message:** `"An error occurred while searching for the medication: {error_message}"`
- **Response:** Returns `MedicationSearchError` with:
  - `error`: Error message describing the system error
  - `searched_name`: The original search query
  - `suggestions`: Empty list
- **Fallback Behavior:** Returns error without suggestions, logs full traceback

### 5. Missing Required Fields in Medication Data
- **Error Code:** Not explicitly numbered, represents data integrity issue
- **Error Message:** `"Medication data is incomplete: missing active ingredients"` or `"Medication data is incomplete: missing dosage instructions"`
- **Response:** Returns `MedicationSearchError` with:
  - `error`: Data integrity error message
  - `searched_name`: The original search query
  - `suggestions`: Empty list
- **Fallback Behavior:** Returns error indicating data incompleteness

## Fallback Behavior

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

## Additional Notes

- **Fuzzy Matching:** The tool supports partial string matching. For example, searching "Acam" will find "Acamol", and searching "paracet" will find "Paracetamol". This is implemented using case-insensitive partial string matching.

- **Multiple Results:** If multiple medications match the search query, the tool returns the first match. In a production system, you might want to return all matches and let the agent choose.

- **Performance:** The tool uses module-level caching for DatabaseManager to improve performance and reduce token usage. The database is loaded once and reused for all tool calls.

- **Required Fields:** The tool validates that all required fields (active_ingredients, dosage_instructions) are present before returning medication information. This ensures data integrity and safety.

