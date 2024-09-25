from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Utiliser les variables d'environnement pour les paramètres de connexion
server = os.getenv("SERVER")
database = os.getenv("DATABASE")
user = os.getenv("AZUREUSER")
password = os.getenv("PASSWORD")

# Créer une connexion à la base de données
engine = create_engine(
    f"mssql+pyodbc://{user}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
)


# Liste des commandes SQL
sql_commands = [
    """
SELECT * FROM Meteo """
]

# Exécuter chaque commande SQL
with engine.connect() as conn:
    for sql_command in sql_commands:
        conn.execute(text(sql_command))


# Fermer la connexion
conn.close()
