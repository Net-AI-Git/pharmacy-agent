# Flow 1: Stock Availability Check

## Overview

This flow handles user queries about medication stock availability. It is a basic and quick flow that allows users to check if a specific medication is available in sufficient quantity before visiting the pharmacy.

**Purpose:** To provide users with accurate information about medication stock availability, including available quantity.

## Sequence

### Step 1: User Query
The user asks about medication stock availability.

**Example queries in Hebrew:**
- "האם יש לכם אקמול במלאי?" (Do you have Acamol in stock?)
- "כמה יחידות של פרצטמול יש לכם?" (How many units of Paracetamol do you have?)
- "אקמול זמין?" (Is Acamol available?)
- "האם אקמול קיים במלאי?" (Is Acamol in stock?)
- "יש לכם מלאי של אקמול?" (Do you have stock of Acamol?)

**Example queries in English:**
- "Do you have Acetaminophen in stock?"
- "How many units of Paracetamol do you have?"
- "Is Acamol available?"
- "Is Acetaminophen in stock?"
- "Do you stock Paracetamol?"

### Step 2: Search Medication by Name
The agent identifies that the user is asking about availability and performs a medication search by name.

**Tool Call:**
```json
{
  "function": "get_medication_by_name",
  "arguments": {
    "name": "אקמול",
    "language": null
  }
}
```

**Possible Response:**
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

**Error Handling:**
- If medication is not found, the agent receives `MedicationSearchError` with suggestions for similar medications
- The agent displays the error and suggestions to the user

### Step 3: Check Stock Availability
After finding the medication, the agent checks stock availability.

**Tool Call:**
```json
{
  "function": "check_stock_availability",
  "arguments": {
    "medication_id": "med_001",
    "quantity": null
  }
}
```

**Possible Response:**
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

**Error Handling:**
- If medication is not found in the database, the agent receives `StockCheckError` with `available: false`
- The agent displays a message to the user that the medication was not found

### Step 4: Response to User
The agent summarizes the information and provides a clear response to the user.

**Response in Hebrew (medication available):**
```
אקמול זמין במלאי. יש לנו 150 יחידות.
המלאי עודכן לאחרונה ב-15 בינואר 2024.
```

**Response in Hebrew (medication not available):**
```
אקמול לא זמין כרגע במלאי. המלאי הנוכחי הוא 0 יחידות.
אנא פנה לבית המרקחת לבדיקת מועד אספקה מחדש.
```

**Response in English (medication available):**
```
Acetaminophen is available in stock. We have 150 units.
The stock was last restocked on January 15, 2024.
```

**Response in English (medication not available):**
```
Acetaminophen is not currently available in stock. Current stock is 0 units.
Please contact the pharmacy to check when it will be restocked.
```

## Trigger Phrases

The agent identifies this flow based on the following phrases:

**Hebrew:**
- "יש לכם" + medication name (Do you have)
- "במלאי" (in stock)
- "זמין" (available)
- "כמה יחידות" (how many units)
- "קיים במלאי" (exists in stock)
- "מלאי של" (stock of)

**English:**
- "in stock"
- "available"
- "do you have"
- "how many units"
- "stock of"

## Edge Cases

### 1. Medication Not Found
**Scenario:** User asks about a medication that doesn't exist in the database.

**Handling:**
1. `get_medication_by_name` returns `MedicationSearchError` with suggestions
2. Agent displays to user: "התרופה [name] לא נמצאה. האם התכוונת לאחת מהתרופות הבאות: [list of suggestions]?" (Medication [name] not found. Did you mean one of the following medications: [list of suggestions]?)

### 2. Multiple Results (Fuzzy Matching)
**Scenario:** Search returns multiple similar medications.

**Handling:**
1. `get_medication_by_name` returns the first medication (closest match)
2. Agent can display to user: "מצאתי את התרופה [name]. האם זו התרופה שביקשת?" (I found medication [name]. Is this the medication you requested?)

### 3. Specific Quantity
**Scenario:** User asks about a specific quantity (e.g., "Do you have 20 units of Acamol?").

