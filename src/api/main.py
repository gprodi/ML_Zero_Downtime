import sys

import mlflow.pyfunc
from fastapi import FastAPI, HTTPException
from loguru import logger
from mlflow.tracking import MlflowClient
from pydantic import BaseModel

logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",  # noqa: E501
    level="INFO",
)

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
