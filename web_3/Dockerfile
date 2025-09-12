FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8888

# Create a non-root user and switch to it
RUN addgroup -g 1000 web3group

RUN adduser -D -u 1000 web3user -G web3group

RUN chown -R web3user:web3group /app

USER web3user

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8888", "app:app"]