**Handling:**
1. Agent identifies the quantity from the query
2. `check_stock_availability` is called with `quantity: 20`
3. Response includes information about whether sufficient units are available: "כן, יש לנו 150 יחידות, מספיק עבור 20 יחידות שביקשת." (Yes, we have 150 units, sufficient for the 20 units you requested.)

### 4. Database Error
**Scenario:** Technical error in the database.

**Handling:**
1. Tool returns error with fallback values
2. Agent displays to user: "מצטער, אירעה שגיאה בבדיקת המלאי. אנא נסה שוב מאוחר יותר או פנה לבית המרקחת." (Sorry, an error occurred while checking stock. Please try again later or contact the pharmacy.)

## Flow Diagram

```
User Query
    ↓
[Agent analyzes query]
    ↓
get_medication_by_name(name)
    ↓
    ├─→ Medication found → check_stock_availability(medication_id)
    │                          ↓
    │                      Stock info retrieved
    │                          ↓
    │                      Agent responds with availability
    │
    └─→ Medication not found → Agent responds with error + suggestions
```

## Complete Conversation Examples

### Example 1: Medication Available (Hebrew)

**User:** "האם יש לכם אקמול במלאי?" (Do you have Acamol in stock?)

**Agent Tool Calls:**
1. `get_medication_by_name(name="אקמול")` → `medication_id: "med_001"`
2. `check_stock_availability(medication_id="med_001")` → `available: true, quantity: 150`

**Agent Response:**
"אקמול זמין במלאי. יש לנו 150 יחידות במלאי. המלאי עודכן לאחרונה ב-15 בינואר 2024." (Acamol is available in stock. We have 150 units in stock. Stock was last updated on January 15, 2024.)

### Example 2: Medication Not Available (English)

**User:** "Do you have Aspirin in stock?"

**Agent Tool Calls:**
1. `get_medication_by_name(name="Aspirin")` → `medication_id: "med_002"`
2. `check_stock_availability(medication_id="med_002")` → `available: false, quantity: 0`

**Agent Response:**
"Aspirin is not currently available in stock. Current stock is 0 units. Please contact the pharmacy to check when it will be restocked."

### Example 3: Specific Quantity (Hebrew)

**User:** "יש לכם 50 יחידות של פרצטמול?" (Do you have 50 units of Paracetamol?)

**Agent Tool Calls:**
1. `get_medication_by_name(name="פרצטמול")` → `medication_id: "med_001"`
2. `check_stock_availability(medication_id="med_001", quantity=50)` → `available: true, quantity: 150, sufficient_quantity: true`

**Agent Response:**
"כן, פרצטמול זמין במלאי. יש לנו 150 יחידות, מספיק עבור 50 היחידות שביקשת." (Yes, Paracetamol is available in stock. We have 150 units, sufficient for the 50 units you requested.)

## Required Testing

For each flow, test at least 5+ variations in Hebrew and 5+ variations in English:

### Variations in Hebrew:
1. "האם יש לכם אקמול במלאי?" (Do you have Acamol in stock?)
2. "כמה יחידות של אקמול יש לכם?" (How many units of Acamol do you have?)
3. "אקמול זמין?" (Is Acamol available?)
4. "האם אקמול קיים במלאי?" (Is Acamol in stock?)
5. "יש לכם מלאי של פרצטמול?" (Do you have stock of Paracetamol?)
6. "אני צריך לבדוק אם יש אקמול במלאי" (I need to check if Acamol is in stock)
7. "מה המצב של המלאי של אקמול?" (What's the stock status of Acamol?)

### Variations in English:
1. "Do you have Acetaminophen in stock?"
2. "How many units of Paracetamol do you have?"
3. "Is Acamol available?"
4. "Is Acetaminophen in stock?"
5. "Do you stock Paracetamol?"
6. "I need to check if Acetaminophen is available"
7. "What's the stock status of Paracetamol?"

## Important Notes

1. **Stateless Agent:** Each conversation is independent, no memory between different conversations
2. **Bilingual Support:** Agent responds in the same language the user wrote in
3. **No Medical Advice:** Agent only provides availability information, does not recommend medications
4. **Safe Defaults:** In case of error, `available` is set to `false` as a safe value
