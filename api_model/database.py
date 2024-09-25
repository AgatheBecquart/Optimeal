from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm import Session
import string
import random
from datetime import datetime

from sqlalchemy import create_engine
from dotenv import load_dotenv
import os


def connect_to_database():
    load_dotenv()
    # Define your PostgreSQL connection parameters
    hostname = os.getenv("SERVER")
    database = os.getenv("DATABASE")
    username = os.getenv("AZUREUSER")
    password = os.getenv("PASSWORD")

    # Créer la chaîne de connexion
    azure_connection_string = f"mssql+pyodbc://{username}:{password}@{hostname}/{database}?driver=ODBC+Driver+17+for+SQL+Server"

    # Créer le moteur SQLAlchemy
    connection = create_engine(azure_connection_string)

    return connection


class Base(DeclarativeBase):
    pass


class DBpredictions(Base):

    __tablename__ = "predictions"

    prediction_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    timestamp: Mapped[str]
    temperature: Mapped[float]
    nb_presence_sur_site: Mapped[float]
    id_jour: Mapped[str]
    prediction: Mapped[int]
    model: Mapped[str]


# Dependency to get the database session


def get_db():
    engine = connect_to_database()
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    database = session_local()
    try:
        yield database
    finally:
        database.close()


# def generate_id():
#     """Generate a unique string ID."""
#     length = 14
#     characters = string.ascii_letters + string.digits
#     return ''.join(random.choice(characters) for i in range(length))


def generate_id(length=6):
    """Generate a unique numeric ID."""
    characters = string.digits  # Utilise uniquement les chiffres 0-9
    return "".join(random.choice(characters) for _ in range(length))


def create_db_prediction(prediction: dict, session: Session) -> DBpredictions:
    db_prediction = DBpredictions(**prediction, prediction_id=generate_id())
    session.add(db_prediction)
    session.commit()
    session.refresh(db_prediction)
    return db_prediction


if __name__ == "__main__":
    engine = connect_to_database()
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
