FROM python:3.12-slim

WORKDIR /home/app

RUN pip install --upgrade pip && pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main

COPY . .

RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /home/app

USER appuser

CMD ["python", "main.py"]
