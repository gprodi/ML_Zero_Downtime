import os

import mlflow
from dotenv import load_dotenv
from mlflow.tracking import MlflowClient
from prefect import flow, task
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# 1. 🛡️ SÉCURITÉ ET RÉSEAU DYNAMIQUE (Compatible Local ET Docker)
load_dotenv()
os.environ["MLFLOW_TRACKING_URI"] = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv("MLFLOW_S3_ENDPOINT_URL", "http://localhost:9000")
os.environ["PREFECT_API_URL"] = os.getenv("PREFECT_API_URL", "http://localhost:4200/api")

MODEL_NAME = "iris_classifier"

# ==========================================
# 🧱 DÉFINITION DES TÂCHES (TASKS)
# ==========================================


@task(name="Chargement des données", retries=2, retry_delay_seconds=5)
def load_and_split_data():
    X, y = load_iris(return_X_y=True)
    return train_test_split(X, y, test_size=0.2, random_state=42)


@task(name="Entraînement et MLflow")
def train_and_evaluate(X_train, X_test, y_train, y_test):
    mlflow.set_experiment("iris_experiment")

    with mlflow.start_run():
        params = {"max_iter": 200, "C": 1.0}
        model = LogisticRegression(**params)

        mlflow.log_params(params)
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        mlflow.log_metric("accuracy", accuracy)

        mlflow.sklearn.log_model(model, "model", registered_model_name=MODEL_NAME)
        return accuracy


@task(name="Mise en Production")
def promote_to_production():
    client = MlflowClient()
    latest_version = client.get_latest_versions(MODEL_NAME, stages=["None"])[0].version
    client.set_registered_model_alias(MODEL_NAME, "production", latest_version)
    return latest_version


# ==========================================
# 🌊 DÉFINITION DU PIPELINE (FLOW)
# ==========================================


@flow(name="Pipeline Principal d'Entraînement", log_prints=True)
def main_training_flow():
    print("🚀 Démarrage de l'usine d'entraînement automatique...")
    X_train, X_test, y_train, y_test = load_and_split_data()
    accuracy = train_and_evaluate(X_train, X_test, y_train, y_test)

    print(f"📊 Précision obtenue : {accuracy:.4f}")

    if accuracy >= 0.80:
        print("✅ Qualité suffisante. Déploiement en cours...")
        version = promote_to_production()
        print(f"🚀 Modèle V{version} en production !")
    else:
        print("❌ Qualité insuffisante. Le modèle est rejeté.")


# ==========================================
# 🤖 EXÉCUTION (LE DÉMON PREFECT)
# ==========================================

if __name__ == "__main__":
    print("🤖 Initialisation du Déploiement Prefect (Mode Serveur)...")
    main_training_flow.serve(
        name="iris-nightly-training", cron="0 3 * * *", tags=["production", "mlops"]
    )
