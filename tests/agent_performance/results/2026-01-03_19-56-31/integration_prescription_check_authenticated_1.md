# Test: integration_prescription_check_authenticated_1
**Date:** 2026-01-03 20:03:39  
**Agent Type:** streaming
**Correlation ID:** `338d2259-f330-4249-babb-6611651e1932`

## Input
- **User Message:** "האם יש לי מרשם פעיל לאמוקסיצילין?"
- **Model:** gpt-5
- **Seed:** 42
- **Conversation History:** None

## Processing

### Iteration 1

**API Call #1**
- **Messages Sent:**
  - System: You are a professional Pharmacy AI Assistant for a retail pharmacy chain. Help customers with medication inquiries using pharmacy data.
  - User: "האם יש לי מרשם פעיל לאמוקסיצילין?"
- **Parameters:**
  - Model: gpt-5
  - Seed: 42
  - Stream: True
- **Stream Chunks:**
  - Total Chunks: 120
  - Chunks with Content: 119
- **Model Response:**
  - Accumulated Content: "כדי לבדוק אם יש לך מרשם פעיל לאמוקסיצילין, עליי לאמת שזה החשבון שלך.

- אם אתה מחובר/ה לחשבון, אנא א..."
  - Finish Reason: `stop`

*Iteration Time: 32.599s*

## Output
**Final Response:** "כדי לבדוק אם יש לך מרשם פעיל לאמוקסיצילין, עליי לאמת שזה החשבון שלך.

- אם אתה מחובר/ה לחשבון, אנא אשר/י ואבדוק מיד.
- אם אינך מחובר/ת, אנא התחבר/י. לחלופין, אפשר למסור את שמך המלא או את כתובת האימייל המשויכת לחשבון כדי שאוכל לאתר את הפרטים שלך.

שימי/שים לב: אוכל לגשת רק למידע האישי שלך, ולא של מישהו אחר."

**All Chunks:** 119 chunks
- Chunk 1: "כ"
- Chunk 2: "די"
- Chunk 3: " לבד"
- Chunk 4: "וק"
- Chunk 5: " אם"
- ... and 114 more chunks

## Statistics
- Total API Calls: 1
- Total Tool Calls: 0
- Total Chunks: 119
- Total Time: 32.601s
- Tools Used: (none)

## Evaluation

### Token Usage
- Total Input Tokens: 1,970
- Total Output Tokens: 275
- Total Tokens: 2,245
- Average Input Tokens per Call: 1970.0
- Average Output Tokens per Call: 275.0
- System Prompt Tokens: 1,937

### Cost Estimation
- Total Estimated Cost: $0.027950
- Input Cost: $0.019700
- Output Cost: $0.008250
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
- Estimated Cost: $0.027950
- Total Tokens: 2,245
- Efficiency Score: 87.0/100
