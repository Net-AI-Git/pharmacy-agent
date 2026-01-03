# Test: integration_full_flow_authenticated_1
**Date:** 2026-01-03 20:02:02  
**Agent Type:** streaming
**Correlation ID:** `aa9476b5-3ed5-4d85-84fa-dba337a81bab`

## Input
- **User Message:** "מה המרשמים שלי? האם יש במלאי? תגיד לי על התרופות שלי"
- **Model:** gpt-5
- **Seed:** 42
- **Conversation History:** None

## Processing

### Iteration 1

**API Call #1**
- **Messages Sent:**
  - System: You are a professional Pharmacy AI Assistant for a retail pharmacy chain. Help customers with medication inquiries using pharmacy data.
  - User: "מה המרשמים שלי? האם יש במלאי? תגיד לי על התרופות שלי"
- **Parameters:**
  - Model: gpt-5
  - Seed: 42
  - Stream: True
- **Stream Chunks:**
  - Total Chunks: 171
  - Chunks with Content: 170
- **Model Response:**
  - Accumulated Content: "אשמח לעזור! כדי להציג את המרשמים האישיים שלך ולבדוק זמינות במלאי, צריך שתהיה/י מחובר/ת לחשבון.

- אם..."
  - Finish Reason: `stop`

*Iteration Time: 29.501s*

## Output
**Final Response:** "אשמח לעזור! כדי להציג את המרשמים האישיים שלך ולבדוק זמינות במלאי, צריך שתהיה/י מחובר/ת לחשבון.

- אם את/ה מחובר/ת: אשר/י, ואמשוך את המרשמים הפעילים שלך מיד.
- אם לא: התחבר/י, או ספק/י את שמך המלא או כתובת האימייל כדי שאאתר את החשבון.

לאחר שאזהה את החשבון, אציג לך:
- את כל המרשמים הפעילים שלך
- זמינות במלאי לכל תרופה
- מידע על כל תרופה (שם בעברית/אנגלית, רכיבים פעילים, צורות מתן, והנחיות שימוש כפי שמופיעות בעלון)

רוצה שאמשיך עכשיו?"

**All Chunks:** 170 chunks
- Chunk 1: "אש"
- Chunk 2: "מח"
- Chunk 3: " לע"
- Chunk 4: "זור"
- Chunk 5: "!"
- ... and 165 more chunks

## Statistics
- Total API Calls: 1
- Total Tool Calls: 0
- Total Chunks: 170
- Total Time: 29.505s
- Tools Used: (none)

## Evaluation

### Token Usage
- Total Input Tokens: 1,984
- Total Output Tokens: 400
- Total Tokens: 2,384
- Average Input Tokens per Call: 1984.0
- Average Output Tokens per Call: 400.0
- System Prompt Tokens: 1,937

### Cost Estimation
- Total Estimated Cost: $0.031840
- Input Cost: $0.019840
- Output Cost: $0.012000
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
- Estimated Cost: $0.031840
- Total Tokens: 2,384
- Efficiency Score: 87.0/100
