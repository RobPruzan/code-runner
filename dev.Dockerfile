
FROM python:3.9-slim

WORKDIR /app

COPY . /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ENV DEBUG=true
ENV PORT=8000
COPY app.py ./
CMD python app.py --reload