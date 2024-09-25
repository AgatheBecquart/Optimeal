from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker, Session
from database.core import Base, DBCanteenEmployees
from typing import Generator
from database.canteen_employees import (
    CanteenEmployeeCreate,
    create_db_canteen_employee,
    generate_id,
)
from database.authentificate import UserCreate, create_db_user
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

    # create test customers
    db_canteen_employee = DBCanteenEmployees(
        canteen_employee_id=generate_id(),
        canteen_employee_unique_id="4321",
        canteen_employee_zip_code_prefix="59000",
        canteen_employee_city="Lille",
        canteen_employee_state="HDF",
    )
    db_session.add(db_canteen_employee)
    db_session.commit()

    yield db_session

    db_session.close()
    Base.metadata.drop_all(bind=engine)


def test_create_customers(session: Session) -> None:
    canteen_employee = create_db_canteen_employee(
        CanteenEmployeeCreate(
            canteen_employee_unique_id="861eff4711a542e4b93843c6dd7febb0",
            canteen_employee_zip_code_prefix="14409",
            canteen_employee_city="franca",
            canteen_employee_state="SP",
        ),
        session,
    )
    assert len(canteen_employee.customer_id) == 14
    assert canteen_employee.customer_unique_id == "861eff4711a542e4b93843c6dd7febb0"
    assert canteen_employee.customer_zip_code_prefix == "14409"
    assert canteen_employee.customer_city == "franca"
    assert canteen_employee.customer_state == "SP"


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
