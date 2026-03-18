from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.main import app, state

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_state():
    state.model = None
    state.version = None


@patch("src.api.main.MlflowClient")
@patch("src.api.main.mlflow.pyfunc.load_model")
def test_predict_success(mock_load_model, MockMlflowClient):
    mock_client_instance = MockMlflowClient.return_value
    mock_client_instance.get_model_version_by_alias.return_value.version = "99"

    mock_model = MagicMock()
    mock_model.predict.return_value = [1]
    mock_load_model.return_value = mock_model

    payload = {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}
    response = client.post("/predict", json=payload)

    assert response.status_code == 200
    assert response.json()["prediction"] == 1
    assert response.json()["model_version"] == "99"
