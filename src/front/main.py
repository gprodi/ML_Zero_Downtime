import os

import requests
import streamlit as st  # type: ignore

# Configuration de l'URL de l'API (via Docker ou localhost)
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Configuration de la page
st.set_page_config(page_title="ML Factory", page_icon="🌺", layout="centered")

st.title("🌺 Identificateur d'Iris (Zero-Downtime)")
st.markdown(
    "Cette interface interroge notre API FastAPI dynamique en temps réel. Remarquez la version du modèle qui s'affiche sous la prédiction."  # noqa: E501
)

with st.form("prediction_form"):
    st.subheader("Saisissez les caractéristiques botaniques")

    col1, col2 = st.columns(2)
    with col1:
        sl = st.number_input("Longueur du sépale (cm)", 0.0, 10.0, 5.1)
        pl = st.number_input("Longueur du pétale (cm)", 0.0, 10.0, 1.4)
    with col2:
        sw = st.number_input("Largeur du sépale (cm)", 0.0, 10.0, 3.5)
        pw = st.number_input("Largeur du pétale (cm)", 0.0, 10.0, 0.2)

    submitted = st.form_submit_button("Prédire l'espèce", use_container_width=True)

if submitted:
    payload = {"sepal_length": sl, "sepal_width": sw, "petal_length": pl, "petal_width": pw}

    # Le dictionnaire de traduction pour passer des mathématiques au vocabulaire métier
    IRIS_CLASSES = {0: "Iris Setosa", 1: "Iris Versicolor", 2: "Iris Virginica"}

    try:
        with st.spinner("Interrogation de l'usine..."):
            response = requests.post(f"{API_URL}/predict", json=payload)
            response.raise_for_status()
            res = response.json()

            # Extraction et traduction de la classe numérique
            prediction_brute = res["prediction"]
            nom_espece = IRIS_CLASSES.get(prediction_brute, "Espèce Inconnue")

            # Affichage des résultats avec bannières
            st.success(f"🌿 L'espèce identifiée est : **{nom_espece}**")
            st.info(
                f"🧠 Propulsé par la **Version {res['model_version']}** du modèle en production."
            )

    except Exception as e:
        st.error(
            "🚨 Impossible de contacter l'API. Vérifiez que le conteneur tourne et qu'un modèle est en production."  # noqa: E501
        )
        st.exception(e)
