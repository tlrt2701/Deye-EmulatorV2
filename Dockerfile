FROM python:3.11-slim

WORKDIR /app
COPY . /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "run.py"]
