import os  # noqa: F401

import mlflow
from dotenv import load_dotenv
from mlflow.tracking import MlflowClient
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier  # noqa: F401
from sklearn.linear_model import LogisticRegression  # noqa: F401
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# 🛡️ SÉCURITÉ : Chargement des identifiants depuis le fichier .env
# Absolument aucun secret en clair dans le code !
load_dotenv()

# 2. 🌐 RÉSEAU : On force les adresses en localhost (Car ce script tourne hors de Docker)
os.environ["MLFLOW_TRACKING_URI"] = "http://localhost:5000"
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://localhost:9000"

MODEL_NAME = "iris_classifier"

if __name__ == "__main__":
    mlflow.set_experiment("iris_experiment")

    # 1. Chargement et séparation des données (Train / Test)
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    with mlflow.start_run() as run:
        # --- CHOIX DU MODÈLE ---
        # model_type = "LogisticRegression"
        # params = {"max_iter": 200, "C": 1.0}
        # model = LogisticRegression(**params)

        # Modèle B : Random Forest (Forêt Aléatoire)
        model_type = "RandomForest"
        params = {"n_estimators": 100, "max_depth": 5}
        model = RandomForestClassifier(**params)

        # 2. Enregistrement des Paramètres
        mlflow.log_param("model_type", model_type)
        mlflow.log_params(params)

        # 3. Entraînement sur le jeu de Train
        model.fit(X_train, y_train)

        # 4. Prédiction et Évaluation sur le jeu de Test
        predictions = model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)

        # 5. Enregistrement des Métriques
        mlflow.log_metric("accuracy", accuracy)
        print(f"📊 Modèle entraîné : {model_type} | Précision (Accuracy) : {accuracy:.4f}")

        # 6. Sauvegarde du Modèle
        mlflow.sklearn.log_model(model, "model", registered_model_name=MODEL_NAME)

    # --- MISE EN PRODUCTION ---
    client = MlflowClient()
    latest_version = client.get_latest_versions(MODEL_NAME, stages=["None"])[0].version
    client.set_registered_model_alias(MODEL_NAME, "production", latest_version)
    print(f"✅ Modèle V{latest_version} enregistré en production avec succès !")
