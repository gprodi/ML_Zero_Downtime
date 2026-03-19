import os

import mlflow
from dotenv import load_dotenv
from mlflow.tracking import MlflowClient
from prefect import flow, task
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

# 🧠 Importation de nos 3 "Gladiateurs"
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

# 1. 🛡️ SÉCURITÉ ET RÉSEAU DYNAMIQUE
load_dotenv()

# Astuce DevOps : On détecte si le script tourne sur votre PC ou dans un conteneur Docker
if not os.path.exists("/.dockerenv"):
    # Nous sommes sur Windows : On force les adresses locales pour contourner le .env
    os.environ["MLFLOW_TRACKING_URI"] = "http://localhost:5000"
    os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://localhost:9000"
else:
    # Nous sommes dans Docker : On utilise le réseau interne
    os.environ["MLFLOW_TRACKING_URI"] = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
    os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv("MLFLOW_S3_ENDPOINT_URL", "http://minio:9000")

os.environ["PREFECT_API_URL"] = os.getenv("PREFECT_API_URL", "http://localhost:4200/api")

MODEL_NAME = "iris_classifier"

# ==========================================
# 🧱 DÉFINITION DES TÂCHES (TASKS)
# ==========================================


@task(name="Chargement des données", retries=2, retry_delay_seconds=5)
def load_and_split_data():
    X, y = load_iris(return_X_y=True)
    return train_test_split(X, y, test_size=0.2, random_state=42)


@task(name="Combat des Modèles (Entraînement)")
def train_and_evaluate(X_train, X_test, y_train, y_test, model_name, model_instance):
    """Entraîne UN modèle spécifique et renvoie son score et son ID de run MLflow."""
    mlflow.set_experiment("iris_experiment")

    # On donne un nom à la run pour la retrouver facilement dans MLflow
    with mlflow.start_run(run_name=model_name) as run:
        mlflow.log_param("algorithm", model_name)

        # Entraînement et Prédiction
        model_instance.fit(X_train, y_train)
        predictions = model_instance.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)

        mlflow.log_metric("accuracy", accuracy)

        # On sauvegarde l'artefact dans cette Run spécifique (mais sans l'enregistrer en production tout de suite)  # noqa: E501
        mlflow.sklearn.log_model(model_instance, "model")

        # On renvoie le score ET l'identifiant unique de cette tentative
        return accuracy, run.info.run_id


@task(name="Couronnement du Vainqueur")
def register_best_model(best_run_id):
    """Prend le Run ID du modèle gagnant, l'enregistre, et le met en production."""
    # 1. Enregistrement du modèle vainqueur dans le registre
    model_uri = f"runs:/{best_run_id}/model"
    result = mlflow.register_model(model_uri, MODEL_NAME)

    # 2. Assignation de l'alias "production"
    client = MlflowClient()
    client.set_registered_model_alias(MODEL_NAME, "production", result.version)
    return result.version


# ==========================================
# 🌊 DÉFINITION DU PIPELINE (FLOW)
# ==========================================


@flow(name="AutoML Pipeline d'Entraînement", log_prints=True)
def main_training_flow():
    print("🚀 Démarrage de l'arène AutoML...")
    X_train, X_test, y_train, y_test = load_and_split_data()

    # 🥊 Nos 3 concurrents
    models_to_test = {
        "LogisticRegression": LogisticRegression(max_iter=200),
        "DecisionTree": DecisionTreeClassifier(max_depth=5, random_state=42),
        "RandomForest": RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42),
    }

    best_accuracy = 0.0
    best_run_id = None
    best_model_name = ""

    # On fait combattre chaque modèle un par un
    for name, model in models_to_test.items():
        print(f"🔄 Entraînement en cours : {name}...")
        acc, run_id = train_and_evaluate(X_train, X_test, y_train, y_test, name, model)
        print(f"📊 {name} a obtenu : {acc:.4f}")

        # On met à jour le champion en titre
        if acc > best_accuracy:
            best_accuracy = acc
            best_run_id = run_id
            best_model_name = name

    print(f"🏆 Le grand gagnant est {best_model_name} avec {best_accuracy:.4f} !")

    # La barrière de sécurité finale
    if best_accuracy >= 0.80:
        print("✅ Le gagnant a le niveau requis. Déploiement en production...")
        version = register_best_model(best_run_id)
        print(f"🚀 Modèle V{version} en production !")
    else:
        print("❌ Même le gagnant est trop mauvais (Score < 0.80). Aucun déploiement.")


# ==========================================
# 🤖 EXÉCUTION (LE DÉMON PREFECT)
# ==========================================

if __name__ == "__main__":
    print("🤖 Initialisation du Déploiement Prefect (Mode Serveur)...")
    main_training_flow.serve(
        name="iris-automl-nightly", cron="0 3 * * *", tags=["production", "automl"]
    )
