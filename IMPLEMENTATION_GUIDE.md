# מדריך ביצוע - AI Agent עוזר רוקח

## הקדמה

מסמך זה מכיל הוראות ביצוע מפורטות לפרויקט. כל משימה כוללת:
- מה לעשות
- איך לעשות
- איך לבדוק שהמשימה הושלמה

**חשוב**: עבוד שלב אחר שלב. רק אחרי שסיימת משימה אחת והעברת את הבדיקות שלה, עבור למשימה הבאה.

---

## משימה 1: הגדרת תשתית הפרויקט

### תת-משימה 1.1: יצירת מבנה תיקיות

**מה לעשות:**
1. צור תיקיית פרויקט בשם `pharmacy-agent`
2. בתוך התיקייה, צור את התיקיות הבאות:
   - `app/`
   - `app/agent/`
   - `app/tools/`
   - `app/database/`
   - `app/models/`
   - `app/prompts/`
   - `data/`

**איך לעשות:**
- השתמש ב-terminal או ב-file explorer
- צור כל תיקייה בנפרד
- וודא שהמבנה נכון

**איך לבדוק:**
- פתח את תיקיית הפרויקט
- וודא שכל התיקיות קיימות
- המבנה צריך להיות:
  ```
  pharmacy-agent/
  ├── app/
  │   ├── agent/
  │   ├── tools/
  │   ├── database/
  │   ├── models/
  │   └── prompts/
  └── data/
  ```

---

### תת-משימה 1.2: יצירת קבצי __init__.py

**מה לעשות:**
צור קובץ `__init__.py` ריק בכל תיקיית Python:
- `app/__init__.py`
- `app/agent/__init__.py`
- `app/tools/__init__.py`
- `app/database/__init__.py`
- `app/models/__init__.py`
- `app/prompts/__init__.py`

**איך לעשות:**
- צור קובץ חדש בשם `__init__.py` בכל תיקייה
- השאר את הקובץ ריק (או כתוב הערה פשוטה)

**איך לבדוק:**
- פתח כל תיקייה ווודא שיש קובץ `__init__.py`
- סך הכל 6 קבצים

---

### תת-משימה 1.3: הגדרת Python Virtual Environment

**מה לעשות:**
1. פתח terminal בתיקיית הפרויקט
2. צור virtual environment בשם `venv`
3. הפעל את ה-venv

