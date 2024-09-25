# from meteofrance_api import MeteoFranceClient
# from datetime import datetime

# # Crée une instance du client Météo-France
# client = MeteoFranceClient()

# # Coordonées GPS de Marcq-en-Baroeul
# latitude = 50.6769
# longitude = 3.0786

# # Récupère les prévisions météo pour Marcq-en-Baroeul
# forecast = client.get_forecast(latitude, longitude, language='fr')

# # Fonction pour convertir le timestamp en format lisible
# def convert_timestamp_to_date(timestamp):
#     return datetime.fromtimestamp(timestamp).strftime('%d %b %Y')

# # Affiche les prévisions à 12h pour chaque jour disponible
# print("Prévisions journalières à 12h :")
# dates_done = set()  # Pour éviter de répéter les jours

# for hour in forecast.forecast:
#     # Convertir l'heure en objet datetime
#     hour_timestamp = datetime.fromtimestamp(hour['dt'])

#     # Vérifier si l'heure est 12h et si on n'a pas déjà traité ce jour
#     if hour_timestamp.hour == 12:
#         date_str = convert_timestamp_to_date(hour['dt'])
#         if date_str not in dates_done:  # Éviter les doublons de jours
#             dates_done.add(date_str)

#             # Récupérer la température et les conditions
#             temp = hour['T']['value']
#             condition = hour.get('weather', {}).get('desc', 'Aucune information sur la météo')

#             # Afficher les informations
#             print(f"Jour: {date_str}, Température à 12h: {temp}°C, Condition: {condition}")

from meteofrance_api import MeteoFranceClient
from datetime import datetime

# Crée une instance du client Météo-France
client = MeteoFranceClient()

# Coordonées GPS de Marcq-en-Baroeul
latitude = 50.6769
longitude = 3.0786

# Récupère les observations météo pour Marcq-en-Baroeul
observation = client.get_observation(latitude, longitude, language="fr")


# Fonction pour convertir le timestamp en format lisible
def convert_timestamp_to_date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%d %b %Y à %H:%M")


# Affiche les observations disponibles
print("Observations météo disponibles :")

# Vérifier et afficher les données d'observation si disponibles
if observation:
    obs_time = convert_timestamp_to_date(observation.time_as_datetime.timestamp())
    temperature = observation.temperature
    weather_description = observation.weather_description

    print(
        f"Date et heure: {obs_time}, Température: {temperature}°C, Condition: {weather_description}"
    )
else:
    print("Aucune observation disponible.")
