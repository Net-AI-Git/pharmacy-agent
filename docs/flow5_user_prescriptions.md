# Flow 5: User Prescription Management

## Overview

This flow handles user queries about their prescriptions. It enables users to view their prescription history, check for active prescriptions for specific medications, and verify prescription details. Users can identify themselves by name or email address, making the interaction more natural and user-friendly.

**Purpose:** To provide users with access to their prescription information, including prescription history, active prescriptions, and prescription details for specific medications.

## Sequence

### Step 1: User Query
The user asks about their prescriptions or identifies themselves and asks about prescriptions.

**Example queries in Hebrew:**
- "מה המרשמים שלי?" (What are my prescriptions?)
- "תגיד לי על המרשמים שלי" (Tell me about my prescriptions)
- "אני John Doe, מה המרשמים שלי?" (I'm John Doe, what are my prescriptions?)
- "האם יש לי מרשם פעיל לאקמול?" (Do I have an active prescription for Acamol?)
- "האם יש לי מרשם לאמוקסיצילין?" (Do I have a prescription for Amoxicillin?)
- "מה המרשמים הפעילים שלי?" (What are my active prescriptions?)

**Example queries in English:**
- "What are my prescriptions?"
- "Tell me about my prescriptions"
- "I'm John Doe, what are my prescriptions?"
- "Do I have an active prescription for Acetaminophen?"
- "Do I have a prescription for Amoxicillin?"
- "What are my active prescriptions?"

### Step 2: Find User by Name or Email
The agent identifies that the user is asking about their prescriptions and needs to find the user first.

**Tool Call:**
```json
{
  "function": "get_user_by_name_or_email",
  "arguments": {
    "name_or_email": "John Doe"
  }
}
```

**Possible Response:**
```json
{
  "user_id": "user_001",
  "name": "John Doe",
  "email": "john.doe@example.com",
  "prescriptions": ["prescription_001"]
}
```

**If user not found:**
```json
{
  "error": "User 'InvalidUser' not found. Please check the spelling or try a different name or email.",
  "searched_name_or_email": "InvalidUser",
  "suggestions": ["John Doe", "Jane Smith"]
}
```

### Step 3A: Get All Prescriptions (for general queries)
If the user asks "What are my prescriptions?" or similar, the agent retrieves all prescriptions for the user.

**Tool Call:**
```json
{
  "function": "get_user_prescriptions",
  "arguments": {
    "user_id": "user_001"
  }
}
```

**Possible Response:**
```json
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

**If user has no prescriptions:**
```json
{
  "user_id": "user_006",
  "user_name": "Emily Davis",
  "prescriptions": []
}
```

### Step 3B: Check Active Prescription for Specific Medication (for medication-specific queries)
If the user asks "Do I have a prescription for X?", the agent needs to:
1. Find the medication by name
2. Check if user has an active prescription for that medication

**Tool Call 1 - Find Medication:**
```json
{
  "function": "get_medication_by_name",
  "arguments": {
    "name": "אקמול",
    "language": "he"
  }
}
```

**Tool Call 2 - Check Prescription:**
```json
{
  "function": "check_user_prescription_for_medication",
  "arguments": {
    "user_id": "user_001",
    "medication_id": "med_001"
  }
}
```

**Possible Response (Active Prescription Found):**
```json
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

**Possible Response (No Active Prescription):**
```json
{
  "has_active_prescription": false,
  "prescription_details": null
}
```

### Step 4: Agent Response
The agent presents the prescription information to the user in a clear, organized format.

**For general prescription queries:**
- Lists all prescriptions with medication names (Hebrew and English)
- Shows prescription dates, expiry dates, quantities, refills remaining, and status
- If no prescriptions, informs user they have no prescriptions

**For medication-specific queries:**
- Clearly states whether user has an active prescription for the medication
- If active prescription exists, provides prescription details
- If no active prescription, informs user they don't have an active prescription for that medication

## Usage Description

### When to Use This Flow

This flow is triggered when:
1. User asks about their prescriptions (general query)
2. User identifies themselves and asks about prescriptions
3. User asks if they have a prescription for a specific medication
4. User asks about active prescriptions

### Tool Usage Sequence

**For general prescription queries:**
1. `get_user_by_name_or_email(name_or_email)` - Find user
2. `get_user_prescriptions(user_id)` - Get all prescriptions

**For medication-specific queries:**
1. `get_user_by_name_or_email(name_or_email)` - Find user
2. `get_medication_by_name(name, language)` - Find medication
3. `check_user_prescription_for_medication(user_id, medication_id)` - Check active prescription

### Error Handling

- **User not found**: Agent should inform user that they couldn't be found and suggest checking the name/email spelling
- **Medication not found**: Agent should inform user that the medication couldn't be found and suggest checking the medication name
- **No prescriptions**: Agent should inform user they have no prescriptions (this is not an error)
- **No active prescription**: Agent should inform user they don't have an active prescription for that medication (this is not an error)

## Examples

### Example 1: General Prescription Query (Hebrew)

**User:** "מה המרשמים שלי?"

**Agent Actions:**
1. Calls `get_user_by_name_or_email` - but user didn't provide name/email
2. Agent should ask user to identify themselves, or use context if available

**User:** "אני John Doe"

**Agent Actions:**
1. Calls `get_user_by_name_or_email("John Doe")` → Returns user_001
2. Calls `get_user_prescriptions("user_001")` → Returns prescriptions list
3. Presents prescription information to user

### Example 2: Medication-Specific Query (English)

**User:** "Do I have an active prescription for Acetaminophen?"

**Agent Actions:**
1. Calls `get_user_by_name_or_email` - but user didn't provide name/email
2. Agent should ask user to identify themselves, or use context if available

**User:** "I'm John Doe"

**Agent Actions:**
1. Calls `get_user_by_name_or_email("John Doe")` → Returns user_001
2. Calls `get_medication_by_name("Acetaminophen", "en")` → Returns med_001
3. Calls `check_user_prescription_for_medication("user_001", "med_001")` → Returns has_active_prescription=false
4. Informs user they don't have an active prescription for Acetaminophen

### Example 3: User with Prescriptions

**User:** "I'm John Doe, what are my prescriptions?"

**Agent Actions:**
1. Calls `get_user_by_name_or_email("John Doe")` → Returns user_001
2. Calls `get_user_prescriptions("user_001")` → Returns prescriptions list with Amoxicillin prescription
3. Presents: "You have 1 active prescription: Amoxicillin (אמוקסיצילין), prescribed by Dr. Sarah Levy on 2024-01-10, expires on 2024-04-10, quantity: 30, refills remaining: 2"

## Notes

- Users can identify themselves by name or email address
- Search is case-insensitive and supports partial matches
- If multiple users match, the first match is used
- Empty prescription list is not an error - user simply has no prescriptions
- Only active prescriptions are returned by `check_user_prescription_for_medication`
- All prescription information includes medication names in both Hebrew and English for better user experience

