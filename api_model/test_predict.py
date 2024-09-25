import pytest
from api_model.predict import prepare_input_data, predict
from api_model.feature_engineering import get_weather_data, get_vacation_data, feature_engineering
import pandas as pd
from unittest.mock import patch
import warnings
from pydantic import PydanticDeprecatedSince20

warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)

@pytest.fixture
def mock_weather_data():
    return {
        'data': [{
            'temp': 20, 'feels_like': 19, 'pressure': 1012, 'humidity': 60,
            'dew_point': 12, 'clouds': 20, 'visibility': 10000, 'wind_speed': 5,
            'wind_deg': 180, 'weather': [{'main': 'Clear', 'description': 'clear sky'}]
        }],
        'rain': {'1h': 0.0}
    }

@pytest.fixture
def mock_vacation_data():
    return pd.DataFrame({
        'description': ['Vacances_Vacances d\'Été'],
        'start_date': ['2023-07-01'],
        'end_date': ['2023-09-01']
    })

  
def test_prepare_input_data(mock_weather_data, mock_vacation_data):
    with patch('api_model.feature_engineering.get_weather_data', return_value=mock_weather_data):
        with patch('api_model.feature_engineering.get_vacation_data', return_value=mock_vacation_data):
            # Préparer les données d'entrée
            input_data = prepare_input_data({"id_jour": "2023-08-01"})
            
            # Vérifier que input_data est un DataFrame avec la colonne 'id_jour'
            assert isinstance(input_data, pd.DataFrame)
            assert 'id_jour' in input_data.columns
            
            # Appliquer le feature engineering
            processed_data = feature_engineering(input_data)
            
            # Liste des colonnes attendues
            expected_columns = ["id_jour", "temp", "feels_like", "pressure", "humidity", "dew_point", "clouds",
                "visibility", "wind_speed", "wind_deg", "rain", "nb_presence_sur_site",
                "Vacances_Vacances d'Été", "Vacances_Vacances de Printemps",
                "Vacances_Vacances d'Hiver", "Vacances_Pont de l'Ascension",
                "Vacances_Vacances de la Toussaint", "Vacances_Vacances de Noël",
                "Vacances_Début des Vacances d'Été", "Jour_Semaine_Monday",
                "Jour_Semaine_Saturday", "Jour_Semaine_Sunday", "Jour_Semaine_Thursday",
                "Jour_Semaine_Tuesday", "Jour_Semaine_Wednesday", "weather_main_Clear", "weather_main_Clouds", 
                "weather_main_Mist", "weather_main_Rain", "weather_main_Snow", "weather_description_brume", 
                "weather_description_ciel dégagé", "weather_description_couvert", "weather_description_forte pluie", 
                "weather_description_légère pluie", "weather_description_légères chutes de neige", 
                "weather_description_nuageux", "weather_description_peu nuageux", "weather_description_pluie modérée", 
                "weather_description_bruine légère", "weather_main_Drizzle", "weather_description_pluie très fine", 
                "weather_description_chutes de neige", "weather_description_partiellement nuageux"]
            
            # Ajouter les colonnes manquantes et réorganiser
            missing_columns = set(expected_columns) - set(processed_data.columns)
            for col in missing_columns:
                processed_data[col] = 0
            processed_data = processed_data[expected_columns]
            
            # Vérifier que toutes les colonnes attendues sont présentes et dans le bon ordre
            assert list(processed_data.columns) == expected_columns, "Les colonnes ne sont pas dans l'ordre attendu ou certaines sont manquantes"
            
            # Vérifier que les colonnes ajoutées ont des valeurs par défaut de 0
            for col in missing_columns:
                assert (processed_data[col] == 0).all(), f"La colonne {col} n'a pas été initialisée à 0"
            
            # Vérifications supplémentaires
            assert not processed_data['temp'].isnull().all(), "Les données de température sont toutes nulles"
            assert 'nb_presence_sur_site' in processed_data.columns, "La colonne nb_presence_sur_site est manquante"
            
            # Vérifier que les colonnes de vacances et de jours de la semaine sont présentes
            assert any(col.startswith("Vacances_") for col in processed_data.columns), "Aucune colonne de vacances trouvée"
            assert any(col.startswith("Jour_Semaine_") for col in processed_data.columns), "Aucune colonne de jour de la semaine trouvée"


def test_feature_engineering():
    input_data = pd.DataFrame({
        'id_jour': ['2023-08-01'],
        'temp': [20],
        'nb_presence_sur_site': [100]
    })
    result = feature_engineering(input_data)
    assert 'Jour_Semaine_Tuesday' in result.columns
    assert 'Vacances_Vacances d\'Été' in result.columns