FROM python:3.12-slim

WORKDIR /home/app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /home/app

USER appuser

CMD ["python", "main.py"]
