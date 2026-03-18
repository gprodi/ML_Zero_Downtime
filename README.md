# 🏭 The ML Factory : MLOps & Zero-Downtime Architecture

[![CI/CD Pipeline](https://github.com/gprodi/ML_Zero_Downtime/actions/workflows/devsecops.yml/badge.svg)](https://github.com/gprodi/ML_Zero_Downtime/actions)
![Python](https://img.shields.io/badge/Python-3.11-blue.svg?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg?logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Front-Streamlit-FF4B4B.svg?logo=streamlit&logoColor=white)
![Security](https://img.shields.io/badge/Security-Gitleaks-8A2BE2.svg)
![Linter](https://img.shields.io/badge/Linter-Ruff-success.svg)

> *« Découpler l'intelligence de l'application pour des déploiements sans la moindre coupure. »*

Bienvenue dans la **ML Factory**. Ce projet est un laboratoire d'excellence MLOps démontrant comment orchestrer, versionner et déployer des modèles de Machine Learning de manière dynamique. L'architecture garantit un **Zero-Downtime** (aucune interruption de service) lors des mises à jour en production.

---

## 🏗️ Architecture du Système

Le système repose sur une isolation stricte des responsabilités (Separation of Concerns) :

1. 🗄️ **MinIO (Le Hangar S3)** : Stockage objet persistant hébergeant les artefacts binaires des modèles entraînés.
2. 📖 **MLflow (Le Registre)** : Le catalogue central traquant les expérimentations et gérant le cycle de vie des modèles via un système d'alias (`@production`).
3. 🧠 **FastAPI (L'Usine / Serving)** : API REST robuste qui ne fige pas de modèle au démarrage, mais interroge dynamiquement le registre pour télécharger le modèle actif à chaud (*hot-reload*).
4. 🎨 **Streamlit (La Vitrine)** : Interface utilisateur conviviale traduisant les prédictions mathématiques brutes en vocabulaire métier.

---

## 📂 Arborescence du Projet

```text
📦 ml-factory
 ┣ 📂 .github/workflows/    # Pipelines CI/CD DevSecOps (Gitleaks, Ruff, Pytest, Docker GHCR)
 ┣ 📂 docs/                 # Documentation technique générée dynamiquement par Sphinx
 ┣ 📂 src/
 ┃ ┣ 📂 api/                # Code source et Dockerfile de l'API FastAPI
 ┃ ┣ 📂 front/              # Code source et Dockerfile de l'interface Streamlit
 ┃ ┗ 📂 train/              # Scripts locaux d'entraînement des modèles (Data Science)
 ┣ 📂 tests/                # Tests unitaires mockés pour l'API
 ┣ 📜 .dockerignore         # Exclusions pour alléger les images Docker de production
 ┣ 📜 .gitignore            # Sécurité et exclusions Git
 ┣ 📜 docker-compose.yml    # Orchestration de l'infrastructure locale
 ┣ 📜 pyproject.toml        # Configuration centrale (dépendances uv, pytest, ruff)
 ┗ 📜 README.md             # Ce document
````

---

## 🚀 Guide de Démarrage Rapide

### 1\. Prérequis

Pour exécuter ce projet localement, vous devez installer :

* [Docker](https://www.docker.com/) et **Docker Compose**
* [uv](https://github.com/astral-sh/uv) (Le gestionnaire de paquets Python ultra-rapide écrit en Rust)

### 2\. Cloner le dépôt et sécuriser l'environnement

Clonez le projet sur votre machine locale :

```bash
git clone https://github.com/gprodi/ML_Zero_Downtime
cd ML_Zero_Downtime
```

⚠️ **Étape critique :** Créez un fichier `.env` à la racine du projet. Ce fichier contient vos secrets locaux et est ignoré par Git pour des raisons de sécurité.

```env
# Contenu du fichier .env
MINIO_ROOT_USER=mlops_admin
MINIO_ROOT_PASSWORD=SuperSecretPassword123!
AWS_ACCESS_KEY_ID=mlops_admin
AWS_SECRET_ACCESS_KEY=SuperSecretPassword123!
MLFLOW_S3_ENDPOINT_URL=http://minio:9000
MLFLOW_TRACKING_URI=http://mlflow:5000
API_URL=http://api:8000
```

### 3\. Allumage de l'Infrastructure Docker

Lancez les conteneurs (l'API démarrera mais renverra une erreur `503 Service Unavailable` tant qu'aucun modèle n'est en production) :

```bash
docker-compose up -d
```

Si c'est votre premier lancement, initialisez le bucket S3 local de MinIO :

```bash
docker-compose up createbuckets
```

### 4\. Entraînement et Injection du Premier Modèle

Installez les dépendances locales de Data Science et lancez l'entraînement. Le script va générer le modèle, l'envoyer dans MinIO, et demander à MLflow de le marquer comme "production".

```bash
uv sync
uv run src/train/train.py
```

*L'API détectera automatiquement ce nouveau modèle et se mettra à jour en silence (Hot-Reload).*

---

## 🌐 Accès aux Services Locaux

Une fois l'infrastructure démarrée et le modèle injecté, accédez à vos interfaces :

* 🌺 **Application Streamlit (Utilisateur)** : [http://localhost:8501](https://www.google.com/search?q=http://localhost:8501)
* 📖 **UI MLflow (Registre ML)** : [http://localhost:5000](https://www.google.com/search?q=http://localhost:5000)
* 🗄️ **Console MinIO (Stockage S3)** : [http://localhost:9001](https://www.google.com/search?q=http://localhost:9001) *(Login: mlops\_admin / SuperSecretPassword123\!)*
* ⚙️ **FastAPI Swagger (Documentation API)** : [http://localhost:8000/docs](https://www.google.com/search?q=http://localhost:8000/docs)

---

## 🛡️ Pipeline DevSecOps & CI/CD

Chaque `git push` vers la branche principale déclenche un pipeline industriel sur GitHub Actions :

1. **Sécurité (SAST)** : Scan de fuite de mots de passe via `Gitleaks`.
2. **Qualité** : Audit syntaxique strict et formatage via `Ruff`.
3. **Tests** : Exécution des tests unitaires mockés de l'API via `Pytest`.
4. **Documentation** : Compilation et déploiement du site statique `Sphinx` sur GitHub Pages.
5. **Déploiement Continu (CD)** : Construction automatique des images Docker et publication sur le **GitHub Container Registry (GHCR)**.

<!-- end list -->