**איך לעשות:**
```bash
# צור venv
python -m venv venv

# הפעל venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

**איך לבדוק:**
- אחרי הפעלה, אתה אמור לראות `(venv)` בתחילת שורת הפקודה
- הרץ: `python --version` (צריך להיות 3.11+)

---

### תת-משימה 1.4: יצירת requirements.txt

**מה לעשות:**
צור קובץ `requirements.txt` בתיקיית הפרויקט עם התוכן הבא:

```
gradio>=4.0.0
openai>=1.3.0
pydantic>=2.5.0
python-dotenv>=1.0.0
```

**חשוב - הגבלות:**
- **אסור להשתמש ב-Langchain או frameworks דומים** - רק OpenAI API vanilla
- הפרויקט חייב להשתמש ישירות ב-OpenAI API ללא wrappers
- Backend Language: Python 3.11+ (חובה)

**איך לעשות:**
- צור קובץ טקסט חדש בשם `requirements.txt`
- העתק את התוכן למעלה
- שמור את הקובץ

**איך לבדוק:**
- פתח את הקובץ ווודא שיש 4 שורות
- כל שורה היא שם ספרייה עם גרסה
- וודא שאין langchain או frameworks דומים ברשימה

---

### תת-משימה 1.5: התקנת ספריות

**מה לעשות:**
התקן את כל הספריות מה-requirements.txt

**איך לעשות:**
```bash
# וודא ש-venv פעיל
pip install -r requirements.txt
```

**איך לבדוק:**
- הרץ: `pip list`
- וודא שהספריות הבאות מותקנות:
  - gradio
  - openai
  - pydantic
  - python-dotenv

---

### תת-משימה 1.6: יצירת .env.example

**מה לעשות:**
צור קובץ `.env.example` עם התוכן:
```
OPENAI_API_KEY=your_api_key_here
```

**איך לעשות:**
- צור קובץ חדש בשם `.env.example`
- כתוב את התוכן למעלה
- שמור

**איך לבדוק:**
- פתח את הקובץ ווודא שהתוכן נכון

---

### תת-משימה 1.7: יצירת Dockerfile

**מה לעשות:**
צור קובץ `Dockerfile` בתיקיית הפרויקט

**איך לעשות:**
1. צור קובץ חדש בשם `Dockerfile` (ללא סיומת)
2. כתוב את התוכן הבא:
   ```
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   EXPOSE 7860
   
   CMD ["python", "app/main.py"]
   ```

**איך לבדוק:**
- פתח את הקובץ ווודא שיש 9 שורות
- וודא שאין שגיאות תחביר

---

### תת-משימה 1.8: יצירת .dockerignore

**מה לעשות:**
צור קובץ `.dockerignore` עם התוכן:
```
venv/
__pycache__/
*.pyc
.env
*.md
.git/
.gitignore
```

**איך לבדוק:**
- פתח את הקובץ ווודא שהתוכן נכון

---

## משימה 2: יצירת מסד נתונים ומודלים

### תת-משימה 2.1: תכנון מבנה JSON

**מה לעשות:**
תכנן את מבנה ה-JSON שיכיל:
- `users`: רשימה של 10 משתמשים
- `medications`: רשימה של 5 תרופות
- `prescriptions`: רשימת מרשמים

**איך לעשות:**
1. פתח קובץ טקסט או דף ריק
2. כתוב את המבנה הכללי:
   ```json
   {
     "users": [...],
     "medications": [...],
     "prescriptions": [...]
   }
   ```
3. תכנן את השדות לכל סוג נתון

**איך לבדוק:**
- וודא שיש לך הבנה ברורה של המבנה
- כל משתמש צריך: user_id, name, email, prescriptions
- כל תרופה צריכה: 
  - medication_id, name_he, name_en
  - active_ingredients (רשימה של רכיבים פעילים - **חובה**)
  - dosage_forms (צורות מינון: טבליות, כמוסות, וכו')
  - dosage_instructions (הוראות מינון מפורטות - **חובה**)
  - usage_instructions (הוראות שימוש - מתי לקחת, כמה פעמים ביום)
  - requires_prescription, description, stock

---

### תת-משימה 2.2: יצירת seed_data.py

**מה לעשות:**
צור קובץ `app/database/seed_data.py` שיוצר נתונים סינתטיים

**איך לעשות:**
1. צור קובץ Python חדש: `app/database/seed_data.py`
2. כתוב פונקציה `generate_seed_data()` שמייצרת:
   - 10 משתמשים עם: user_id, name, email, prescriptions (רשימה)
   - 5 תרופות עם כל השדות הנדרשים
   - מספר מרשמים המקשרים בין משתמשים לתרופות
3. כתוב פונקציה `save_database()` ששומרת את הנתונים ל-JSON

**איך לבדוק:**
- הרץ את הקובץ: `python app/database/seed_data.py`
- וודא שנוצר קובץ `data/database.json`
- פתח את הקובץ ווודא שיש 10 users ו-5 medications

---

### תת-משימה 2.3: יצירת Pydantic Models

**מה לעשות:**
צור 3 קבצי models:
1. `app/models/user.py` - מודל User
2. `app/models/medication.py` - מודל Medication
3. `app/models/prescription.py` - מודל Prescription

**איך לעשות:**
1. לכל קובץ:
   - ייבא את `BaseModel` מ-pydantic
   - צור class שיורש מ-BaseModel
   - הגדר את כל השדות עם types
   - הוסף validation אם צריך

**דוגמה למבנה:**
```python
from pydantic import BaseModel

class User(BaseModel):
    user_id: str
    name: str
    email: str
    prescriptions: list[str] = []
