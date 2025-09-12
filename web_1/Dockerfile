FROM python:3.11-alpine

WORKDIR /app

RUN apt-get update && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8888

# Create a non-root user and switch to it
RUN addgroup -g 1000 web1group

RUN adduser -D -u 1000 web1user -G web1group

RUN chown -R web1user:web1group /app

USER web1user

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8888", "app:app"]