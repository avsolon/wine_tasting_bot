FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p storage/db storage/photos storage/backups logs

CMD ["python", "-m", "app.main"]
