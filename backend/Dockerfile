# Pin minor version for reproducible builds — update deliberately, not automatically
FROM python:3.12.9-slim AS base
WORKDIR /app

FROM base AS deps
COPY pyproject.toml ./
RUN pip install --no-cache-dir --root-user-action=ignore -e ".[dev]"

FROM base AS production
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin
COPY . .
RUN groupadd -r app && useradd -r -g app app
USER app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
