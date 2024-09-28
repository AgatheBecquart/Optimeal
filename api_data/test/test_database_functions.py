from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker, Session
from api_data.database.core import Base, DBCanteenEmployeesUser
from typing import Generator
from api_data.database.canteen_employees import (
    CanteenEmployeeUserCreate,
    create_db_canteen_employee_user,
    generate_id,
)
from api_data.database.authentificate import UserCreate, create_db_user
import pytest
from passlib.context import CryptContext


@pytest.fixture
def session() -> Generator[Session, None, None]:
    TEST_DATABASE_URL = "sqlite:///:memory:"

    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()

    # Créer un employé de cantine de test
    db_canteen_employee = DBCanteenEmployeesUser(
        employee_id=generate_id(),
        employee_unique_id="4321",
        employee_username="johndoe",
        employee_password="hashed_password",
        employee_email="john.doe@example.com",
        employee_first_name="John",
        employee_last_name="Doe",
        employee_zip_code_prefix="75000",
        employee_city="Paris",
        employee_state="Île-de-France",
    )
    db_session.add(db_canteen_employee)
    db_session.commit()

    yield db_session

    db_session.close()
    Base.metadata.drop_all(bind=engine)


def test_create_canteen_employee(session: Session) -> None:
    canteen_employee = create_db_canteen_employee_user(
        CanteenEmployeeUserCreate(
            employee_unique_id="861eff4711a542e4b93843c6dd7febb0",
            employee_username="janesmith",
            employee_password="password123",
            employee_email="jane.smith@example.com",
            employee_first_name="Jane",
            employee_last_name="Smith",
            employee_zip_code_prefix="69000",
            employee_city="Lyon",
            employee_state="Auvergne-Rhône-Alpes",
        ),
        session,
    )
    assert len(canteen_employee.employee_id) == 14
    assert canteen_employee.employee_unique_id == "861eff4711a542e4b93843c6dd7febb0"
    assert canteen_employee.employee_username == "janesmith"
    assert canteen_employee.employee_email == "jane.smith@example.com"
    assert canteen_employee.employee_first_name == "Jane"
    assert canteen_employee.employee_last_name == "Smith"
    assert canteen_employee.employee_zip_code_prefix == "69000"
    assert canteen_employee.employee_city == "Lyon"
    assert canteen_employee.employee_state == "Auvergne-Rhône-Alpes"


def test_create_user(session: Session) -> None:
    user = create_db_user(
        UserCreate(
            username="test_user",
            email="test_user@test.com",
            full_name="test_user_fullname",
            password="test_password",
        ),
        session,
    )

    assert user.username == "test_user"
    assert user.email == "test_user@test.com"
    assert user.full_name == "test_user_fullname"
    assert user.disabled == False
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    assert pwd_context.verify("test_password", user.hashed_password)
