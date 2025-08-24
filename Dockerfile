FROM python:3.11-slim

# Set Arbeitsverzeichnis
WORKDIR /app

# Kopiere nur relevante Dateien
COPY requirements.txt run.py ./

# Optional: Umgebungsvariablen für sauberes Verhalten
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installiere Python-Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Starte das Emulator-Skript
CMD ["python", "run.py"]
