FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Expose the port that Gradio will run on
EXPOSE 7860

# Run the application
# Note: app/main.py is configured to run on 0.0.0.0:7860 for Docker compatibility
CMD ["python", "app/main.py"]

