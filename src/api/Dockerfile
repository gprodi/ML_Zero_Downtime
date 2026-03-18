FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./

# On retire --system, uv va créer un dossier .venv
RUN uv sync --no-dev

# On ajoute l'environnement virtuel au chemin d'exécution du conteneur
ENV PATH="/app/.venv/bin:$PATH"

COPY src/api ./src/api
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]