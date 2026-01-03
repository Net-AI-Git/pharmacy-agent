# Test: edge_case_nonexistent_user_1
**Date:** 2026-01-03 19:58:22  
**Agent Type:** streaming
**Correlation ID:** `62cae7c2-75dc-4df5-94f2-27e8c799f3e4`

## Input
- **User Message:** "מה המרשמים שלי? אני לא קיים במערכת 12345"
- **Model:** gpt-5
- **Seed:** 42
- **Conversation History:** None

## Processing

### Iteration 1

**API Call #1**
- **Messages Sent:**
  - System: You are a professional Pharmacy AI Assistant for a retail pharmacy chain. Help customers with medication inquiries using pharmacy data.
  - User: "מה המרשמים שלי? אני לא קיים במערכת 12345"
- **Parameters:**
  - Model: gpt-5
  - Seed: 42
  - Stream: True
- **Stream Chunks:**
  - Total Chunks: 204
  - Chunks with Content: 203
- **Model Response:**
  - Accumulated Content: "אני יכול להציג מרשמים רק עבור המשתמש המאומת עצמו. כרגע אינך מחובר, ובנוסף כתבת שאינך קיים במערכת—במק..."
  - Finish Reason: `stop`

*Iteration Time: 20.711s*

## Output
**Final Response:** "אני יכול להציג מרשמים רק עבור המשתמש המאומת עצמו. כרגע אינך מחובר, ובנוסף כתבת שאינך קיים במערכת—במקרה כזה לא יופיעו לנו מרשמים.

אפשרויות להמשך:
- אם יש לך חשבון: היכנס/י לחשבון ולאחר ההתחברות שאל/י שוב “מה המרשמים שלי?” ואוכל לשלוף אותם מיד.
- אם אין לך חשבון/רישום אצלנו: לא יופיעו מרשמים במערכת. אפשר לפתוח רישום בבית המרקחת ולבקש מהרופא להעביר מרשם אלקטרוני, או להביא מרשם פיזי לבית המרקחת.
- אם תרצה/י שאבדוק בכל זאת לפי פרטים מזהים, שלח/י את שמך המלא או את כתובת האימייל הרשומה (אם קיימת), ואב..."

**All Chunks:** 203 chunks
- Chunk 1: "אני"
- Chunk 2: " יכול"
- Chunk 3: " לה"
- Chunk 4: "ציג"
- Chunk 5: " מר"
- ... and 198 more chunks

## Statistics
- Total API Calls: 1
- Total Tool Calls: 0
- Total Chunks: 203
- Total Time: 20.712s
- Tools Used: (none)

## Evaluation

### Token Usage
- Total Input Tokens: 1,970
- Total Output Tokens: 497
- Total Tokens: 2,467
- Average Input Tokens per Call: 1970.0
- Average Output Tokens per Call: 497.0
- System Prompt Tokens: 1,937

### Cost Estimation
- Total Estimated Cost: $0.034610
- Input Cost: $0.019700
- Output Cost: $0.014910
- Model: gpt-5

### Efficiency Issues
- **large_system_prompt** (medium): System prompt is 1937 tokens

### Efficiency Score: **87.0/100**
  - Status: Excellent

### Summary
- Total Duplicate API Calls: 0
- Total Duplicate Tool Calls: 0
- Total Redundant Information Cases: 0
- Total Inefficiency Issues: 1
- Estimated Cost: $0.034610
- Total Tokens: 2,467
- Efficiency Score: 87.0/100
