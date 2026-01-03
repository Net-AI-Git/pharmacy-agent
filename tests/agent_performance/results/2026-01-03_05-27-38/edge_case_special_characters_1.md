# Test: edge_case_special_characters_1
**Date:** 2026-01-03 05:30:22  
**Agent Type:** streaming
**Correlation ID:** `a6de3562-f8e0-4ff6-9088-c4eaf1ffd1f1`

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
      - ID: `call_ljg9CsnUc1IKWX5ACBB0yZQW`
      - Arguments: `{"name":"!@#$%^&*()_+-=[]{}|;':\",./<>?","language...`
  - Finish Reason: `tool_calls`

**Tool Execution #1**
- Tool: `get_medication_by_name`
- Arguments: `{"name": "!@#$%^&*()_+-=[]{}|;':\",./<>?", "language": "he"}`
- Result: `{"error": "Medication '!@#$%^&*()_+-=[]{}|;':\",./<>?' not found. Please check the spelling or try a...`
- Execution Time: 0.002s
- Correlation ID: `a6de3562-f8e0-4ff6-9088-c4eaf1ffd1f1`

*Iteration Time: 4.684s*

### Iteration 2

**API Call #2**
- **Messages Sent:**
  - System: You are a professional Pharmacy AI Assistant for a retail pharmacy chain. Help customers with medication inquiries using pharmacy data.
  - User: "תגיד לי על תרופה בשם: !@#$%^&*()_+-=[]{}|;':",./<>?"
  - Assistant:  [Tool Calls: get_medication_by_name]
  - Tool (ID: call_ljg9CsnUc1IKWX5ACBB0yZQW): {"error": "Medication '!@#$%^&*()_+-=[]{}|;':\",./<>?' not found. Please check the spelling or try a different name.", "searched_name": "!@#$%^&*()_+-=[]{}|;':\",./<>?", "suggestions": []}
- **Parameters:**
  - Model: gpt-5
  - Seed: 42
  - Stream: True
- **Stream Chunks:**
  - Total Chunks: 189
  - Chunks with Content: 188
- **Model Response:**
  - Accumulated Content: "נראה שהשם שסיפקת כולל תווים מיוחדים, ולא הצלחתי למצוא תרופה בשם הזה. אנא הזן/י:
- שם התרופה המדויק ב..."
  - Finish Reason: `stop`

*Iteration Time: 15.150s*

## Output
**Final Response:** "נראה שהשם שסיפקת כולל תווים מיוחדים, ולא הצלחתי למצוא תרופה בשם הזה. אנא הזן/י:
- שם התרופה המדויק בעברית או באנגלית (לדוגמה: "אקמול", "פאראצטמול", "Advil", "Ibuprofen"), או
- שם החומר הפעיל, או
- אפילו חלק מהשם (אפשר חיפוש עם הקלדה חלקית).

לאחר שתספק/י שם תקין, אוכל לתת מידע מלא: שמות התרופה, החומרים הפעילים, צורות מתן, הוראות מינון (כמות, תדירות, תזמון ומקסימום יומי), האם נדרש מרשם, וזמינות במלאי.

אם מדובר בשאלה רפואית (התאמה לטיפול, תסמינים וכו’) מומלץ לפנות לרופא או לרוקח."

**All Chunks:** 188 chunks
- Chunk 1: "נ"
- Chunk 2: "ראה"
- Chunk 3: " שה"
- Chunk 4: "שם"
- Chunk 5: " שס"
- ... and 183 more chunks

## Statistics
- Total API Calls: 2
- Total Tool Calls: 1
- Total Chunks: 188
- Total Time: 19.848s
- Tools Used: get_medication_by_name

## Evaluation

### Token Usage
- Total Input Tokens: 1,475
- Total Output Tokens: 452
- Total Tokens: 1,927
- Average Input Tokens per Call: 737.5
- Average Output Tokens per Call: 226.0
- System Prompt Tokens: 1,331

### Cost Estimation
- Total Estimated Cost: $0.028310
- Input Cost: $0.014750
- Output Cost: $0.013560
- Model: gpt-5

### Efficiency Issues
- **repeated_message** (low): Message content repeated across iterations

### Efficiency Score: **93.0/100**
  - Status: Excellent

### Summary
- Total Duplicate API Calls: 0
- Total Duplicate Tool Calls: 0
- Total Redundant Information Cases: 0
- Total Inefficiency Issues: 1
- Estimated Cost: $0.028310
- Total Tokens: 1,927
- Efficiency Score: 93.0/100
