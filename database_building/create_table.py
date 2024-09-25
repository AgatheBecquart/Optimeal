import pyodbc
from dotenv import load_dotenv
import os
import csv
from datetime import datetime, timedelta, timezone
import requests
import time
import pytz

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Utiliser les variables d'environnement pour les paramètres de connexion
server = os.getenv("SERVER")
database = os.getenv("DATABASE")
user = os.getenv("AZUREUSER")
password = os.getenv("PASSWORD")

# Chaîne de connexion à la base de données
conn_str = f"DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};UID={user};PWD={password}"

# Coordonnées de Marcq-en-Baroeul
lat = 50.6788
lon = 3.0915


# Définir la fonction pour anonymiser les identifiants des agents
def anonymize_id(id):
    # Utiliser la fonction de hashage pour transformer l'ID en une valeur hash
    hashed_id = hash(str(id))
    # Assurer que l'ID est toujours positif
    anonymized_id = abs(hashed_id)
    # Limiter la longueur à 7 chiffres
    anonymized_id = anonymized_id % (10**7)
    return anonymized_id


# Convertir une date à 12h en timestamp Unix
def get_unix_timestamp_for_noon(date_str):
    # Fuseau horaire de Paris
    paris_tz = pytz.timezone("Europe/Paris")

    # Créer un objet datetime à 12h de la date donnée
    date = datetime.strptime(date_str, "%Y-%m-%d")
    date_noon = date.replace(hour=12, minute=0, second=0)

    # Convertir en heure locale (Paris) et en timestamp Unix
    localized_time = paris_tz.localize(date_noon)
    return int(localized_time.timestamp())