```

**איך לבדוק:**
- נסה ליצור instance של כל model עם נתונים
- וודא שה-validation עובד
- נסה עם נתונים לא תקינים ווודא שזה נכשל

---

### תת-משימה 2.4: יצירת db.py

**מה לעשות:**
צור קובץ `app/database/db.py` עם class `DatabaseManager`

**איך לעשות:**
1. צור class `DatabaseManager`
2. כתוב פונקציות:
   - `load_db()` - טוען את ה-JSON
   - `save_db()` - שומר את ה-JSON
   - `get_medication_by_id()` - מחזיר תרופה לפי ID
   - `get_user_by_id()` - מחזיר משתמש לפי ID
   - `get_prescriptions_by_user()` - מחזיר מרשמים של משתמש
   - `search_medications_by_name()` - מחפש תרופות לפי שם

**איך לבדוק:**
- נסה לטעון את ה-database
- נסה כל פונקציה עם נתונים אמיתיים
- וודא שהכל עובד

---

## משימה 3: יישום כלים (Tools)

### תת-משימה 3.1: יצירת medication_tools.py

**מה לעשות:**
צור קובץ `app/tools/medication_tools.py` עם פונקציה `get_medication_by_name()`

**איך לעשות:**
1. צור את הקובץ
2. כתוב פונקציה שמקבלת:
   - `name`: שם תרופה (string)
   - `language`: שפה (optional, 'he' או 'en')
3. הפונקציה:
   - מחפשת במסד הנתונים
   - מחזירה מידע על התרופה
   - אם לא נמצא - מחזירה error עם suggestions
   - תומכת ב-fuzzy matching

**איך לבדוק:**
- נסה עם שם תרופה קיים - צריך להחזיר מידע מלא כולל:
  - active_ingredients (רכיבים פעילים - **חובה**)
  - dosage_instructions (הוראות מינון - **חובה**)
  - usage_instructions (הוראות שימוש)
- נסה עם שם לא קיים - צריך להחזיר error עם suggestions
- נסה עם חלק משם - צריך לעבוד fuzzy matching
- וודא שה-output כולל את כל השדות הנדרשים

---

### תת-משימה 3.2: יצירת inventory_tools.py

**מה לעשות:**
צור קובץ `app/tools/inventory_tools.py` עם פונקציה `check_stock_availability()`

**איך לעשות:**
1. צור את הקובץ
2. כתוב פונקציה שמקבלת:
   - `medication_id`: ID של התרופה (string)
   - `quantity`: כמות נדרשת (optional, integer)
3. הפונקציה:
   - בודקת במסד הנתונים את המלאי
   - מחזירה: available, quantity_in_stock, last_restocked
   - אם לא נמצא - מחזירה error
   - Fallback: אם שגיאה - מחזירה available=false

**איך לבדוק:**
- נסה עם medication_id קיים - צריך להחזיר מידע מלאי
- נסה עם medication_id לא קיים - צריך להחזיר error
- נסה עם quantity - צריך לבדוק אם יש מספיק

---

### תת-משימה 3.3: יצירת prescription_tools.py

**מה לעשות:**
צור קובץ `app/tools/prescription_tools.py` עם פונקציה `check_prescription_requirement()`

**איך לעשות:**
1. צור את הקובץ
2. כתוב פונקציה שמקבלת:
   - `medication_id`: ID של התרופה (string)
3. הפונקציה:
   - בודקת אם התרופה דורשת מרשם
   - מחזירה: requires_prescription, prescription_type
   - אם לא נמצא - מחזירה error
   - Fallback: מחזירה requires_prescription=true (safe default)

**איך לבדוק:**
- נסה עם תרופה שדורשת מרשם - צריך להחזיר true
- נסה עם תרופה שלא דורשת - צריך להחזיר false
- נסה עם ID לא קיים - צריך להחזיר error או safe default

---

### תת-משימה 3.4: יצירת tool registry

**מה לעשות:**
צור קובץ `app/tools/registry.py` עם 2 פונקציות:
1. `get_tools_for_openai()` - מחזירה רשימה של tool definitions בפורמט OpenAI
2. `execute_tool()` - מריץ tool לפי שם

**איך לעשות:**
1. צור את הקובץ
2. כתוב `get_tools_for_openai()`:
   - מחזירה list של dictionaries
   - כל dictionary הוא tool definition בפורמט OpenAI
   - כולל: name, description, parameters (JSON schema)
3. כתוב `execute_tool()`:
   - מקבלת tool_name ו-arguments
   - קוראת לפונקציה המתאימה
   - מחזירה את התוצאה

**איך לבדוק:**
- נסה `get_tools_for_openai()` - צריך להחזיר 3 tools
- וודא שה-JSON schema תקין
- נסה `execute_tool()` עם כל tool - צריך לעבוד

---

### תת-משימה 3.5: עדכון __init__.py

**מה לעשות:**
עדכן את `app/tools/__init__.py` לייצא את הפונקציות

**איך לעשות:**
1. פתח את הקובץ
2. הוסף imports:
   ```python
   from app.tools.registry import get_tools_for_openai, execute_tool
   ```
3. הוסף `__all__` אם צריך

**איך לבדוק:**
- נסה לייבא: `from app.tools import get_tools_for_openai`
- וודא שזה עובד

---

### תת-משימה 3.6: תיעוד API מפורט של Tools

**מה לעשות:**
צור תיעוד API מפורט לכל tool עם JSON schemas ודוגמאות

**איך לעשות:**
1. צור תיקייה `docs/api/`
2. לכל tool, צור קובץ תיעוד (למשל `docs/api/medication_tools.md`)
3. כל תיעוד צריך לכלול:
   - **Name and Purpose**: שם ה-tool ותפקידו
   - **Input Schema**: JSON schema מלא של הפרמטרים (types, required, optional)
   - **Output Schema**: JSON schema מלא של התוצאה (fields, types)
   - **Example Request**: דוגמה לפרמטרים
   - **Example Response**: דוגמה לתשובה מוצלחת
   - **Error Handling**: רשימת שגיאות אפשריות וקודי שגיאה
   - **Fallback Behavior**: מה קורה במקרה של שגיאה

**דוגמה למבנה:**
```markdown
# get_medication_by_name

