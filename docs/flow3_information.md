# Flow 3: Complete Medication Information

## Overview

This flow handles user queries requesting comprehensive information about medications. It is a complex flow that provides users with complete information about medications, including active ingredients, dosage instructions, prescription requirements, and sometimes stock availability.

**Purpose:** To provide users with comprehensive and detailed information about medications, including all relevant information that can help them understand the medication, how to use it, and what is required to purchase it.

## Sequence

### Step 1: User Query
The user requests information about a medication.

**Example queries in Hebrew:**
- "תספר לי על אקמול" (Tell me about Acamol)
- "מה זה פרצטמול?" (What is Paracetamol?)
- "אני רוצה לדעת על אמוקסיצילין" (I want to know about Amoxicillin)
- "מידע על אקמול" (Information about Acamol)
- "מה זה אקמול ולמה הוא משמש?" (What is Acamol and what is it used for?)
- "תן לי פרטים על פרצטמול" (Give me details about Paracetamol)

**Example queries in English:**
- "Tell me about Acetaminophen"
- "What is Paracetamol?"
- "I want to know about Amoxicillin"
- "Information about Acetaminophen"
- "What is Acetaminophen and what is it used for?"
- "Give me details about Paracetamol"

### Step 2: Search Medication by Name
The agent identifies that the user is requesting information about a medication and performs a medication search by name.

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
- If medication is not found, the agent receives `MedicationSearchError` with suggestions
- Agent displays the error and suggestions to the user

### Step 3: Display Basic Information
The agent displays basic information about the medication from the `get_medication_by_name` result.

**Basic information includes:**
- Medication name (Hebrew and English)
- Active ingredients (active ingredients) - **MUST always display**
- Dosage forms (dosage forms)
- Dosage instructions (dosage instructions) - **MUST always display**
- Usage instructions (usage instructions)
- General description (description)

### Step 4: Check Prescription Requirement
The agent checks the prescription requirement to provide comprehensive information.

**Tool Call:**
```json
{
  "function": "check_prescription_requirement",
  "arguments": {
    "medication_id": "med_001"
  }
}
```

**Possible Response:**
```json
{
  "medication_id": "med_001",
  "medication_name": "אקמול",
  "requires_prescription": false,
  "prescription_type": "not_required"
}
```

### Step 5: Check Stock Availability (Optional)
The agent can check stock availability to provide more comprehensive information, especially if the user explicitly asked about it or if it's relevant.

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

**Decision when to check availability:**
- If user explicitly asked about availability → always check
- If user requested "complete information" or "details" → recommended to check availability
- If medication does not require prescription → can check availability if relevant

### Step 6: Comprehensive Response to User
The agent summarizes all information and provides a comprehensive and organized response to the user.

**Response in Hebrew (complete example):**
```
אקמול (Acetaminophen) הוא משכך כאבים ומפחית חום.

**רכיבים פעילים:**
- Paracetamol 500mg

**צורות מינון:**
- טבליות (Tablets)
- כמוסות (Capsules)

**הוראות מינון:**
500-1000mg כל 4-6 שעות, מקסימום 4g ביום.

**הוראות שימוש:**
יש לקחת עם או אחרי אוכל. ניתן לקחת עד 4 פעמים ביום לפי הצורך.

**דרישת מרשם:**
לא דורש מרשם רופא - ניתן לרכוש ללא מרשם.

**זמינות במלאי:**
זמין במלאי - יש לנו 150 יחידות. המלאי עודכן לאחרונה ב-15 בינואר 2024.

**אזהרה חשובה:**
אנא שים לב - מידע זה הוא מידע עובדתי בלבד ואינו מהווה ייעוץ רפואי. אם יש לך שאלות רפואיות, אנא פנה לרופא או רוקח.
```

**Response in English (complete example):**
```
Acetaminophen (Paracetamol) is a pain reliever and fever reducer.

**Active Ingredients:**
- Paracetamol 500mg

**Dosage Forms:**
- Tablets
- Capsules

**Dosage Instructions:**
500-1000mg every 4-6 hours, maximum 4g per day.

**Usage Instructions:**
Take with or after food. Can be taken up to 4 times per day as needed.

**Prescription Requirement:**
Does not require a doctor's prescription - can be purchased without a prescription.

**Stock Availability:**
Available in stock - we have 150 units. Stock was last restocked on January 15, 2024.

**Important Warning:**
Please note - this information is factual only and does not constitute medical advice. If you have medical questions, please consult a doctor or pharmacist.
```

## Trigger Phrases

The agent identifies this flow based on the following phrases:

