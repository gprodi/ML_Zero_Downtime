# 🏭 The ML Factory : Zero-Downtime MLOps Infrastructure

> *« Découpler l'intelligence de l'application pour des mises à jour sans la moindre coupure. »*

Bienvenue dans la **ML Factory**. Ce projet démontre comment orchestrer, versionner et déployer des modèles de Machine Learning de manière dynamique, en garantissant un **Zero-Downtime** lors des mises à jour en production.

## 🏗️ Architecture
* 🗄️ **MinIO** : Stockage objet persistant (Artefacts S3).
* 📖 **MLflow** : Registre de modèles et gestion des alias (`@production`).
* 🧠 **FastAPI** : API REST avec système de rechargement à chaud (Hot-Reload).
* 🎨 **Streamlit** : Interface utilisateur interactive.
