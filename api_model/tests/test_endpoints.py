from fastapi.testclient import TestClient
from api_model.main import app
import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import sessionmaker, Session
from api_model.database import Base, DBpredictions, get_db
from typing import Generator
from sqlalchemy import create_engine, StaticPool


@pytest.fixture(autouse=False)
def valid_token(monkeypatch):
    # Mock the jwt.decode function to return the mock payload
    monkeypatch.setattr("jose.jwt.decode", MagicMock(
        return_value={"sub": "admin"}))


@pytest.fixture(autouse=False)
def mock_predict_single(monkeypatch):
    # Mock the jwt.decode function to return the mock payload
    monkeypatch.setattr("api.utils.predict_single", MagicMock(return_value=1))


TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL, connect_args={
                       "check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def session() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()

    yield db_session

    db_session.close()
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)

# Dependency to override the get_db dependency in the main app


def override_get_db():
    database = TestingSessionLocal()
    yield database
    database.close()


app.dependency_overrides[get_db] = override_get_db


def test_train_unauthorize(session: Session):
    data = {"produit_recu": 1, "temps_livraison": 12}
    headers = {"Authorization": "Bearer false_token"}
    response = client.post("predict", json=data, headers=headers)
    assert response.status_code == 401, response.text


def test_predict_single(valid_token, mock_predict_single, session: Session):
    # Assuming SinglePredictionInput is a pydantic model
    data = {"produit_recu": 1, "temps_livraison": 12}
    # Replace with actual input data
    headers = {"Authorization": "Bearer mock_token"}
    response = client.post("predict", json=data, headers=headers)
    assert response.status_code == 200
    # Assuming predict_single returns a valid prediction
    assert "prediction" in response.json()