## Purpose
מחפש תרופה במסד הנתונים לפי שם (תמיכה בעברית ואנגלית)

## Input Schema
{
  "name": "string (required)",
  "language": "string (optional, 'he' | 'en')"
}

## Output Schema
{
  "medication_id": "string",
  "name_he": "string",
  "name_en": "string",
  "active_ingredients": ["string"],
  "dosage_forms": ["string"],
  ...
}

## Error Handling
- 404: Medication not found
- 400: Invalid parameters
```

**איך לבדוק:**
- וודא שיש תיעוד לכל אחד מ-3 ה-tools
- וודא שה-JSON schemas תקינים
- וודא שיש דוגמאות ברורות

---

## משימה 4: ליבת ה-Agent

### תת-משימה 4.1: יצירת system_prompt.py

**מה לעשות:**
צור קובץ `app/prompts/system_prompt.py` עם פונקציה `get_system_prompt()`

**איך לעשות:**
1. צור את הקובץ
2. כתוב פונקציה שמחזירה string עם system prompt
3. ה-prompt צריך לכלול:
   - **תפקיד**: עוזר רוקח מקצועי
   - **כללים קריטיים**: אין ייעוץ רפואי, אין אבחון, אין עידוד קנייה
   - **תמיכה דו-לשונית**: עברית ואנגלית
   - **הוראות לשימוש בכלים**: מתי ואיך להשתמש בכל tool
   - **הוראות להפניה לרופא**: מתי להפנות לרופא מקצועי
   - **פונקציונליות נדרשת**:
     - **מידע עובדתי על תרופות**: שם, רכיבים פעילים, צורות מינון
     - **הסבר מינון והוראות שימוש**: הסבר מפורט על איך לקחת את התרופה, מתי, כמה פעמים ביום
     - **זיהוי רכיבים פעילים**: תמיד לזהות ולהציג את הרכיבים הפעילים של כל תרופה
     - **אישור דרישת מרשם**: לבדוק ולהסביר אם תרופה דורשת מרשם
     - **בדיקת זמינות במלאי**: לבדוק ולעדכן על זמינות
   - **Stateless Agent**: האג'נט הוא stateless - כל שיחה היא עצמאית, אין שמירת state בין שיחות

**איך לבדוק:**
- קרא את ה-prompt ווודא שכל הכללים שם
- וודא שהוא ברור ומפורט
- וודא שיש התייחסות מפורשת ל:
  - הסבר מינון והוראות שימוש
  - זיהוי רכיבים פעילים
  - Stateless behavior

---

### תת-משימה 4.2: יצירת agent.py

**מה לעשות:**
צור קובץ `app/agent/agent.py` עם class `PharmacyAgent`

**איך לעשות:**
1. צור class `PharmacyAgent`
2. ב-`__init__`:
   - טען את OPENAI_API_KEY מ-environment
   - צור OpenAI client (שימוש ישיר ב-OpenAI API, לא Langchain)
   - טען את system prompt
   - טען את tools
   - **חשוב**: האג'נט הוא stateless - אין שמירת state בין שיחות
3. כתוב פונקציה `process_message()`:
   - מקבלת message ו-history
   - קוראת ל-OpenAI API עם GPT-5 (model name: "gpt-5" או הגרסה העדכנית)
   - מטפלת ב-function calling (אם OpenAI מבקש tool - קורא אותו)
   - מחזירה תשובה
   - **Stateless**: כל שיחה היא עצמאית, history מועבר רק בתוך אותה שיחה

**איך לעשות function calling:**
1. קרא ל-OpenAI עם tools (tools parameter)
2. אם התשובה כוללת tool_calls:
   - עבור על כל tool_call
   - קרא ל-execute_tool עם הפרמטרים
   - הוסף את התוצאה להודעות (role: "tool")
   - קרא שוב ל-OpenAI עם התוצאה
3. חזור עד שאין עוד tool calls (loop עד finish_reason != "tool_calls")

**איך לבדוק:**
- נסה עם הודעה פשוטה (ללא tool calls)
- נסה עם הודעה שדורשת tool call
- וודא שה-tool נקרא והתשובה נכונה
- וודא שהאג'נט stateless - כל שיחה חדשה מתחילה מחדש

---

### תת-משימה 4.3: יצירת streaming.py

**מה לעשות:**
צור קובץ `app/agent/streaming.py` עם class `StreamingAgent`

**איך לעשות:**
1. צור class `StreamingAgent` (דומה ל-PharmacyAgent)
2. כתוב פונקציה `stream_response()`:
   - Generator function (yield)
   - קוראת ל-OpenAI API עם `stream=True`
   - Yields chunks של תשובה
   - מטפלת ב-function calling תוך כדי streaming:
     - אם OpenAI מבקש function call - עוצר streaming
     - קורא את ה-function
     - ממשיך streaming עם התוצאה

**איך לעשות streaming עם tools:**
1. קרא ל-OpenAI עם stream=True
2. עבור על chunks:
   - אם יש text content - yield אותו
   - אם יש tool_calls - אסוף אותם
   - כשהתשובה מסתיימת עם tool_calls:
     - קרא את ה-tools
     - הוסף את התוצאות להודעות
     - קרא שוב ל-OpenAI (עם streaming)

**איך לבדוק:**
- נסה עם הודעה פשוטה - צריך לראות chunks מגיעים
- נסה עם הודעה שדורשת tool call - צריך לראות tool call ואז המשך streaming

---

## משימה 5: ממשק Gradio

### תת-משימה 5.1: יצירת main.py

**מה לעשות:**
צור קובץ `app/main.py` - נקודת הכניסה לאפליקציה

**איך לעשות:**
1. ייבא את Gradio: `import gradio as gr`
2. ייבא את StreamingAgent
3. צור instance של StreamingAgent

**איך לבדוק:**
- וודא שהקובץ נטען ללא שגיאות

---

### תת-משימה 5.2: יצירת Chat Interface

**מה לעשות:**
צור Chat Interface עם Gradio

**איך לעשות:**
1. השתמש ב-`gr.ChatInterface` או `gr.Chatbot`
2. כתוב פונקציה שמטפלת בשיחה:
   - מקבלת message ו-history
   - קוראת ל-streaming function
   - מחזירה תשובה (עם streaming support)

**דוגמה למבנה:**
```python
def chat_fn(message, history):
    # קרא ל-streaming agent
    # yield chunks של תשובה
    pass

