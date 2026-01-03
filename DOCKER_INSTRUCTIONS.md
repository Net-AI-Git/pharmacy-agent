# הוראות Docker - Pharmacy AI Agent

## דרישות מוקדמות

1. **התקן Docker Desktop**:
   - הורד מ: https://www.docker.com/products/docker-desktop
   - התקן והפעל את Docker Desktop
   - וודא ש-Docker פועל (הסמל בתחתית המסך צריך להיות ירוק)

2. **הכן קובץ .env**:
   - העתק את `.env.example` ל-`.env`
   - הוסף את ה-OPENAI_API_KEY שלך

## תת-משימה 8.2: בניית Docker Image

לבנות את ה-Docker image, הרץ את הפקודה הבאה בתיקיית הפרויקט:

```bash
docker build -t pharmacy-agent .
```

**איך לבדוק:**
- וודא שה-build עובר בהצלחה
- אין שגיאות
- ה-image נוצר (בדוק עם `docker images`)

## תת-משימה 8.3: הרצת Docker Container

להרצת ה-container, השתמש בפקודה הבאה:

```bash
docker run -p 7860:7860 -e OPENAI_API_KEY=your_api_key_here pharmacy-agent
```

או אם יש לך קובץ `.env`:

```bash
docker run -p 7860:7860 --env-file .env pharmacy-agent
```

**איך לבדוק:**
- וודא שהאפליקציה רצה
- פתח דפדפן ב-`http://localhost:7860`
- בדוק שהכל עובד:
  - streaming
  - tool calls
  - כל ה-flows

## הערות חשובות

1. **פורט 7860**: האפליקציה רצה על פורט 7860. אם הפורט תפוס, תוכל לשנות:
   ```bash
   docker run -p 8080:7860 -e OPENAI_API_KEY=your_key pharmacy-agent
   ```
   ואז גש ל-`http://localhost:8080`

2. **משתני סביבה**: אם יש לך משתני סביבה נוספים (כמו `ENVIRONMENT`, `RATE_LIMIT_PER_MINUTE`), הוסף אותם:
   ```bash
   docker run -p 7860:7860 -e OPENAI_API_KEY=your_key -e ENVIRONMENT=prod pharmacy-agent
   ```

3. **נתונים**: ה-container כולל את תיקיית `data/` עם `database.json`, כך שהאפליקציה תוכל לגשת למסד הנתונים.

4. **לוגים**: כדי לראות את הלוגים:
   ```bash
   docker logs <container_id>
   ```

## פתרון בעיות

### Docker לא מזוהה
- וודא ש-Docker Desktop פועל
- נסה להפעיל מחדש את הטרמינל
- נסה להפעיל מחדש את Docker Desktop

### פורט תפוס
- שנה את הפורט ב-`docker run` (למשל `-p 8080:7860`)
- או עצור את האפליקציה שרצה על פורט 7860

### שגיאת API Key
- וודא שה-OPENAI_API_KEY מועבר נכון
- בדוק שהוא תקין ב-`.env`

### שגיאת database
- וודא שתיקיית `data/` נכללת ב-build
- בדוק ש-`database.json` קיים

