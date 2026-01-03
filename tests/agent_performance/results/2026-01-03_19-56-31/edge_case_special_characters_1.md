# Test: edge_case_special_characters_1
**Date:** 2026-01-03 19:59:16  
**Agent Type:** streaming
**Correlation ID:** `76e80d81-d389-4ac2-bc0e-e1b25cc8374c`

## Input
- **User Message:** "תגיד לי על תרופה בשם: !@#$%^&*()_+-=[]{}|;':",./<>?"
- **Model:** gpt-5
- **Seed:** 42
- **Conversation History:** None

## Processing

### Iteration 1

**API Call #1**
- **Messages Sent:**
  - System: You are a professional Pharmacy AI Assistant for a retail pharmacy chain. Help customers with medication inquiries using pharmacy data.
  - User: "תגיד לי על תרופה בשם: !@#$%^&*()_+-=[]{}|;':",./<>?"
- **Parameters:**
  - Model: gpt-5
  - Seed: 42
  - Stream: True
- **Stream Chunks:**
  - Total Chunks: 1
- **Model Response:**
  - Tool Calls: 1
    - Tool: `get_medication_by_name`
      - ID: `call_5cZNcTaROpQjbIhE3qMisEwk`
      - Arguments: `{"name":"!@#$%^&*()_+-=[]{}|;':\",./<>?","language...`
  - Finish Reason: `tool_calls`

**Tool Execution #1**
- Tool: `get_medication_by_name`
- Arguments: `{"name": "!@#$%^&*()_+-=[]{}|;':\",./<>?", "language": "he"}`
- Result: `{"error": "Medication '!@#$%^&*()_+-=[]{}|;':\",./<>?' not found. Please check the spelling or try a...`
- Execution Time: 0.000s
- Correlation ID: `76e80d81-d389-4ac2-bc0e-e1b25cc8374c`

*Iteration Time: 3.820s*

### Iteration 2

**API Call #2**
- **Messages Sent:**
  - System: You are a professional Pharmacy AI Assistant for a retail pharmacy chain. Help customers with medication inquiries using pharmacy data.
  - User: "תגיד לי על תרופה בשם: !@#$%^&*()_+-=[]{}|;':",./<>?"
  - Assistant:  [Tool Calls: get_medication_by_name]
  - Tool (ID: call_5cZNcTaROpQjbIhE3qMisEwk): {"error": "Medication '!@#$%^&*()_+-=[]{}|;':\",./<>?' not found. Please check the spelling or try a different name.", "searched_name": "!@#$%^&*()_+-=[]{}|;':\",./<>?", "suggestions": []}
- **Parameters:**
  - Model: gpt-5
  - Seed: 42
  - Stream: True
- **Stream Chunks:**
  - Total Chunks: 256
  - Chunks with Content: 255
- **Model Response:**
  - Accumulated Content: "לא מצאתי תרופה בשם הזה. נראה שהוזנו תווי סימון/מיוחדים. אנא שלח/י את שם התרופה המדויק בעברית או באנג..."
  - Finish Reason: `stop`

*Iteration Time: 17.116s*

## Output
**Final Response:** "לא מצאתי תרופה בשם הזה. נראה שהוזנו תווי סימון/מיוחדים. אנא שלח/י את שם התרופה המדויק בעברית או באנגלית (שם מסחרי או שם גנרי).

אפשרויות שיעזרו לי למצוא:
- כתיב מדויק של השם (למשל: “אקמול” או “Acamol”).
- שם החומר הפעיל (למשל: פרצטמול/Paracetamol).
- צורת המוצר (טבליות, סירופ, ג’ל וכד’).

ברגע שתתני/יתן שם תקין, אוכל לספק:
- מידע מלא על התרופה, כולל החומרים הפעילים.
- צורות מינון ותיאור המוצר.
- מידע כללי מתוך העלון לגבי מינונים ותדירות שימוש.
- האם נדרש מרשם.
- זמינות במלאי.

אם התכוונת למשהו כ..."

**All Chunks:** 255 chunks
- Chunk 1: "לא"
- Chunk 2: " מצ"
- Chunk 3: "א"
- Chunk 4: "תי"
- Chunk 5: " תר"
- ... and 250 more chunks

## Statistics
- Total API Calls: 2
- Total Tool Calls: 1
- Total Chunks: 255
- Total Time: 20.936s
- Tools Used: get_medication_by_name

## Evaluation

### Token Usage
- Total Input Tokens: 2,081
- Total Output Tokens: 556
- Total Tokens: 2,637
- Average Input Tokens per Call: 1040.5
- Average Output Tokens per Call: 278.0
- System Prompt Tokens: 1,937

### Cost Estimation
- Total Estimated Cost: $0.037490
- Input Cost: $0.020810
- Output Cost: $0.016680
- Model: gpt-5

### Efficiency Issues
- **large_system_prompt** (medium): System prompt is 1937 tokens
- **repeated_message** (low): Message content repeated across iterations

### Efficiency Score: **85.0/100**
  - Status: Excellent

### Summary
- Total Duplicate API Calls: 0
- Total Duplicate Tool Calls: 0
- Total Redundant Information Cases: 0
- Total Inefficiency Issues: 2
- Estimated Cost: $0.037490
- Total Tokens: 2,637
- Efficiency Score: 85.0/100
