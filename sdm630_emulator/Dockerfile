# Basis-Image mit Python 3.11
FROM python:3.11-slim

# Arbeitsverzeichnis setzen
WORKDIR /app

# Systemabhängigkeiten installieren (z. B. für MQTT & Modbus)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt kopieren und installieren
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Projektdateien kopieren
COPY run.py ./

# Startbefehl
CMD ["python", "run.py"]
