# Test: performance_conversation_history_1
**Date:** 2026-01-03 04:32:48  
**Agent Type:** streaming
**Correlation ID:** `7452321c-fa14-4b15-919c-b30551887137`

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
  - Total Chunks: 72
  - Chunks with Content: 71
- **Model Response:**
  - Accumulated Content: "כדי להציג את המרשמים שלך, אנא מסור/י את שמך המלא או כתובת האימייל הרשומה אצלנו כדי שאוכל לאתר את החש..."
  - Finish Reason: `stop`

*Iteration Time: 20.243s*

## Output
**Final Response:** "כדי להציג את המרשמים שלך, אנא מסור/י את שמך המלא או כתובת האימייל הרשומה אצלנו כדי שאוכל לאתר את החשבון.  
אם את/ה מחובר/ת לחשבון, אפשר גם למסור את המזהה המאומת (Authenticated User ID) אם קיים."

**All Chunks:** 71 chunks
- Chunk 1: "כ"
- Chunk 2: "די"
- Chunk 3: " לה"
- Chunk 4: "ציג"
- Chunk 5: " את"
- ... and 66 more chunks

## Statistics
- Total API Calls: 1
- Total Tool Calls: 0
- Total Chunks: 71
- Total Time: 20.243s
- Tools Used: (none)

## Evaluation

### Token Usage
- Total Input Tokens: 1,440
- Total Output Tokens: 158
- Total Tokens: 1,598
- Average Input Tokens per Call: 1440.0
- Average Output Tokens per Call: 158.0
- System Prompt Tokens: 1,331

### Cost Estimation
- Total Estimated Cost: $0.019140
- Input Cost: $0.014400
- Output Cost: $0.004740
- Model: gpt-5

### Efficiency Score: **95.0/100**
  - Status: Excellent

### Summary
- Total Duplicate API Calls: 0
- Total Duplicate Tool Calls: 0
- Total Redundant Information Cases: 0
- Total Inefficiency Issues: 0
- Estimated Cost: $0.019140
- Total Tokens: 1,598
- Efficiency Score: 95.0/100
