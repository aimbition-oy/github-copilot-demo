FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
RUN uv pip install --system --no-cache \
    fastapi \
    "uvicorn[standard]" \
    sqlalchemy \
    pydantic \
    "pydantic-settings" \
    "bcrypt>=4.0.0" \
    pyjwt \
    httpx \
    "psycopg2-binary>=2.9.0"

COPY app/ app/

EXPOSE 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
