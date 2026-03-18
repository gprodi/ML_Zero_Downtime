# rebuild.sh
#!/bin/bash
echo "🚀 Démarrage du Protocole Phénix : Reconstruction de la ML Factory..."

# 1. Création de l'arborescence
mkdir -p src/api src/front src/train .github/workflows docs tests data
touch src/__init__.py src/api/__init__.py tests/__init__.py

# 2. Fichier .env
cat << 'EOF' > .env
MINIO_ROOT_USER=mlops_admin
MINIO_ROOT_PASSWORD=SuperSecretPassword123!
AWS_ACCESS_KEY_ID=mlops_admin
AWS_SECRET_ACCESS_KEY=SuperSecretPassword123!
MLFLOW_S3_ENDPOINT_URL=http://minio:9000
MLFLOW_TRACKING_URI=http://mlflow:5000
API_URL=http://api:8000
EOF

# 3. Fichier pyproject.toml (Configuration uv, pytest, ruff)
cat << 'EOF' > pyproject.toml
[project]
name = "ml-factory"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi", "uvicorn", "pydantic", "mlflow", "scikit-learn", 
    "boto3", "streamlit", "requests", "loguru"
]

[tool.uv]
dev-dependencies = ["pytest", "httpx", "ruff", "sphinx", "sphinx-rtd-theme", "myst-parser"]

[tool.pytest.ini_options]
pythonpath = ["."]

[tool.ruff]
line-length = 100
[tool.ruff.lint]
select = ["E", "F", "I"]
EOF

# 4. Fichier docker-compose.yml
cat << 'EOF' > docker-compose.yml
services:
  minio:
    image: minio/minio
    ports: ["9000:9000", "9001:9001"]
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
    command: server /data --console-address ":9001"
    volumes: ["minio_data:/data"]

  createbuckets:
    image: minio/mc
    depends_on: [minio]
    entrypoint: >
      /bin/sh -c "sleep 5; /usr/bin/mc config host add myminio http://minio:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}; /usr/bin/mc mb myminio/mlflow --ignore-existing; exit 0;"

  mlflow:
    image: python:3.11-slim
    ports: ["5000:5000"]
    depends_on: [minio]
    environment:
      AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
      AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
      MLFLOW_S3_ENDPOINT_URL: ${MLFLOW_S3_ENDPOINT_URL}
    command: >
      /bin/sh -c "pip install mlflow boto3 && mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root s3://mlflow/ --host 0.0.0.0 --allowed-hosts 'mlflow:5000,localhost:5000'"

  api:
    build:
      context: .
      dockerfile: src/api/Dockerfile
    ports: ["8000:8000"]
    depends_on: [mlflow]
    environment:
      MLFLOW_TRACKING_URI: ${MLFLOW_TRACKING_URI}
      AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
      AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
      MLFLOW_S3_ENDPOINT_URL: ${MLFLOW_S3_ENDPOINT_URL}

  front:
    build:
      context: .
      dockerfile: src/front/Dockerfile
    ports: ["8501:8501"]
    depends_on: [api]
    environment:
      API_URL: ${API_URL}

volumes:
  minio_data:
EOF

# 5. L'API FastAPI (src/api/main.py)
cat << 'EOF' > src/api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow.pyfunc
from mlflow.tracking import MlflowClient
import sys
from loguru import logger

logger.remove()
logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>", level="INFO")

app = FastAPI()
class ModelState:
    def __init__(self):
        self.model = None
        self.version = None

state = ModelState()
MODEL_NAME = "iris_classifier"
ALIAS = "production"

class PredictRequest(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

def refresh_model():
    client = MlflowClient()
    try:
        model_info = client.get_model_version_by_alias(MODEL_NAME, ALIAS)
        if state.version != model_info.version:
            logger.info(f"Changement d'alias détecté. Téléchargement V{model_info.version}...")
            state.model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}@{ALIAS}")
            state.version = model_info.version
            logger.success(f"Modèle V{state.version} chargé en mémoire ! 🚀")
    except Exception as e:
        logger.error(f"Erreur MLflow/MinIO : {str(e)}")
        if state.model is None:
            raise HTTPException(status_code=503, detail="Modèle indisponible.")
        logger.warning(f"Utilisation de secours (V{state.version}).")

@app.post("/predict")
def predict(request: PredictRequest):
    refresh_model()
    data = [[request.sepal_length, request.sepal_width, request.petal_length, request.petal_width]]
    prediction = state.model.predict(data)[0]
    return {"prediction": int(prediction), "model_version": state.version}
EOF

# 6. Dockerfile API
cat << 'EOF' > src/api/Dockerfile
FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --system
COPY src/api ./src/api
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# 7. Streamlit Front (src/front/main.py)
cat << 'EOF' > src/front/main.py
import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("🌺 Identificateur d'Iris (Zero-Downtime)")
with st.form("prediction_form"):
    sl = st.number_input("Sepal Length", 0.0, 10.0, 5.1)
    sw = st.number_input("Sepal Width", 0.0, 10.0, 3.5)
    pl = st.number_input("Petal Length", 0.0, 10.0, 1.4)
    pw = st.number_input("Petal Width", 0.0, 10.0, 0.2)
    submitted = st.form_submit_button("Prédire")

if submitted:
    payload = {"sepal_length": sl, "sepal_width": sw, "petal_length": pl, "petal_width": pw}
    IRIS_CLASSES = {0: "Iris Setosa", 1: "Iris Versicolor", 2: "Iris Virginica"}
    try:
        response = requests.post(f"{API_URL}/predict", json=payload)
        response.raise_for_status()
        res = response.json()
        nom_espece = IRIS_CLASSES.get(res['prediction'], "Inconnue")
        st.success(f"Espèce : **{nom_espece}**")
        st.info(f"Modèle : V{res['model_version']}")
    except Exception as e:
        st.error("L'API est indisponible.")
EOF

# 8. Dockerfile Front
cat << 'EOF' > src/front/Dockerfile
FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --system
COPY src/front ./src/front
CMD ["streamlit", "run", "src/front/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
EOF

# 9. Script d'Entraînement (src/train/train.py)
cat << 'EOF' > src/train/train.py
import os
import mlflow
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from mlflow.tracking import MlflowClient

os.environ["MLFLOW_TRACKING_URI"] = "http://localhost:5000"
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://localhost:9000"
os.environ["AWS_ACCESS_KEY_ID"] = "mlops_admin"
os.environ["AWS_SECRET_ACCESS_KEY"] = "SuperSecretPassword123!"

MODEL_NAME = "iris_classifier"

if __name__ == "__main__":
    mlflow.set_experiment("iris_experiment")
    X, y = load_iris(return_X_y=True)
    
    with mlflow.start_run():
        model = LogisticRegression(max_iter=200)
        # model = RandomForestClassifier(n_estimators=100) # Pour la Phase 2
        model.fit(X, y)
        mlflow.sklearn.log_model(model, "model", registered_model_name=MODEL_NAME)
    
    client = MlflowClient()
    latest_version = client.get_latest_versions(MODEL_NAME, stages=["None"])[0].version
    client.set_registered_model_alias(MODEL_NAME, "production", latest_version)
    print(f"✅ Modèle V{latest_version} enregistré en production !")
EOF

# 10. Initialisation de uv.lock
uv lock

echo "✨ Reconstruction terminée avec succès ! Le phénix est rené de ses cendres."