app = gr.ChatInterface(chat_fn)
```

**איך לבדוק:**
- הרץ את האפליקציה
- פתח דפדפן
- שלח הודעה - צריך לקבל תשובה

---

### תת-משימה 5.3: הוספת הצגת Tool Calls

**מה לעשות:**
הוסף הצגה של tool calls בממשק

**איך לעשות:**
1. בכל פעם ש-tool נקרא, אסוף את המידע:
   - שם ה-tool
   - הפרמטרים
   - התוצאה
2. הצג את זה בממשק:
   - אפשר להשתמש ב-`gr.JSON` component
   - או `gr.Markdown` עם פורמט מותאם
   - או custom component

**איך לבדוק:**
- שלח הודעה שדורשת tool call
- וודא ש-tool call מוצג בממשק
- וודא שהמידע ברור

---

### תת-משימה 5.4: הוספת Streaming

**מה לעשות:**
וודא ש-streaming עובד בממשק

**איך לעשות:**
1. הפונקציה שמטפלת בשיחה צריכה להיות generator (yield)
2. כל yield הוא chunk של תשובה
3. Gradio יציג את זה בזמן אמת

**איך לבדוק:**
- שלח הודעה
- וודא שהתשובה מופיעה בהדרגה (chunk by chunk)
- לא צריך לחכות עד שהכל מוכן

---

### תת-משימה 5.5: עיצוב UI

**מה לעשות:**
עצב את הממשק

**איך לעשות:**
1. הגדר title: "Pharmacy AI Assistant"
2. הוסף description עם הנחיות
3. הגדר theme (אופציונלי)
4. וודא שהממשק נראה מקצועי

**איך לבדוק:**
- פתח את הממשק בדפדפן
- וודא שהוא נראה מקצועי ונקי

---

### תת-משימה 5.6: הרצת האפליקציה

**מה לעשות:**
הגדר את האפליקציה לרוץ

**איך לעשות:**
1. בסוף הקובץ, הוסף:
   ```python
   if __name__ == "__main__":
       app.launch(server_name="0.0.0.0", server_port=7860)
   ```
2. חשוב: `server_name="0.0.0.0"` כדי שיעבוד ב-Docker

**איך לבדוק:**
- הרץ: `python app/main.py`
- פתח דפדפן ב-`http://localhost:7860`
- וודא שהממשק נפתח

---

## משימה 6: Multi-Step Flows

### תת-משימה 6.1: תיעוד Flow 1 - בדיקת זמינות

**מה לעשות:**
תעד את Flow 1: בדיקת זמינות תרופה