# Fonction pour récupérer les données météorologiques pour une période donnée
def get_weather_data_for_period(api_key, start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    current_date = start_date
    weather_data = []

    while current_date <= end_date:
        # Obtenir le timestamp Unix pour 12h à Marcq-en-Baroeul
        timestamp = get_unix_timestamp_for_noon(current_date.strftime("%Y-%m-%d"))

        # Construire l'URL pour la requête API
        history_url = f"https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={lat}&lon={lon}&dt={timestamp}&appid={api_key}&lang=fr&units=metric"
        print(
            f"Fetching data for {current_date.strftime('%Y-%m-%d')} at 12h: {history_url}"
        )

        # Envoyer la requête à l'API et stocker les résultats
        response = requests.get(history_url)
        if response.status_code == 200:
            weather_data.append(response.json())
        else:
            print(
                f"Erreur lors de la récupération des données météo pour {current_date.strftime('%Y-%m-%d')}"
            )

        # Passer au jour suivant
        current_date += timedelta(days=1)

    return weather_data


# Fonction pour insérer les données météo dans la base de données
def insert_weather_data(cursor, weather_data):
    # Fuseau horaire de Paris
    paris_tz = pytz.timezone("Europe/Paris")

    for record in weather_data:
        try:
            # Accéder à la liste des données météo sous la clé 'data'
            for weather in record["data"]:
                # Convertir le timestamp Unix en datetime aware (timezone-aware UTC)
                timestamp = weather["dt"]
                utc_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)

                # Convertir en heure de Paris
                paris_time = utc_time.astimezone(paris_tz)
                date = paris_time.strftime("%Y-%m-%d")

                # Extraire les autres données
                temp = weather["temp"]
                feels_like = weather["feels_like"]
                pressure = weather["pressure"]
                humidity = weather["humidity"]
                dew_point = weather["dew_point"]
                clouds = weather["clouds"]
                visibility = weather.get(
                    "visibility", 10000
                )  # Par défaut 10000 si non disponible
                wind_speed = weather["wind_speed"]
                wind_deg = weather["wind_deg"]
                weather_main = weather["weather"][0]["main"]
                weather_description = weather["weather"][0]["description"]
                rain = weather.get("rain", {}).get(
                    "1h", 0.0
                )  # Par défaut 0.0 si pas de pluie

                # Insérer dans la base de données
                cursor.execute(
                    """
                    INSERT INTO Meteo (id_jour, temp, feels_like, pressure, humidity, dew_point, clouds, visibility, wind_speed, wind_deg, weather_main, weather_description, rain)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        date,
                        temp,
                        feels_like,
                        pressure,
                        humidity,
                        dew_point,
                        clouds,
                        visibility,
                        wind_speed,
                        wind_deg,
                        weather_main,
                        weather_description,
                        rain,
                    ),
                )

        except Exception as e:
            print(
                f"Erreur lors de l'insertion des données météo pour {date if 'date' in locals() else 'inconnue'} : {e}"
            )


# Fonction pour insérer les données depuis les fichiers CSV
def insert_csv_data(cursor, csv_files, id_mapping):
    for table, file_path in csv_files.items():
        try:
            with open(file_path, newline="", encoding="utf-8") as csvfile:

                csv_reader = csv.reader(csvfile, delimiter=",")
                next(csv_reader)  # Passer l'en-tête

                for row in csv_reader:
                    print(row)
                    try:
                        if table == "RepasVendus":
                            date_str = datetime.strptime(row[0], "%d/%m/%Y").strftime(
                                "%Y-%m-%d"
                            )
                            cursor.execute(
                                f"INSERT INTO {table} (id_jour, nb_couvert) VALUES (?, ?)",
                                (date_str, row[1]),
                            )
                        elif table == "PresenceRH":
                            # Anonymiser l'identifiant de l'agent
                            old_id_agent = row[0]
                            anonymized_id_agent = id_mapping.get(old_id_agent)
                            if anonymized_id_agent is None:
                                anonymized_id_agent = anonymize_id(old_id_agent)
                                id_mapping[old_id_agent] = anonymized_id_agent
                            # Utiliser le nouvel identifiant anonymisé
                            row[0] = anonymized_id_agent
                            # Convertir les dates et heures
                            row[6] = datetime.strptime(row[6], "%d/%m/%Y").strftime(
                                "%Y-%m-%d"
                            )
                            row[7] = datetime.strptime(row[7], "%d/%m/%Y").strftime(
                                "%Y-%m-%d"
                            )
                            cursor.execute(
                                f"INSERT INTO {table} VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                row,
                            )
                    except Exception as e:
                        print(
                            f"Une erreur s'est produite lors de l'insertion de données dans la table {table}"
                        )
                        print(f"Erreur : {e}")
        except Exception as e:
            print(f"Erreur lors de l'ouverture du fichier {file_path} : {e}")


# Connexion à la base de données et création des tables
try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    print("Connexion réussie")

    # Création des tables
    sql_commands = [
        """
        CREATE TABLE Meteo (
            id_jour DATE PRIMARY KEY,
            temp FLOAT,
            feels_like FLOAT,
            pressure INT,
            humidity INT,
            dew_point FLOAT,
            clouds INT,
            visibility INT,
            wind_speed FLOAT,
            wind_deg INT,
            weather_main VARCHAR(50),
            weather_description VARCHAR(100),
            rain FLOAT
        );
        """,
        """
        CREATE TABLE RepasVendus (
            id_jour DATE PRIMARY KEY,
            nb_couvert INTEGER
        );
        """,
        """
        CREATE TABLE PresenceRH (
            id_agent_anonymise INT,
            heure DATETIME,
            id_motif INT,
            lib_motif TEXT,
            type_presence TEXT,
            origine TEXT,
            date_traitement DATE,
            date_j DATE
        );
        """,
    ]

    for sql_command in sql_commands:
        cursor.execute(sql_command)
        conn.commit()

    # Récupérer les données météorologiques
    api_key = os.getenv(
        "API_KEY"
    )  # Assurez-vous que l'API_KEY est définie dans le fichier .env
    weather_data = get_weather_data_for_period(api_key, "2023-09-01", "2024-09-28")

    # Insérer les données météorologiques dans la base de données
    insert_weather_data(cursor, weather_data)

    # Insérer des données depuis les fichiers CSV dans les tables
    csv_files = {
        "RepasVendus": "data/df_passage_cantine.csv",
        "PresenceRH": "data/df_presence_rh.csv",
    }
    id_mapping = {}
    insert_csv_data(cursor, csv_files, id_mapping)

    # Valider les transactions
    conn.commit()

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
