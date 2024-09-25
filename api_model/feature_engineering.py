import pandas as pd
import requests
from datetime import datetime, timedelta, timezone
from api_model.database import connect_to_database
import pytz
import os
from dotenv import load_dotenv

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Coordonnées de Marcq-en-Baroeul
lat = 50.6788
lon = 3.0915


def get_vacation_data(location="Lille"):
    # Exemple d'appel à l'API des vacances scolaires
    url = "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records?where=location%20like%20%22lille%22&limit=100"
    response = requests.get(url)
    data = response.json()
    vacances = []
    for record in data["results"]:
        fields = record
        if fields["location"] == location:
            vacances.append(
                {
                    "start_date": fields["start_date"],  # Remove timezone
                    "end_date": fields["end_date"],  # Remove timezone
                    "description": fields["description"],
                    "location": fields["location"],
                    "description": fields["description"],
                    "annee_scolaire": fields["annee_scolaire"],
                    "zone": fields["zones"],
                }
            )

    return pd.DataFrame(vacances)


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


# Fonction pour récupérer les données météorologiques pour une date spécifique
def get_weather_data(api_key, date_str):
    # Obtenir le timestamp Unix pour 12h de la date spécifiée
    timestamp = get_unix_timestamp_for_noon(date_str)

    # Construire l'URL pour la requête API
    weather_url = f"https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={lat}&lon={lon}&dt={timestamp}&appid={api_key}&lang=fr&units=metric"
    print(f"Fetching data for {date_str} at 12h: {weather_url}")
    print(timestamp)
    # Envoyer la requête à l'API
    response = requests.get(weather_url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur lors de la récupération des données météo pour {date_str}")
        print(response.status_code)
        return None


# Fonction de feature engineering
def feature_engineering(df):
    df["id_jour"] = pd.to_datetime(
        df["id_jour"]
    )  # S'assurer que 'id_jour' est de type datetime

    # Obtenir les données de vacances scolaires depuis l'API
    vacances_df = get_vacation_data()

    # Créer une colonne pour chaque type de vacances et initialiser à 0
    vacances_types = vacances_df["description"].unique()
    for vac in vacances_types:
        df[f"Vacances_{vac}"] = 0

    # Convertir les colonnes de date des vacances en datetime si nécessaire
    vacances_df["start_date"] = pd.to_datetime(vacances_df["start_date"]).dt.strftime(
        "%Y-%m-%d"
    )
    vacances_df["end_date"] = pd.to_datetime(vacances_df["end_date"]).dt.strftime(
        "%Y-%m-%d"
    )

    # Marquer les jours de chaque période de vacances avec la valeur 1
    for _, row in vacances_df.iterrows():
        vac_column = f'Vacances_{row["description"]}'
        df.loc[
            (df["id_jour"] >= row["start_date"]) & (df["id_jour"] <= row["end_date"]),
            vac_column,
        ] = 1

    # Créer une colonne 'Jour_Semaine' qui contient le nom du jour
    df["Jour_Semaine"] = df["id_jour"].dt.day_name()

    # Liste complète des jours de la semaine
    jours_semaine_complet = [
        "Jour_Semaine_Monday",
        "Jour_Semaine_Saturday",
        "Jour_Semaine_Sunday",
        "Jour_Semaine_Thursday",
        "Jour_Semaine_Tuesday",
        "Jour_Semaine_Wednesday",
    ]

    # Encodage one-hot avec tous les jours de la semaine
    df_temp = pd.get_dummies(
        df["Jour_Semaine"], columns=["Jour_Semaine"], drop_first=False
    )
    for jour in jours_semaine_complet:
        jour_seul = jour[13:]
        if jour_seul not in df_temp.columns:
            df[jour] = 0
        else:
            df[jour] = 1

    df = df.drop(["Jour_Semaine"], axis=1)

    # Ajout des données météo pour chaque jour
    for index, row in df.iterrows():
        api_key = os.getenv(
            "API_KEY"
        )  # Assurez-vous que l'API_KEY est définie dans le fichier .env
        weather_data = get_weather_data(api_key, row["id_jour"].strftime("%Y-%m-%d"))
        print(weather_data)
        if weather_data:
            current_weather = weather_data["data"][
                0
            ]  # Supposons que la réponse contient les données dans 'data'
            df.loc[index, "temp"] = current_weather.get("temp", None)
            df.loc[index, "feels_like"] = current_weather.get("feels_like", None)
            df.loc[index, "pressure"] = current_weather.get("pressure", None)
            df.loc[index, "humidity"] = current_weather.get("humidity", None)
            df.loc[index, "dew_point"] = current_weather.get("dew_point", None)
            df.loc[index, "clouds"] = current_weather.get("clouds", None)
            df.loc[index, "visibility"] = current_weather.get("visibility", None)
            df.loc[index, "wind_speed"] = current_weather.get("wind_speed", None)
            df.loc[index, "wind_deg"] = current_weather.get("wind_deg", None)
            df.loc[index, "weather_main"] = current_weather["weather"][0]["main"]
            df.loc[index, "weather_description"] = current_weather["weather"][0][
                "description"
            ]
            df.loc[index, "rain"] = weather_data.get("rain", {}).get("1h", 0.0)
        else:
            print(f"Aucune donnée météo pour la date {row['id_jour']}")

    connection = connect_to_database()

    presence_query = """
    SELECT 	
        date_j,
        count(id_agent_anonymise)/2 as nb_presence_sur_site
    FROM
        [dbo].[PresenceRH]
    GROUP BY 
        date_j
    ORDER BY 
        date_j DESC
    """

    df_presence = pd.read_sql_query(presence_query, connection)

    # Assurer que 'date_j' est aussi de type datetime
    df_presence["date_j"] = pd.to_datetime(df_presence["date_j"])

    # Vérifier les types de données avant la fusion (pour diagnostic)
    print(f"Type de 'id_jour' dans df: {df['id_jour'].dtype}")
    print(f"Type de 'date_j' dans df_presence: {df_presence['date_j'].dtype}")

    # Fusionner df et df_presence sur 'id_jour' et 'date_j'
    df = pd.merge(df, df_presence, left_on="id_jour", right_on="date_j", how="left")

    # Supprimer la colonne 'date_j' après la fusion si elle n'est plus nécessaire
    df = df.drop(columns=["date_j"])

    return df