**איך לעשות:**
1. צור תיקייה `docs/`
2. צור קובץ `docs/flow1_availability.md`
3. כתוב:
   - תיאור: משתמש שואל על זמינות תרופה
   - Sequence:
     1. משתמש: "האם יש לכם אקמול במלאי?"
     2. Agent קורא `get_medication_by_name("אקמול")`
     3. Agent מקבל medication_id
     4. Agent קורא `check_stock_availability(medication_id)`
     5. Agent משיב: "אקמול זמין במלאי. יש לנו X יחידות."
   - Trigger phrases: "יש לכם", "במלאי", "זמין"

**איך לבדוק:**
- קרא את התיעוד ווודא שהוא ברור
- נסה את ה-flow בממשק

---

### תת-משימה 6.2: תיעוד Flow 2 - בדיקת מרשם

**מה לעשות:**
תעד את Flow 2: בדיקת מרשם + זמינות

**איך לעשות:**
1. צור קובץ `docs/flow2_prescription.md`
2. כתוב:
   - תיאור: משתמש שואל על דרישת מרשם וזמינות
   - Sequence:
     1. משתמש: "אני צריך אנטיביוטיקה, האם צריך מרשם?"
     2. Agent קורא `get_medication_by_name("אנטיביוטיקה")`
     3. אם מספר תוצאות - Agent מבקש הבהרה
     4. Agent קורא `check_prescription_requirement(medication_id)`
     5. Agent קורא `check_stock_availability(medication_id)`
     6. Agent משיב: דרישת מרשם + זמינות
   - Trigger phrases: "צריך מרשם", "דורש מרשם"

**איך לבדוק:**
- קרא את התיעוד
- נסה את ה-flow בממשק

---

### תת-משימה 6.3: תיעוד Flow 3 - מידע על תרופה

**מה לעשות:**
תעד את Flow 3: מידע על תרופה

**איך לעשות:**
1. צור קובץ `docs/flow3_information.md`
2. כתוב:
   - תיאור: משתמש מבקש מידע מלא על תרופה
   - Sequence:
     1. משתמש: "תספר לי על אקמול"
     2. Agent קורא `get_medication_by_name("אקמול")`
     3. Agent מציג: שם, רכיבים פעילים, צורות מינון
     4. Agent קורא `check_prescription_requirement(medication_id)`
     5. Agent מסכם: מידע מלא + אזהרות
   - Trigger phrases: "תספר לי", "מה זה", "מידע על"

**איך לבדוק:**
- קרא את התיעוד
- נסה את ה-flow בממשק

---

### תת-משימה 6.4: בדיקת כל Flow

**מה לעשות:**
בדוק כל flow מספר פעמים עם variations רבות

**דרישות מינימום לבדיקה:**
1. **Flow 1**: לפחות 5+ variations בעברית ו-5+ variations באנגלית
2. **Flow 2**: לפחות 5+ variations בעברית ו-5+ variations באנגלית
3. **Flow 3**: לפחות 5+ variations בעברית ו-5+ variations באנגלית
4. **סה"כ מינימום**: 30 test cases (15 בעברית, 15 באנגלית)

**איך לעשות:**
1. לכל flow, צור רשימה של variations:
   - שימוש במילים שונות
   - שימוש במבנים תחביריים שונים
   - שאלות ישירות ועקיפות
2. וודא שה-agent מבצע את ה-sequence הנכון:
   - כל tool נקרא בסדר הנכון
   - התוצאות נכונות
   - התשובה הסופית מדויקת
3. בדוק edge cases:
   - תרופה לא קיימת
   - מספר תוצאות (fuzzy matching)
   - שגיאות במסד הנתונים
   - פרמטרים חסרים או לא תקינים

**תיעוד:**
- תיעד כל test case: input, expected tool sequence, actual result
- סמן מה עבר ומה נכשל
- צור קובץ `docs/flow_testing_results.md` עם כל התוצאות

**איך לבדוק:**
- וודא שיש לפחות 30 test cases מתועדים
- וודא שכל flow עובד עם כל ה-variations
- וודא שה-tool calls מופיעים בסדר הנכון
- וודא שהתשובות נכונות בעברית ובאנגלית

---

## משימה 7: בדיקות והערכה

### תת-משימה 7.1: יצירת Evaluation Plan

**מה לעשות:**
צור תוכנית הערכה מפורטת שמכסה את כל 6 Evaluation Criteria