**Hebrew:**
- "תספר לי על" (Tell me about)
- "מה זה" (What is)
- "מידע על" (Information about)
- "פרטים על" (Details about)
- "אני רוצה לדעת על" (I want to know about)
- "תן לי מידע על" (Give me information about)
- "מה זה [medication name] ולמה הוא משמש?" (What is [medication name] and what is it used for?)

**English:**
- "Tell me about"
- "What is"
- "Information about"
- "Details about"
- "I want to know about"
- "Give me information about"
- "What is [medication name] and what is it used for?"

## Edge Cases

### 1. Medication Not Found
**Scenario:** User requests information about a medication that doesn't exist in the database.

**Handling:**
1. `get_medication_by_name` returns `MedicationSearchError` with suggestions
2. Agent displays to user: "התרופה [name] לא נמצאה. האם התכוונת לאחת מהתרופות הבאות: [list of suggestions]?" (Medication [name] not found. Did you mean one of the following medications: [list of suggestions]?)

### 2. Multiple Results (Fuzzy Matching)
**Scenario:** Search returns multiple similar medications.

**Handling:**
1. `get_medication_by_name` returns the first medication (closest match)
2. Agent can display to user: "מצאתי את התרופה [name]. האם זו התרופה שביקשת?" (I found medication [name]. Is this the medication you requested?)

### 3. Incomplete Information
**Scenario:** Some required fields are missing in the database.

**Handling:**
1. `get_medication_by_name` returns `MedicationSearchError` if `active_ingredients` or `dosage_instructions` are missing
2. Agent displays to user: "מצטער, המידע על התרופה לא שלם במערכת. אנא פנה לבית המרקחת למידע נוסף." (Sorry, the medication information is incomplete in the system. Please contact the pharmacy for additional information.)

### 4. Specific Query About Active Ingredients
**Scenario:** User explicitly asks about active ingredients.

**Handling:**
1. Agent identifies the specific query
2. Agent emphasizes active ingredients in response: "הרכיב הפעיל באקמול הוא Paracetamol 500mg." (The active ingredient in Acamol is Paracetamol 500mg.)

### 5. Query About Medical Use
**Scenario:** User asks "What is Acamol used for?" or "When should I take Acamol?"

**Handling:**
1. Agent displays the `description` and `usage_instructions`
2. **Important:** Agent does not provide medical advice - only factual information
3. If user asks "Should I take this?" → Agent redirects to doctor

### 6. Safe Default - Prescription Requirement
**Scenario:** Error in checking prescription requirement.

**Handling:**
1. `check_prescription_requirement` returns `PrescriptionCheckError` with `requires_prescription: true` as a safe default
2. Agent displays: "לא הצלחתי לבדוק את דרישת המרשם. אנא פנה לבית המרקחת עם מרשם רופא (כדי להיות בטוח)." (I couldn't check the prescription requirement. Please contact the pharmacy with a doctor's prescription (to be safe).)

## Flow Diagram

```
User Query
    ↓
[Agent analyzes query - identifies information request]
    ↓
get_medication_by_name(name)
    ↓
    ├─→ Medication found → Display basic info (name, active ingredients, dosage, etc.)
    │                          ↓
    │                      check_prescription_requirement(medication_id)
    │                          ↓
    │                      Prescription info retrieved
    │                          ↓
    │                      [If relevant] → check_stock_availability(medication_id)
    │                                         ↓
    │                                     Stock info retrieved
    │                                         ↓
    │                                     Agent provides comprehensive response
    │
    └─→ Medication not found → Agent responds with error + suggestions
```

## Complete Conversation Examples

### Example 1: Complete Information (Hebrew)

**User:** "תספר לי על אקמול" (Tell me about Acamol)

**Agent Tool Calls:**
1. `get_medication_by_name(name="אקמול")` → `medication_id: "med_001"` + all basic information
2. `check_prescription_requirement(medication_id="med_001")` → `requires_prescription: false`
3. `check_stock_availability(medication_id="med_001")` → `available: true, quantity: 150`

**Agent Response:**
"אקמול (Acetaminophen) הוא משכך כאבים ומפחית חום.

**רכיבים פעילים:**
- Paracetamol 500mg

**צורות מינון:**
- טבליות (Tablets)
- כמוסות (Capsules)

**הוראות מינון:**
500-1000mg כל 4-6 שעות, מקסימום 4g ביום.

**הוראות שימוש:**
יש לקחת עם או אחרי אוכל. ניתן לקחת עד 4 פעמים ביום לפי הצורך.

**דרישת מרשם:**
לא דורש מרשם רופא - ניתן לרכוש ללא מרשם.

