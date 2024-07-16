from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from dotenv import load_dotenv
import os
from sqlalchemy import VARCHAR

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Utiliser les variables d'environnement pour les paramètres de connexion
server = os.getenv("SERVER")
database = os.getenv("DATABASE")
user = os.getenv("AZUREUSER")
password = os.getenv("PASSWORD")

DATABASE_URL= f"mssql+pyodbc://{user}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&timeout=90"

class NotFoundError(Exception):
    pass


class Base(DeclarativeBase):
    pass



class DBCanteenEmployees(Base):

    __tablename__ = "canteen_employees"

    employee_id: Mapped[str] = mapped_column(primary_key=True, index=True, type_=VARCHAR(50))
    employee_unique_id: Mapped[str]
    employee_zip_code_prefix: Mapped[str] 
    employee_city: Mapped[str]
    employee_state: Mapped[str]



class DBUsers(Base):

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(primary_key=True, index=True, type_=VARCHAR(50))
    email: Mapped[str]
    full_name: Mapped[str]
    disabled: Mapped[bool] = mapped_column(default=False)
    hashed_password: Mapped[str]

class DBToken(Base):

    __tablename__ = "tokens"

    username: Mapped[str] = mapped_column(primary_key=True, index=True, type_=VARCHAR(50))

engine = create_engine(DATABASE_URL)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    database = session_local()
    try:
        yield database
    finally:
        database.close()
