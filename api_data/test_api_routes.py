from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker, Session
from api_data.database.core import Base, get_db, DBCanteenEmployeesUser
from api_data.database.authentificate import create_db_user, UserCreate
from api_data.database.canteen_employees import generate_id
from api_data.main import app
from typing import Generator
import pytest
from unittest.mock import MagicMock

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def session() -> Generator[Session, None, None]:

    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()

    # create test canteen employee
    db_canteen_employee = DBCanteenEmployeesUser(
        employee_id=generate_id(),
        employee_unique_id="12345",
        employee_username="johndoe",
        employee_password="hashed_password",
        employee_email="john.doe@example.com",
        employee_first_name="John",
        employee_last_name="Doe",
        employee_zip_code_prefix="59000",
        employee_city="Lille",
        employee_state="HDF",
    )

    db_session.add(db_canteen_employee)
    db_session.commit()

    # create test user
    create_db_user(
        UserCreate(
            username="test_user",
            email="test_user@test.com",
            full_name="test_user_fullname",
            password="test_password",
        ),
        db_session,
    )

    yield db_session

    db_session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=False)
def valid_token(monkeypatch):
    monkeypatch.setattr("jose.jwt.decode", MagicMock(return_value={"sub": "test_user"}))


client = TestClient(app)


def override_get_db():
    database = TestingSessionLocal()
    yield database
    database.close()


app.dependency_overrides[get_db] = override_get_db


def test_read_root(session: Session):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "Server is running."


def test_create_canteen_employee_unauthorize(session: Session):
    response = client.post(
        "/employees/",
        json={
            "employee_unique_id": "67890",
            "employee_username": "janesmith",
            "employee_password": "password123",
            "employee_email": "jane.smith@example.com",
            "employee_first_name": "Jane",
            "employee_last_name": "Smith",
            "employee_zip_code_prefix": "75000",
            "employee_city": "Paris",
            "employee_state": "IDF",
        },
    )
    assert response.status_code == 401, response.text


def test_create_improper_canteen_employee(session: Session, valid_token):
    response = client.post(
        "/employees/",
        json={
            "employee_unique_id": "67890",
            "employee_username": "janesmith",
            "employee_email": "jane.smith@example.com",
        },
        headers={"Authorization": f"Bearer {'mocked_token'}"},
    )
    assert response.status_code == 422, response.text


def test_create_canteen_employee(session: Session, valid_token):
    response = client.post(
        "/employees/",
        json={
            "employee_unique_id": "67890",
            "employee_username": "janesmith",
            "employee_password": "password123",
            "employee_email": "jane.smith@example.com",
            "employee_first_name": "Jane",
            "employee_last_name": "Smith",
            "employee_zip_code_prefix": "75000",
            "employee_city": "Paris",
            "employee_state": "IDF",
        },
        headers={"Authorization": f"Bearer {'mocked_token'}"},
    )
    assert response.status_code == 200, response.text


####  Authentification


def test_create_user(session: Session):
    response = client.post(
        "/auth/create_user",
        json={
            "username": "test_user_2",
            "email": "test_user@test.com",
            "full_name": "test_user_fullname",
            "password": "test_password",
        },
    )
    assert response.status_code == 200, response.text
    assert "username" in response.json()


def test_login_for_access_token(session):
    response = client.post(
        "/auth/token", data={"username": "test_user", "password": "test_password"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_is_authorized(session: Session, valid_token):
    response = client.get(
        "/auth/is_authorized/", headers={"Authorization": f"Bearer {'mocked_token'}"}
    )
    assert response.status_code == 200
    assert response.json() == True
