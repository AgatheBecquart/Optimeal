import pyodbc
from dotenv import load_dotenv
import os
import csv
from datetime import datetime
import requests

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Utiliser les variables d'environnement pour les paramètres de connexion
server = os.getenv("SERVER")
database = os.getenv("DATABASE")
user = os.getenv("AZUREUSER")
password = os.getenv("PASSWORD")

# Chaîne de connexion à la base de données
conn_str = f'DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};UID={user};PWD={password}'

# Définir la fonction pour anonymiser les identifiants des agents
def anonymize_id(id):
    # Utiliser la fonction de hashage pour transformer l'ID en une valeur hash
    hashed_id = hash(str(id))
    # Assurer que l'ID est toujours positif
    anonymized_id = abs(hashed_id)
    # Limiter la longueur à 7 chiffres
    anonymized_id = anonymized_id % (10**7)
    return anonymized_id

# Endpoint de l'API météo
URL = "https://public.opendatasoft.com/api/records/1.0/search/"
resource = "?dataset=donnees-synop-essentielles-omm&q="
station = f"&refine.nom=ORLY"
start_date = '2023-09-01'
end_date = '2024-02-28'
row_limit = "&rows=10000"

# Fonction pour récupérer les données météorologiques depuis l'API
def fetch_weather_data():
    # Créer l'URL de l'API à partir des dates de début et de fin
    date_fork = f"date%3A%5B{start_date}+TO+{end_date}%5D"
    endpoint = URL + resource + date_fork + row_limit + station
    response = requests.get(endpoint)
    
    daily_temperatures = []
    for record in response.json()["records"]:
        date_time = record["fields"]["date"]  # Extraire la date et l'heure complètes
        if date_time.endswith("T12:00:00+00:00"):  # Vérifier si l'heure est 12:00:00
            date = date_time[:10]  # Extraire uniquement la date au format YYYY-MM-DD
            if "tc" not in record["fields"]:
                continue  # Passer à l'itération suivante si la clé "tc" n'est pas présente
            temperature = record["fields"]["tc"]
            temperature = round(temperature, 1) 
            daily_temperatures.append({'date': date, 'temperature': temperature})
    
    return daily_temperatures

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    print("Connexion réussie")
    
    # Liste des commandes SQL
    sql_commands = [
        "CREATE TABLE Meteo (id_jour DATE PRIMARY KEY, temperature FLOAT);",
        "CREATE TABLE RepasVendus (id_jour DATE PRIMARY KEY, nb_couvert INTEGER);",
        "CREATE TABLE PresenceRH (id_agent_anonymise INT, date_demi_j DATETIME, id_motif INT, lib_motif TEXT, type_presence TEXT, origine TEXT, date_traitement DATE);"
    ]
    
    # Exécuter chaque commande SQL pour créer les tables
    for sql_command in sql_commands:
        try:
            cursor.execute(sql_command)
            conn.commit()  # Valider la transaction
        except Exception as e:
            print(f"Une erreur s'est produite lors de l'exécution de la commande SQL : {sql_command}")
            print(f"Erreur : {e}")

        # Récupérer les données météorologiques depuis l'API
    daily_temperatures = fetch_weather_data()
    
    # Insérer les données dans la table Meteo
    for row in daily_temperatures:
        print(row)
        cursor.execute("INSERT INTO Meteo (id_jour, temperature) VALUES (?, ?)", (row['date'], row['temperature']))
    
    # Insérer des données depuis les fichiers CSV dans les tables
    csv_files = {
        'RepasVendus': 'data/Passage_Journalier_Passage_API.csv',
        'PresenceRH': 'data/df_olga.csv'
    }
    
    # Créer un dictionnaire pour mapper les anciens identifiants aux nouveaux identifiants anonymisés
    id_mapping = {}
    
    for table, file_path in csv_files.items():
        with open(file_path, newline='') as csvfile:
            if table == 'RepasVendus' or table == 'PresenceRH':
                csv_reader = csv.reader(csvfile, delimiter=';')  # Spécifier le point-virgule comme délimiteur
            else:
                csv_reader = csv.reader(csvfile)  # Utiliser le délimiteur par défaut
            next(csv_reader)  # Ignorer l'en-tête si nécessaire
            for row in csv_reader:
                print(row)
                try:
                    # Exclure la colonne d'identité lors de l'insertion
                    if table == 'RepasVendus':
                        date_str = datetime.strptime(row[0], '%d/%m/%Y').strftime('%Y-%m-%d')
                        cursor.execute(f"INSERT INTO {table} VALUES (?, ?)", (date_str, row[1]))
                    elif table == 'PresenceRH':
                        # Anonymiser l'identifiant de l'agent
                        old_id_agent = row[0]
                        anonymized_id_agent = id_mapping.get(old_id_agent)
                        if anonymized_id_agent is None:
                            anonymized_id_agent = anonymize_id(old_id_agent)
                            id_mapping[old_id_agent] = anonymized_id_agent
                        # Utiliser le nouvel identifiant anonymisé
                        row[0] = anonymized_id_agent
                        # Convertir la chaîne de date et heure en un objet datetime
                        date_time_str = row[1]
                        date_time_obj = datetime.strptime(date_time_str, '%d/%m/%Y %H:%M:%S,%f')
                        # Convertir la date de la sixième colonne au format attendu par la base de données
                        date_str_2 = datetime.strptime(row[6], '%d/%m/%Y').strftime('%Y-%m-%d')
                        # Remplacer les valeurs dans la liste row avec les valeurs converties
                        row[1] = date_time_obj
                        row[6] = date_str_2
                        cursor.execute(f"INSERT INTO {table} VALUES (?, ?, ?, ?, ?, ?, ?)", row)
                except Exception as e:
                    print(f"Une erreur s'est produite lors de l'insertion de données dans la table {table}")
                    print(f"Erreur : {e}")
    
    # Valider la transaction
    conn.commit()
    
finally:
    # Fermer la connexion à la base de données
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
