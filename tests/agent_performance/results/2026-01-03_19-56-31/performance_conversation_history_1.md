# Test: performance_conversation_history_1
**Date:** 2026-01-03 20:03:56  
**Agent Type:** streaming
**Correlation ID:** `406f46e6-9ee1-4eba-aef1-ef72bda7acfb`

## Input
- **User Message:** "מה המרשמים שלי?"
- **Model:** gpt-5
- **Seed:** 42
- **Conversation History:** 6 messages

## Processing

### Iteration 1

**API Call #1**
- **Messages Sent:**
  - System: You are a professional Pharmacy AI Assistant for a retail pharmacy chain. Help customers with medication inquiries using pharmacy data.
  - User: "מה זה אקמול?"
  - Assistant: אקמול הוא משכך כאבים...
  - User: "האם יש במלאי?"
  - Assistant: כן, יש במלאי 150 יחידות...
  - User: "מה המינון?"
  - Assistant: המינון המומלץ הוא...
  - User: "מה המרשמים שלי?"
- **Parameters:**
  - Model: gpt-5
  - Seed: 42
  - Stream: True
- **Stream Chunks:**
  - Total Chunks: 82
  - Chunks with Content: 81
- **Model Response:**
  - Accumulated Content: "כדי להציג את המרשמים שלך עליי לוודא שזה החשבון שלך.
- אם אתה מחובר: אשר שזה החשבון שלך ואמשוך את המר..."
  - Finish Reason: `stop`

*Iteration Time: 16.945s*

## Output
**Final Response:** "כדי להציג את המרשמים שלך עליי לוודא שזה החשבון שלך.
- אם אתה מחובר: אשר שזה החשבון שלך ואמשוך את המרשמים.
- אם אינך מחובר: אנא ספק שם מלא או כתובת אימייל כדי שאאתר את החשבון שלך.

שימי/שימו לב: איני יכול למסור מידע על אדם אחר."

**All Chunks:** 81 chunks
- Chunk 1: "כ"
- Chunk 2: "די"
- Chunk 3: " לה"
- Chunk 4: "ציג"
- Chunk 5: " את"
- ... and 76 more chunks

## Statistics
- Total API Calls: 1
- Total Tool Calls: 0
- Total Chunks: 81
- Total Time: 16.947s
- Tools Used: (none)

## Evaluation

### Token Usage
- Total Input Tokens: 2,046
- Total Output Tokens: 204
- Total Tokens: 2,250
- Average Input Tokens per Call: 2046.0
- Average Output Tokens per Call: 204.0
- System Prompt Tokens: 1,937

### Cost Estimation
- Total Estimated Cost: $0.026580
- Input Cost: $0.020460
- Output Cost: $0.006120
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
- Estimated Cost: $0.026580
- Total Tokens: 2,250
- Efficiency Score: 87.0/100
