FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Ensure data directory is copied for database access
COPY data/ ./data/

EXPOSE 7860

CMD ["python", "app/main.py"]

