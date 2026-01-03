# Test: performance_conversation_history_1
**Date:** 2026-01-03 05:33:40  
**Agent Type:** streaming
**Correlation ID:** `2efce6ed-aba4-41ff-a69c-f3fbb8a8853c`

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
  - Total Chunks: 71
  - Chunks with Content: 70
- **Model Response:**
  - Accumulated Content: "כדי לבדוק את המרשמים שלך, אוכל לאתר את החשבון שלך לפי שם מלא או כתובת אימייל. אנא ספק/י:
- השם המלא ..."
  - Finish Reason: `stop`

*Iteration Time: 10.086s*

## Output
**Final Response:** "כדי לבדוק את המרשמים שלך, אוכל לאתר את החשבון שלך לפי שם מלא או כתובת אימייל. אנא ספק/י:
- השם המלא כפי שמופיע אצלנו, או
- כתובת האימייל הרשומה

לאחר מכן אבדוק ואציג את כל המרשמים שלך."

**All Chunks:** 70 chunks
- Chunk 1: "כ"
- Chunk 2: "די"
- Chunk 3: " לבד"
- Chunk 4: "וק"
- Chunk 5: " את"
- ... and 65 more chunks

## Statistics
- Total API Calls: 1
- Total Tool Calls: 0
- Total Chunks: 70
- Total Time: 10.086s
- Tools Used: (none)

## Evaluation

### Token Usage
- Total Input Tokens: 1,440
- Total Output Tokens: 169
- Total Tokens: 1,609
- Average Input Tokens per Call: 1440.0
- Average Output Tokens per Call: 169.0
- System Prompt Tokens: 1,331

### Cost Estimation
- Total Estimated Cost: $0.019470
- Input Cost: $0.014400
- Output Cost: $0.005070
- Model: gpt-5

### Efficiency Score: **95.0/100**
  - Status: Excellent

### Summary
- Total Duplicate API Calls: 0
- Total Duplicate Tool Calls: 0
- Total Redundant Information Cases: 0
- Total Inefficiency Issues: 0
- Estimated Cost: $0.019470
- Total Tokens: 1,609
- Efficiency Score: 95.0/100
