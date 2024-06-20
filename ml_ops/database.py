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