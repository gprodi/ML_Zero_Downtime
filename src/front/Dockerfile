FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./

# On retire --system
RUN uv sync --no-dev

# On ajoute l'environnement virtuel
ENV PATH="/app/.venv/bin:$PATH"

COPY src/front ./src/front
CMD ["streamlit", "run", "src/front/main.py", "--server.port=8501", "--server.address=0.0.0.0"]