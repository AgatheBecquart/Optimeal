import pyodbc
from dotenv import load_dotenv
import os

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Utiliser les variables d'environnement pour les paramètres de connexion
server = os.getenv("SERVER")
database = os.getenv("DATABASE")
user = os.getenv("AZUREUSER")
password = os.getenv("PASSWORD")

# Chaîne de connexion à la base de données
conn_str = f"DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};UID={user};PWD={password}"

# Liste des tables à supprimer
tables_to_drop = ["Meteo", "RepasVendus", "PresenceRH"]

# Connexion à la base de données
try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    print("Connexion réussie")

    # Supprimer chaque table dans la liste
    for table in tables_to_drop:
        try:
            cursor.execute(f"DROP TABLE {table};")
            conn.commit()  # Valider la transaction
            print(f"La table {table} a été supprimée avec succès.")
        except Exception as e:
            print(
                f"Une erreur s'est produite lors de la suppression de la table {table}."
            )
            print(f"Erreur : {e}")

finally:
    # Fermer la connexion à la base de données
    if "cursor" in locals():
        cursor.close()
    if "conn" in locals():
        conn.close()
