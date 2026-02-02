FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY profiles/ ./profiles/

# The entrypoint script that runs when the action starts
CMD ["python", "/app/src/main.py"]