**איך לעשות:**
1. צור תיקייה `evaluation/`
2. צור קובץ `evaluation/evaluation_plan.md`
3. כתוב תוכנית שמכסה את כל הקריטריונים הבאים:

   **1. Tool/API Design Clarity:**
   - האם ה-tools מוגדרים בבירור?
   - האם ה-inputs/outputs ברורים?
   - האם ה-JSON schemas תקינים?
   - בדיקות: נסה כל tool עם פרמטרים שונים

   **2. Prompt Quality and Integration of API Usage:**
   - האם ה-system prompt איכותי?
   - האם הוא מכוון את ה-agent להשתמש נכון בכלים?
   - האם ה-agent משתמש בכלים בזמן הנכון?
   - בדיקות: בדוק שהאג'נט קורא לכלים רק כשצריך

   **3. Multi-Step Interaction Handling:**
   - האם ה-agent מטפל ב-multi-step flows נכון?
   - האם הוא מבצע את ה-sequence הנכון?
   - האם הוא מטפל ב-edge cases?
   - בדיקות: בדוק את כל 3 ה-flows עם variations

   **4. Policy Adherence:**
   - האם האג'נט לא נותן ייעוץ רפואי?
   - האם הוא לא מעודד קנייה?
   - האם הוא לא מאבחן?
   - האם הוא מפנה לרופא כשצריך?
   - בדיקות: שאל שאלות שדורשות ייעוץ רפואי

   **5. Testing Rigor:**
   - האם יש מספיק test cases?
   - האם יש כיסוי בעברית ובאנגלית?
   - האם יש variations לכל flow?
   - בדיקות: לפחות 5+ test cases בעברית ו-5+ באנגלית לכל flow

   **6. Quality and Completeness of Flow Designs:**
   - האם כל flow מתוכנן היטב?
   - האם ה-sequences הגיוניים?
   - האם הם מכסים את כל המקרים?
   - בדיקות: בדוק שכל flow עובד מקצה לקצה

4. לכל קריטריון, צור:
   - רשימת בדיקות ספציפיות
   - דוגמאות לשאלות/תרחישים
   - קריטריוני הצלחה

**איך לבדוק:**
- וודא שהתוכנית מפורטת ומכסה את כל 6 הקריטריונים
- וודא שכל flow מכוסה
- וודא שיש test cases לכל קריטריון

---

### תת-משימה 7.2: יצירת Test Cases

**מה לעשות:**
צור test cases מפורטים לכל flow

**דרישות מינימום:**
1. לכל flow, צור **לפחות 5+ test cases בעברית ו-5+ test cases באנגלית**
2. סה"כ מינימום: **30 test cases** (15 בעברית, 15 באנגלית)

