# Test: performance_conversation_history_1
**Date:** 2026-01-03 06:13:15  
**Agent Type:** streaming
**Correlation ID:** `71b0ade8-41bf-40d5-b569-e42652effbd8`

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
  - Total Chunks: 93
  - Chunks with Content: 92
- **Model Response:**
  - Accumulated Content: "כדי להביא את רשימת המרשמים שלך, אני צריך לאתר את החשבון שלך. אנא ספק/י:
- שם מלא כפי שמופיע אצלנו, א..."
  - Finish Reason: `stop`

*Iteration Time: 16.468s*

## Output
**Final Response:** "כדי להביא את רשימת המרשמים שלך, אני צריך לאתר את החשבון שלך. אנא ספק/י:
- שם מלא כפי שמופיע אצלנו, או
- כתובת האימייל הרשומה אצלנו.

ברגע שאזהה את החשבון, אציג את כל המרשמים הפעילים וההיסטוריים שלך (כולל תאריכים, כמות, ומספר חידושים שנותרו)."

**All Chunks:** 92 chunks
- Chunk 1: "כ"
- Chunk 2: "די"
- Chunk 3: " להב"
- Chunk 4: "יא"
- Chunk 5: " את"
- ... and 87 more chunks

## Statistics
- Total API Calls: 1
- Total Tool Calls: 0
- Total Chunks: 92
- Total Time: 16.473s
- Tools Used: (none)

## Evaluation

### Token Usage
- Total Input Tokens: 1,362
- Total Output Tokens: 227
- Total Tokens: 1,589
- Average Input Tokens per Call: 1362.0
- Average Output Tokens per Call: 227.0
- System Prompt Tokens: 1,253

### Cost Estimation
- Total Estimated Cost: $0.020430
- Input Cost: $0.013620
- Output Cost: $0.006810
- Model: gpt-5

### Efficiency Score: **95.0/100**
  - Status: Excellent

### Summary
- Total Duplicate API Calls: 0
- Total Duplicate Tool Calls: 0
- Total Redundant Information Cases: 0
- Total Inefficiency Issues: 0
- Estimated Cost: $0.020430
- Total Tokens: 1,589
- Efficiency Score: 95.0/100
