import pandas as pd
import os
from unittest.mock import patch

# Supposons que la fonction feature_engineering est définie ici ou importée
# from your_module import feature_engineering
# Exemple de données d'entrée factices
data = {
    "id_jour": [
        "2023-09-01",
        "2023-09-02",
        "2023-09-03",
        "2023-09-04",
    ],  # Quatre jours successifs
}
df_test = pd.DataFrame(data)
df_test["id_jour"] = pd.to_datetime(df_test["id_jour"])
# Données de vacances factices
vacances_data = pd.DataFrame(
    {
        "description": ["Vacances_Summer", "Vacances_Summer"],
        "start_date": ["2023-07-01", "2023-07-01"],
        "end_date": ["2023-09-01", "2023-09-02"],
    }
)


# Fonction mock pour get_vacation_data
def mock_get_vacation_data():
    return vacances_data


# Données météo factices
weather_data_mock = {
    "data": [
        {
            "temp": 20,
            "feels_like": 19,
            "pressure": 1012,
            "humidity": 60,
            "dew_point": 12,
            "clouds": 20,
            "visibility": 10000,
            "wind_speed": 5,
            "wind_deg": 180,
            "weather": [{"main": "Clear", "description": "clear sky"}],
        }
    ],
    "rain": {"1h": 0.0},
}


# Fonction mock pour get_weather_data
def mock_get_weather_data(api_key, date):
    return weather_data_mock
