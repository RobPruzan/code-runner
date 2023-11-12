FROM python:3.9-slim

WORKDIR /app

COPY . /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD gunicorn app:app -b 0.0.0.0:$PORT