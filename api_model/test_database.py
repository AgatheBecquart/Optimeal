from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker, Session
from api_model.database import Base, DBpredictions
from datetime import datetime
from typing import Generator
import pytest
import warnings
from pydantic import PydanticDeprecatedSince20

warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)


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
    yield db_session
    db_session.close()
    Base.metadata.drop_all(bind=engine)


def test_create_prediction(session: Session):
    mock_prediction = {
        "prediction": 100,
        "temperature": 25.5,
        "nb_presence_sur_site": 350,
        "id_jour": "2024-09-19",
        "timestamp": datetime.now().isoformat(),
        "model": "test_model",
    }

    new_prediction = DBpredictions(**mock_prediction)
    session.add(new_prediction)
    session.commit()

    prediction_in_db = session.query(DBpredictions).first()
    assert prediction_in_db is not None
    assert prediction_in_db.prediction == 100
    assert prediction_in_db.temperature == 25.5
    assert prediction_in_db.nb_presence_sur_site == 350
    assert prediction_in_db.model == "test_model"
