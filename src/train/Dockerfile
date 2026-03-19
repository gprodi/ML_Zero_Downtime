FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./

# Installation des dépendances
RUN uv sync --no-dev
ENV PATH="/app/.venv/bin:$PATH"

COPY src/train ./src/train

# Le conteneur exécutera ce script en continu
CMD ["python", "src/train/train.py"]