import os

import mlflow
from mlflow.tracking import MlflowClient
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

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
        # model = RandomForestClassifier(n_estimators=100)  # Pour la Phase 2
        model.fit(X, y)
        mlflow.sklearn.log_model(model, "model", registered_model_name=MODEL_NAME)

    client = MlflowClient()
    latest_version = client.get_latest_versions(MODEL_NAME, stages=["None"])[0].version
    client.set_registered_model_alias(MODEL_NAME, "production", latest_version)
    print(f"✅ Modèle V{latest_version} enregistré en production !")