**זמינות במלאי:**
זמין במלאי - יש לנו 150 יחידות. המלאי עודכן לאחרונה ב-15 בינואר 2024.

**אזהרה חשובה:**
אנא שים לב - מידע זה הוא מידע עובדתי בלבד ואינו מהווה ייעוץ רפואי. אם יש לך שאלות רפואיות, אנא פנה לרופא או רוקח."

### Example 2: Specific Query About Active Ingredients (English)

**User:** "What are the active ingredients in Acetaminophen?"

**Agent Tool Calls:**
1. `get_medication_by_name(name="Acetaminophen")` → `medication_id: "med_001"` + `active_ingredients: ["Paracetamol 500mg"]`

**Agent Response:**
"The active ingredient in Acetaminophen is Paracetamol 500mg. This is the main component that provides the medication's pain-relieving and fever-reducing effects."

### Example 3: Information About Prescription Medication (Hebrew)

**User:** "מה זה אמוקסיצילין?" (What is Amoxicillin?)

**Agent Tool Calls:**
1. `get_medication_by_name(name="אמוקסיצילין")` → `medication_id: "med_003"` + all basic information
2. `check_prescription_requirement(medication_id="med_003")` → `requires_prescription: true`
3. `check_stock_availability(medication_id="med_003")` → `available: true, quantity: 75`

**Agent Response:**
"אמוקסיצילין (Amoxicillin) הוא אנטיביוטיקה המשמשת לטיפול בזיהומים חיידקיים.

**רכיבים פעילים:**
- Amoxicillin 500mg

**צורות מינון:**
- כמוסות (Capsules)

**הוראות מינון:**
500mg שלוש פעמים ביום.

**הוראות שימוש:**
יש לקחת עם אוכל כדי להפחית אי נוחות בקיבה.

**דרישת מרשם:**
דורש מרשם רופא - יש להביא מרשם רופא תקף כדי לרכוש את התרופה.

**זמינות במלאי:**
זמין במלאי - יש לנו 75 יחידות.

**אזהרה חשובה:**
אנא שים לב - מידע זה הוא מידע עובדתי בלבד ואינו מהווה ייעוץ רפואי. אנטיביוטיקה דורשת מרשם רופא ויש לקחת אותה רק לפי הוראות רופא. אם יש לך שאלות רפואיות, אנא פנה לרופא או רוקח."

### Example 4: Query About Use (English)

**User:** "What is Paracetamol used for?"

**Agent Tool Calls:**
1. `get_medication_by_name(name="Paracetamol")` → `medication_id: "med_001"` + `description: "Pain reliever and fever reducer"`

**Agent Response:**
"Paracetamol (Acetaminophen) is used as a pain reliever and fever reducer. It is commonly used to treat:
- Headaches
- Muscle aches
- Fever
- General pain and discomfort

**Active Ingredient:**
- Paracetamol 500mg

**Important Note:**
This information is factual only. If you have questions about whether this medication is right for your specific condition, please consult a doctor or pharmacist."

## Required Testing

For each flow, test at least 5+ variations in Hebrew and 5+ variations in English:

### Variations in Hebrew:
1. "תספר לי על אקמול" (Tell me about Acamol)
2. "מה זה פרצטמול?" (What is Paracetamol?)
3. "אני רוצה לדעת על אמוקסיצילין" (I want to know about Amoxicillin)
4. "מידע על אקמול" (Information about Acamol)
5. "מה זה אקמול ולמה הוא משמש?" (What is Acamol and what is it used for?)
6. "תן לי פרטים על פרצטמול" (Give me details about Paracetamol)
7. "מה הרכיבים הפעילים באקמול?" (What are the active ingredients in Acamol?)

### Variations in English:
1. "Tell me about Acetaminophen"
2. "What is Paracetamol?"
3. "I want to know about Amoxicillin"
4. "Information about Acetaminophen"
5. "What is Acetaminophen and what is it used for?"
6. "Give me details about Paracetamol"
7. "What are the active ingredients in Acetaminophen?"

## Important Notes

1. **Stateless Agent:** Each conversation is independent, no memory between different conversations
2. **Bilingual Support:** Agent responds in the same language the user wrote in
3. **No Medical Advice:** Agent only provides factual information, does not provide medical advice or diagnosis
4. **Active Ingredients - Always Required:** Agent must always display active ingredients (required field)
5. **Dosage Instructions - Always Required:** Agent must always display dosage instructions (required field)
6. **Comprehensive Information:** Agent provides comprehensive and organized information about the medication
7. **Warning Message:** Agent always includes a warning that the information is factual only and does not constitute medical advice
8. **Doctor Referral:** If user asks medical questions, agent redirects to doctor or pharmacist
