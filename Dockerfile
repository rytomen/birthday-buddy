# ---------- Этап 1: builder (сборка зависимостей) ----------
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ---------- Этап 2: runtime (минимальный образ запуска) ----------
FROM python:3.12-slim AS runtime

# Непривилегированный пользователь
RUN useradd -m -u 1001 appuser

# Только готовое виртуальное окружение из builder, без компиляторов и кэша
COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app" \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY app ./app

USER appuser
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app.main:app"]
