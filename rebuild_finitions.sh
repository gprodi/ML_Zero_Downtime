#!/bin/bash
echo "🛡️ Démarrage de la Phase 2 : Injection DevSecOps, Docs et Tests..."

mkdir -p docs tests .github/workflows

# 1. Le README.md (La vitrine du projet)
cat << 'EOF' > README.md
# 🏭 The ML Factory : Zero-Downtime MLOps Infrastructure

> *« Découpler l'intelligence de l'application pour des mises à jour sans la moindre coupure. »*

Bienvenue dans la **ML Factory**. Ce projet démontre comment orchestrer, versionner et déployer des modèles de Machine Learning de manière dynamique, en garantissant un **Zero-Downtime** lors des mises à jour en production.

## 🏗️ Architecture
* 🗄️ **MinIO** : Stockage objet persistant (Artefacts S3).
* 📖 **MLflow** : Registre de modèles et gestion des alias (`@production`).
* 🧠 **FastAPI** : API REST avec système de rechargement à chaud (Hot-Reload).
* 🎨 **Streamlit** : Interface utilisateur interactive.
EOF

# 2. Configuration Sphinx (docs/conf.py)
cat << 'EOF' > docs/conf.py
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'ML Factory'
copyright = '2026, Équipe MLOps'
author = 'Tech Lead'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'myst_parser',
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}
html_theme = 'sphinx_rtd_theme'
EOF

# 3. Index Sphinx (docs/index.rst) pointant vers le README
cat << 'EOF' > docs/index.rst
🏭 The ML Factory - Documentation
=================================

.. include:: ../README.md
   :parser: myst_parser.sphinx_

.. toctree::
   :maxdepth: 2
   :caption: Code Source & API:
EOF

# 4. Test Unitaire de l'API (tests/test_api.py)
# Indispensable pour que le CI/CD passe avec succès !
cat << 'EOF' > tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.api.main import app, state

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_state():
    state.model = None
    state.version = None

@patch("src.api.main.MlflowClient")
@patch("src.api.main.mlflow.pyfunc.load_model")
def test_predict_success(mock_load_model, MockMlflowClient):
    mock_client_instance = MockMlflowClient.return_value
    mock_client_instance.get_model_version_by_alias.return_value.version = "99"
    
    mock_model = MagicMock()
    mock_model.predict.return_value = [1]
    mock_load_model.return_value = mock_model

    payload = {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}
    response = client.post("/predict", json=payload)

    assert response.status_code == 200
    assert response.json()["prediction"] == 1
    assert response.json()["model_version"] == "99"
EOF

# 5. Le Workflow Ultime DevSecOps (.github/workflows/devsecops.yml)
cat << 'EOF' > .github/workflows/devsecops.yml
name: 🏭 DevSecOps & Documentation Pipeline

on:
  push:
    branches: ["main"]

permissions:
  contents: read
  pages: write
  id-token: write
  packages: write

jobs:
  audit-and-security:
    name: 🛡️ Sécurité & Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: 🕵️‍♂️ Scan de Sécurité (Gitleaks)
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - uses: astral-sh/setup-uv@v2
        with:
          enable-cache: true

      - run: uv python install 3.11
      - run: uv sync

      - name: 🧹 Ruff Check & Format
        run: |
          uv run ruff check .
          uv run ruff format --check .

      - name: 🧪 Tests Pytest
        run: uv run pytest

  deploy-docs:
    name: 📚 Déploiement Sphinx
    needs: audit-and-security
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v2
      - run: uv python install 3.11
      - run: uv sync
      - run: uv run sphinx-build -b html docs docs/_build/html
      - uses: actions/upload-pages-artifact@v3
        with:
          path: docs/_build/html
      - id: deployment
        uses: actions/deploy-pages@v4

  build-and-push-docker:
    name: 🐳 CD Docker (GHCR)
    needs: audit-and-security
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: 🔑 Login GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: 🏗️ Variables
        run: echo "REPO_LOWER=$(echo "${{ github.repository }}" | tr '[:upper:]' '[:lower:]')" >> $GITHUB_ENV

      - name: 🚀 Push API
        uses: docker/build-push-action@v5
        with:
          context: .
          file: src/api/Dockerfile
          push: true
          tags: ghcr.io/${{ env.REPO_LOWER }}/mlfactory-api:latest

      - name: 🚀 Push Front
        uses: docker/build-push-action@v5
        with:
          context: .
          file: src/front/Dockerfile
          push: true
          tags: ghcr.io/${{ env.REPO_LOWER }}/mlfactory-front:latest
EOF

echo "✅ Fichiers injectés avec succès !"