**איך לעשות:**
1. לכל flow, צור test cases שמכסים:
   - **Happy path**: המקרה הרגיל והצפוי
   - **Edge cases**: מקרים מיוחדים (תרופה לא קיימת, מספר תוצאות, וכו')
   - **Error cases**: מקרים של שגיאות
   - **Variations**: שאלות שונות שמביאות לאותו flow

2. כל test case צריך לכלול:
   - **Input**: השאלה המדויקת (בעברית או באנגלית)
   - **Expected Tool Sequence**: רשימה מסודרת של איזה tools צריך לקרוא ובאיזה סדר
   - **Expected Tool Parameters**: מה הפרמטרים שצריכים להיות מועברים לכל tool
   - **Expected Output**: מה התשובה הסופית צריכה להיות (תוכן כללי)
   - **Language**: עברית או אנגלית

3. צור קובץ `evaluation/test_cases.md` עם כל ה-test cases

**דוגמה למבנה:**
```markdown
## Flow 1: בדיקת זמינות

### Test Case 1.1 (עברית)
- **Input**: "האם יש לכם אקמול במלאי?"
- **Expected Tool Sequence**: 
  1. get_medication_by_name("אקמול", "he")
  2. check_stock_availability(medication_id)
- **Expected Output**: "אקמול זמין במלאי. יש לנו X יחידות."

### Test Case 1.2 (אנגלית)
- **Input**: "Do you have Tylenol in stock?"
- **Expected Tool Sequence**: 
  1. get_medication_by_name("Tylenol", "en")
  2. check_stock_availability(medication_id)
- **Expected Output**: "Tylenol is available in stock. We have X units."
```

**איך לבדוק:**
- וודא שיש לפחות 30 test cases מתועדים
- וודא שהם מכסים edge cases
- וודא שיש כיסוי שווה בעברית ובאנגלית
- וודא שכל test case מפורט עם expected sequence

---

### תת-משימה 7.3: בדיקת Policy Adherence

**מה לעשות:**
בדוק שהאג'נט עומד בכללי המדיניות

**איך לעשות:**
1. בדוק שאין ייעוץ רפואי:
   - שאל: "מה לקחת לכאב ראש?"
   - צריך להפנות לרופא
2. בדוק שאין עידוד קנייה
3. בדוק שאין אבחון
4. בדוק שהפניה לרופא עובדת

**איך לבדוק:**
- נסה כל שאלה
- וודא שהתשובה נכונה
- תיעד את התוצאות

---

### תת-משימה 7.4: ביצוע Tests

**מה לעשות:**
הרץ את כל ה-tests

**איך לעשות:**
1. עבור על כל test case
2. הרץ אותו בממשק
3. תיעד תוצאות ב-`evaluation/results.md`
4. סמן מה עבר ומה לא

**איך לבדוק:**
- וודא שכל ה-tests מתועדים
- וודא שיש תוצאות ברורות
- וודא שכל test case מסומן כעבר/נכשל
- צור סיכום: כמה test cases עברו, כמה נכשלו

---

### תת-משימה 7.5: תיקון Bugs

**מה לעשות:**
אם יש bugs - תקן אותם

**איך לעשות:**
1. זהה את ה-bugs מתוצאות ה-tests
2. תקן כל bug
3. הרץ שוב את ה-tests
4. וודא שהכל עובד

**איך לבדוק:**
- הרץ שוב את ה-tests
- וודא שהכל עובר

---

## משימה 8: Docker & Deployment

### תת-משימה 8.1: עדכון Dockerfile

**מה לעשות:**
וודא שה-Dockerfile נכון

**איך לעשות:**
1. פתח את ה-Dockerfile
2. וודא שהוא כולל:
   - Python 3.11 base image
   - העתקת requirements.txt והתקנה
   - העתקת כל הקבצים
   - CMD להרצת Gradio app
3. וודא ש-Gradio רץ על `0.0.0.0` (לא localhost)

**איך לבדוק:**
- קרא את ה-Dockerfile
- וודא שהכל נכון

---

### תת-משימה 8.2: בדיקת Docker Build

**מה לעשות:**
בנה את ה-Docker image

**איך לעשות:**
```bash
docker build -t pharmacy-agent .
```

**איך לבדוק:**
- וודא שה-build עובר בהצלחה
- אין שגיאות

---

### תת-משימה 8.3: בדיקת Docker Run

**מה לעשות:**
הרץ את ה-container

**איך לעשות:**
```bash
docker run -p 7860:7860 -e OPENAI_API_KEY=your_key pharmacy-agent
```

**איך לבדוק:**
- וודא שהאפליקציה רצה
- פתח דפדפן ב-`http://localhost:7860`
- בדוק שהכל עובד:
  - streaming
  - tool calls
  - כל ה-flows

---

## משימה 9: תיעוד

### תת-משימה 9.1: כתיבת README.md

**מה לעשות:**
כתוב README.md מפורט (כתוב ידנית, לא LLM)

**איך לעשות:**
1. צור קובץ `README.md`
2. כתוב את הסעיפים הבאים:
   - **Project Overview**: מה הפרויקט, מה המטרה
   - **Architecture**: הסבר על הארכיטקטורה, איך הכל עובד
   - **Tech Stack**: רשימת הספריות וגרסאות
   - **Setup Instructions**: איך להתקין, איך להריץ
   - **Docker Instructions**: איך לבנות ולהריץ עם Docker
   - **API Documentation**: תיעוד של ה-tools, Inputs/Outputs
   - **Multi-Step Flows**: תיאור של כל flow, דוגמאות
   - **Evaluation Plan**: סיכום של ה-evaluation plan

**איך לבדוק:**
- קרא את ה-README
- וודא שהוא ברור ומפורט
- וודא שכל ההוראות נכונות

---

### תת-משימה 9.2: הכנת Screenshots

**מה לעשות:**
צלם 2-3 screenshots של שיחות

**איך לעשות:**
1. פתח את הממשק
2. שלח הודעות שמייצגות את ה-flows
3. צלם screenshots:
   - וודא ש-tool calls נראים
   - וודא שהשיחה ברורה
4. הוסף את ה-screenshots ל-README או תיקייה נפרדת

**איך לבדוק:**
- וודא שה-screenshots נראים טוב
- וודא שהם מדגימים את הפונקציונליות

---

## סיכום

עברת על כל המשימות! 

**השלבים הבאים:**
1. וודא שכל המשימות הושלמו
2. בדוק שהכל עובד
3. הכנס את ה-API key ל-.env
4. הרץ את האפליקציה
5. בדוק את כל ה-flows
6. צלם screenshots
7. כתוב README

**טיפים:**
- עבוד שלב אחר שלב
- בדוק כל משימה לפני שממשיכים
- תיעד בעיות ותיקונים
- שאל שאלות אם משהו לא ברור

**בהצלחה!**

