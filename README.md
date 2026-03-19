# 🏭 The ML Factory : MLOps & Zero-Downtime Architecture

[![CI/CD Pipeline](https://github.com/gprodi/ML_Zero_Downtime/actions/workflows/devsecops.yml/badge.svg)](https://github.com/gprodi/ML_Zero_Downtime/actions)
![Python](https://img.shields.io/badge/Python-3.11-blue.svg?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg?logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Front-Streamlit-FF4B4B.svg?logo=streamlit&logoColor=white)
![Prefect](https://img.shields.io/badge/Orchestration-Prefect-ffffff.svg?logo=prefect&logoColor=blue)
![Security](https://img.shields.io/badge/Security-Gitleaks-8A2BE2.svg)

> *« Découpler l'intelligence de l'application pour des déploiements sans la moindre coupure. »*

Bienvenue dans la **ML Factory**. Ce projet est un laboratoire d'excellence MLOps démontrant comment orchestrer, versionner et déployer des modèles de Machine Learning de manière dynamique. L'architecture garantit un **Zero-Downtime** (aucune interruption de service) lors des mises à jour en production et une **automatisation totale** du ré-entraînement.

---

## 🏗️ Architecture du Système

Le système repose sur une isolation stricte des responsabilités (Separation of Concerns) :

1. 🗄️ **MinIO (Le Hangar S3)** : Stockage objet persistant hébergeant les artefacts binaires des modèles entraînés.
2. 📖 **MLflow (Le Registre)** : Le catalogue central traquant les expérimentations et gérant le cycle de vie des modèles via un système d'alias (`@production`).
3. 🧠 **FastAPI (L'Usine / Serving)** : API REST robuste qui ne fige pas de modèle au démarrage, mais interroge dynamiquement le registre pour télécharger le modèle actif à chaud (*hot-reload*).
4. 🎨 **Streamlit (La Vitrine)** : Interface utilisateur conviviale acceptant les requêtes unitaires et les envois par lots (Batch processing via CSV).
5. 🤖 **Prefect (L'Orchestrateur)** : Planifie et exécute automatiquement les pipelines d'entraînement des modèles en tâche de fond de manière autonome.

---

## 📂 Arborescence du Projet

```text
📦 ml-factory
 ┣ 📂 .github/workflows/    # Pipelines CI/CD DevSecOps (Gitleaks, Ruff, Pytest, Docker GHCR)
 ┣ 📂 docs/                 # Documentation technique générée dynamiquement par Sphinx
 ┣ 📂 src/
 ┃ ┣ 📂 api/                # Code source et Dockerfile de l'API FastAPI
 ┃ ┣ 📂 front/              # Code source et Dockerfile de l'interface Streamlit
 ┃ ┗ 📂 train/              # Scripts d'entraînement automatisés (Flows Prefect) et Dockerfile
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
* [uv](https://github.com/astral-sh/uv) (Optionnel en local, géré par Docker en production)

### 2\. Cloner le dépôt et sécuriser l'environnement

Clonez le projet sur votre machine locale :

```bash
git clone [https://github.com/gprodi/ML_Zero_Downtime](https://github.com/gprodi/ML_Zero_Downtime)
cd ML_Zero_Downtime
```

⚠️ **Étape critique :** Créez un fichier `.env` à la racine du projet pour la gestion sécurisée des identifiants et du réseau.

```env
# Contenu du fichier .env
MINIO_ROOT_USER=mlops_admin
MINIO_ROOT_PASSWORD=SuperSecretPassword123!
AWS_ACCESS_KEY_ID=mlops_admin
AWS_SECRET_ACCESS_KEY=SuperSecretPassword123!
MLFLOW_S3_ENDPOINT_URL=http://minio:9000
MLFLOW_TRACKING_URI=http://mlflow:5000
API_URL=http://api:8000
PREFECT_API_URL=http://localhost:4200/api
```

### 3\. Allumage de l'Infrastructure Docker

Lancez l'intégralité des microservices (API, Front, MLflow, MinIO, Prefect, Train Worker) :

```bash
docker-compose up -d
```

*(Si c'est votre premier lancement, n'oubliez pas d'initialiser le bucket S3 local via `docker-compose up createbuckets`)*

### 4\. Déclenchement de l'Entraînement Automatisé

L'infrastructure intègre un démon d'entraînement autonome. Le pipeline est programmé pour tourner automatiquement en tâche de fond chaque nuit.

Cependant, pour forcer le premier entraînement et injecter le modèle en production immédiatement :

1. Ouvrez le tableau de bord Prefect : [http://localhost:4200](https://www.google.com/search?q=http://localhost:4200)
2. Allez dans l'onglet **Deployments**.
3. Trouvez le déploiement `iris-nightly-training` et cliquez sur le bouton **Run** (ou *Quick Run*).
4. Allez dans **Flow Runs** pour observer les tâches s'exécuter en temps réel.

*Dès que Prefect valide la précision du modèle, l'API FastAPI le télécharge et se met à jour en silence (Hot-Reload).*

---

## 🌐 Accès aux Services Locaux

Une fois l'infrastructure démarrée, supervisez votre usine via ces tableaux de bord :

* 🌺 **Application Streamlit (Utilisateur)** : [http://localhost:8501](https://www.google.com/search?q=http://localhost:8501)
* 🤖 **UI Prefect (Orchestration)** : [http://localhost:4200](https://www.google.com/search?q=http://localhost:4200)
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
5. **Déploiement Continu (CD)** : Construction automatique de l'ensemble des images Docker (API, Front, Train) et publication sur le **GitHub Container Registry (GHCR)**.

<!-- end list -->
