FROM python:3.11-slim AS builder

WORKDIR /build

RUN python -m venv /build/venv
ENV PATH="/build/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.11-slim AS runtime

RUN useradd --create-home appuser
WORKDIR /home/appuser

COPY --from=builder /build/venv /build/venv
COPY app/ ./app/

ENV PATH="/build/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
