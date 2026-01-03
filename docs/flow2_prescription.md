# Flow 2: Prescription Requirement + Stock Check

## Overview

This flow handles user queries about prescription requirements for medications, and sometimes also checks stock availability. It is a more complex flow that combines prescription requirement checking with stock availability, providing users with comprehensive information about the medication.

**Purpose:** To provide users with information about prescription requirements for medications, and sometimes also about stock availability, so they can understand what is required of them before purchasing the medication.

## Sequence

### Step 1: User Query
The user asks about prescription requirements for a medication, and sometimes also about availability.

**Example queries in Hebrew:**
- "אני צריך אנטיביוטיקה, האם צריך מרשם?" (I need antibiotics, do I need a prescription?)
- "האם אקמול דורש מרשם רופא?" (Does Acamol require a doctor's prescription?)
- "אני רוצה לקנות פרצטמול, צריך מרשם?" (I want to buy Paracetamol, do I need a prescription?)
- "האם יש לכם אנטיביוטיקה במלאי וצריך מרשם?" (Do you have antibiotics in stock and do they require a prescription?)
- "אמוקסיצילין - צריך מרשם? וזמין במלאי?" (Amoxicillin - requires prescription? And is it in stock?)

**Example queries in English:**
- "I need antibiotics, do I need a prescription?"
- "Does Acetaminophen require a prescription?"
- "I want to buy Paracetamol, do I need a prescription?"
- "Do you have antibiotics in stock and do they require a prescription?"
- "Amoxicillin - requires prescription? And is it in stock?"

### Step 2: Search Medication by Name
The agent identifies that the user is asking about prescription requirements and performs a medication search by name.

**Tool Call:**
```json
{
  "function": "get_medication_by_name",
  "arguments": {
    "name": "אנטיביוטיקה",
    "language": null
  }
}
```

**Possible Response:**
```json
{
  "medication_id": "med_003",
  "name_he": "אמוקסיצילין",
  "name_en": "Amoxicillin",
  "active_ingredients": ["Amoxicillin 500mg"],
  "dosage_forms": ["Capsules"],
  "dosage_instructions": "500mg three times daily",
  "usage_instructions": "Take with food to reduce stomach upset",
  "description": "Antibiotic used to treat bacterial infections"
}
```

**Important Notes:**
- `get_medication_by_name` returns **basic medication information only** (names, active ingredients, dosage forms, instructions, description)
- `get_medication_by_name` **does NOT return** prescription requirement or stock availability information
- The `medication_id` from this response is **required** for calling `check_prescription_requirement` and `check_stock_availability`

**Error Handling:**
- If medication is not found, the agent receives `MedicationSearchError` with suggestions
- If there are multiple results, the agent can ask the user for clarification

### Step 3: Check Prescription Requirement
After finding the medication and obtaining the `medication_id`, the agent must call `check_prescription_requirement` to get prescription information, since `get_medication_by_name` does not return prescription data.

**Tool Call:**
```json
{
  "function": "check_prescription_requirement",
  "arguments": {
    "medication_id": "med_003"
  }
}
```

**Possible Response (prescription required):**
```json
{
  "medication_id": "med_003",
  "medication_name": "אמוקסיצילין",
  "requires_prescription": true,
  "prescription_type": "prescription_required"
}
```

**Possible Response (no prescription required):**
```json
{
  "medication_id": "med_001",
  "medication_name": "אקמול",
  "requires_prescription": false,
  "prescription_type": "not_required"
}
```

**Error Handling:**
- If medication is not found, the agent receives `PrescriptionCheckError` with `requires_prescription: true` as a safe default
- Agent displays a message to the user that the medication was not found

### Step 4: Check Stock Availability (Optional)
If the user also asked about availability, or if the agent decides it's relevant, the agent checks stock availability.

**Tool Call:**
```json
{
  "function": "check_stock_availability",
  "arguments": {
    "medication_id": "med_003",
    "quantity": null
  }
}
```

**Possible Response:**
```json
{
  "medication_id": "med_003",
  "medication_name": "אמוקסיצילין",
  "available": true,
  "quantity_in_stock": 75,
  "last_restocked": "2024-01-10T08:00:00Z",
  "sufficient_quantity": true,
  "requested_quantity": null
}
```

**Decision when to check availability:**
- If user explicitly asked about availability → always check
- If medication requires prescription → recommended to check availability to provide comprehensive information
- If medication does not require prescription → can check availability if relevant

**Important:** `check_stock_availability` must be called separately because `get_medication_by_name` does not return stock information.

### Step 5: Response to User
The agent summarizes the information and provides a comprehensive response to the user.

**Response in Hebrew (prescription required + available):**
```
אמוקסיצילין דורש מרשם רופא. התרופה זמינה במלאי - יש לנו 75 יחידות.
אנא הבא מרשם רופא תקף כדי לרכוש את התרופה.
```

**Response in Hebrew (no prescription required + available):**
```
אקמול לא דורש מרשם רופא - ניתן לרכוש ללא מרשם. התרופה זמינה במלאי - יש לנו 150 יחידות.
```

**Response in Hebrew (prescription required + not available):**
```
אמוקסיצילין דורש מרשם רופא. כרגע התרופה לא זמינה במלאי.
אנא פנה לבית המרקחת עם מרשם רופא לבדיקת מועד אספקה מחדש.
```

**Response in English (prescription required + available):**
```
Amoxicillin requires a doctor's prescription. The medication is available in stock - we have 75 units.
Please bring a valid doctor's prescription to purchase the medication.
```

**Response in English (no prescription required + available):**
```
Acetaminophen does not require a doctor's prescription - it can be purchased without a prescription. The medication is available in stock - we have 150 units.
```

## Trigger Phrases

The agent identifies this flow based on the following phrases:

**Hebrew:**
- "צריך מרשם" (need prescription)
- "דורש מרשם" (requires prescription)
- "מרשם רופא" (doctor's prescription)
- "אני צריך" + medication name + "צריך מרשם?" (I need + medication name + need prescription?)
- "אני רוצה לקנות" + medication name + "צריך מרשם?" (I want to buy + medication name + need prescription?)

**English:**
- "need prescription"
- "require prescription"
- "doctor's prescription"
- "I need" + medication name + "prescription?"
- "I want to buy" + medication name + "prescription?"

## Edge Cases

### 1. Medication Not Found
**Scenario:** User asks about a medication that doesn't exist in the database.

**Handling:**
1. `get_medication_by_name` returns `MedicationSearchError` with suggestions
2. Agent displays to user: "התרופה [name] לא נמצאה. האם התכוונת לאחת מהתרופות הבאות: [list of suggestions]?" (Medication [name] not found. Did you mean one of the following medications: [list of suggestions]?)

### 2. Multiple Results (Fuzzy Matching)
**Scenario:** Search returns multiple similar medications (e.g., "אנטיביוטיקה" can return multiple types of antibiotics).

**Handling:**
1. `get_medication_by_name` returns the first medication (closest match)
2. Agent can display to user: "מצאתי את התרופה [name]. האם זו התרופה שביקשת?" (I found medication [name]. Is this the medication you requested?)
3. If user requests clarification, agent can display all results

### 3. Combined Query (Prescription + Stock)
**Scenario:** User asks about both prescription and availability in the same query.

**Handling:**
1. Agent identifies both topics
2. Agent performs both tool calls:
   - `check_prescription_requirement`
   - `check_stock_availability`
3. Response includes both pieces of information

### 4. Safe Default - Prescription Requirement
**Scenario:** Error in checking prescription requirement.

**Handling:**
1. `check_prescription_requirement` returns `PrescriptionCheckError` with `requires_prescription: true` as a safe default
2. Agent displays to user: "מצטער, לא הצלחתי לבדוק את דרישת המרשם. אנא פנה לבית המרקחת עם מרשם רופא (כדי להיות בטוח)." (Sorry, I couldn't check the prescription requirement. Please contact the pharmacy with a doctor's prescription (to be safe).)

### 5. Medication Without Prescription But Not Available
**Scenario:** Medication does not require prescription but is not available in stock.

**Handling:**
1. Agent displays: "התרופה לא דורשת מרשם, אבל כרגע לא זמינה במלאי." (The medication does not require a prescription, but is currently not available in stock.)
2. Agent can suggest to user to check again later

## Flow Diagram

```
User Query
    ↓
[Agent analyzes query - identifies prescription + possibly stock question]
    ↓
get_medication_by_name(name)
    ↓
    ├─→ Medication found → Get medication_id + basic info (NO prescription or stock info)
    │                          ↓
    │                      check_prescription_requirement(medication_id)
    │                          ↓
    │                      Prescription info retrieved
    │                          ↓
    │                      [If stock question or relevant] → check_stock_availability(medication_id)
    │                                                          ↓
    │                                                      Stock info retrieved
    │                                                          ↓
    │                                                      Agent responds with prescription + stock info
    │
    └─→ Medication not found → Agent responds with error + suggestions
```

## Complete Conversation Examples

### Example 1: Prescription Required + Availability (Hebrew)

**User:** "אני צריך אנטיביוטיקה, האם צריך מרשם? וזה זמין?" (I need antibiotics, do I need a prescription? And is it available?)

**Agent Tool Calls:**
1. `get_medication_by_name(name="אנטיביוטיקה")` → `medication_id: "med_003"` + basic medication info (NO prescription or stock info)
2. `check_prescription_requirement(medication_id="med_003")` → `requires_prescription: true` (required because `get_medication_by_name` does not return prescription info)
3. `check_stock_availability(medication_id="med_003")` → `available: true, quantity: 75` (required because `get_medication_by_name` does not return stock info)

**Agent Response:**
"אמוקסיצילין דורש מרשם רופא. התרופה זמינה במלאי - יש לנו 75 יחידות. אנא הבא מרשם רופא תקף כדי לרכוש את התרופה." (Amoxicillin requires a doctor's prescription. The medication is available in stock - we have 75 units. Please bring a valid doctor's prescription to purchase the medication.)

### Example 2: No Prescription Required (English)

**User:** "Does Acetaminophen require a prescription?"

**Agent Tool Calls:**
1. `get_medication_by_name(name="Acetaminophen")` → `medication_id: "med_001"` + basic medication info
2. `check_prescription_requirement(medication_id="med_001")` → `requires_prescription: false` (required because `get_medication_by_name` does not return prescription info)

**Agent Response:**
"Acetaminophen does not require a doctor's prescription - it can be purchased without a prescription. The medication is available in stock - we have 150 units."

### Example 3: Prescription Required But Not Available (Hebrew)

**User:** "אני צריך אמוקסיצילין, צריך מרשם?" (I need Amoxicillin, do I need a prescription?)

**Agent Tool Calls:**
1. `get_medication_by_name(name="אמוקסיצילין")` → `medication_id: "med_003"` + basic medication info
2. `check_prescription_requirement(medication_id="med_003")` → `requires_prescription: true` (required because `get_medication_by_name` does not return prescription info)
3. `check_stock_availability(medication_id="med_003")` → `available: false, quantity: 0` (required because `get_medication_by_name` does not return stock info)

**Agent Response:**
"אמוקסיצילין דורש מרשם רופא. כרגע התרופה לא זמינה במלאי. אנא פנה לבית המרקחת עם מרשם רופא לבדיקת מועד אספקה מחדש." (Amoxicillin requires a doctor's prescription. The medication is currently not available in stock. Please contact the pharmacy with a doctor's prescription to check when it will be restocked.)

### Example 4: Complex Query (English)

**User:** "I want to buy Paracetamol. Do I need a prescription and is it in stock?"

**Agent Tool Calls:**
1. `get_medication_by_name(name="Paracetamol")` → `medication_id: "med_001"` + basic medication info
2. `check_prescription_requirement(medication_id="med_001")` → `requires_prescription: false` (required because `get_medication_by_name` does not return prescription info)
3. `check_stock_availability(medication_id="med_001")` → `available: true, quantity: 150` (required because `get_medication_by_name` does not return stock info)

**Agent Response:**
"Paracetamol (Acetaminophen) does not require a doctor's prescription - it can be purchased without a prescription. The medication is available in stock - we have 150 units."

## Required Testing

For each flow, test at least 5+ variations in Hebrew and 5+ variations in English:

### Variations in Hebrew:
1. "אני צריך אנטיביוטיקה, האם צריך מרשם?" (I need antibiotics, do I need a prescription?)
2. "האם אקמול דורש מרשם רופא?" (Does Acamol require a doctor's prescription?)
3. "אני רוצה לקנות פרצטמול, צריך מרשם?" (I want to buy Paracetamol, do I need a prescription?)
4. "האם יש לכם אנטיביוטיקה במלאי וצריך מרשם?" (Do you have antibiotics in stock and do they require a prescription?)
5. "אמוקסיצילין - צריך מרשם? וזמין במלאי?" (Amoxicillin - requires prescription? And is it in stock?)
6. "מה דרישת המרשם לאקמול?" (What's the prescription requirement for Acamol?)
7. "אני צריך לקנות תרופה, איך אדע אם צריך מרשם?" (I need to buy medication, how do I know if I need a prescription?)

### Variations in English:
1. "I need antibiotics, do I need a prescription?"
2. "Does Acetaminophen require a prescription?"
3. "I want to buy Paracetamol, do I need a prescription?"
4. "Do you have antibiotics in stock and do they require a prescription?"
5. "Amoxicillin - requires prescription? And is it in stock?"
6. "What's the prescription requirement for Acetaminophen?"
7. "I need to buy medication, how do I know if I need a prescription?"

## Important Notes

1. **Stateless Agent:** Each conversation is independent, no memory between different conversations
2. **Bilingual Support:** Agent responds in the same language the user wrote in
3. **No Medical Advice:** Agent only provides information about prescription requirements, does not recommend medications
4. **Safe Defaults:** In case of error, `requires_prescription` is set to `true` as a safe default
5. **Combined Queries:** Agent can handle combined queries (prescription + availability) in the same conversation
6. **Policy Adherence:** Agent always emphasizes that a valid doctor's prescription is required when needed
