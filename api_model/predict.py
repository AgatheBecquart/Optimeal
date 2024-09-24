# main.py script
from fastapi import Depends
from fastapi import APIRouter
from fastapi.params import Depends
from api_model.utils import has_access, SinglePredictionInput, SinglePredictionOutput, predict_single, get_model
from api_model.database import get_db, create_db_prediction
from sqlalchemy.orm import Session
import time
import pandas as pd
from api_model.feature_engineering import feature_engineering
from fastapi import HTTPException


router = APIRouter()


def prepare_input_data(input_data):
    df = pd.DataFrame([input_data.__dict__])
    return df


@router.post("", response_model=SinglePredictionOutput)
def predict(
    canteen: SinglePredictionInput,
    authenticated: bool = Depends(has_access),
    db: Session = Depends(get_db)
) -> SinglePredictionOutput:
    model_name = "run_final"
    model = get_model(model_name)

    # Préparez les données d'entrée en DataFrame
    input_data = prepare_input_data(canteen)

    # Stockez 'id_jour' séparément
    id_jour = input_data['id_jour'].iloc[0]

    expected_columns = ["id_jour", "temp", "feels_like", "pressure", "humidity", "dew_point", "clouds",
       "visibility", "wind_speed", "wind_deg", "rain", "nb_presence_sur_site",
       "Vacances_Vacances d'Été", "Vacances_Vacances de Printemps",
       "Vacances_Vacances d'Hiver", "Vacances_Pont de l'Ascension",
       "Vacances_Vacances de la Toussaint", "Vacances_Vacances de Noël",
       "Vacances_Début des Vacances d'Été", "Jour_Semaine_Monday",
       "Jour_Semaine_Saturday", "Jour_Semaine_Sunday", "Jour_Semaine_Thursday",
       "Jour_Semaine_Tuesday", "Jour_Semaine_Wednesday", "weather_main_Clear", "weather_main_Clouds", 
       "weather_main_Mist", "weather_main_Rain", "weather_main_Snow", "weather_description_brume", "weather_description_ciel dégagé", 
       "weather_description_couvert", "weather_description_forte pluie", "weather_description_légère pluie", "weather_description_légères chutes de neige", 
       "weather_description_nuageux", "weather_description_peu nuageux", "weather_description_pluie modérée", "weather_description_bruine légère", 
       "weather_main_Drizzle", "weather_description_pluie très fine", "weather_description_chutes de neige", "weather_description_partiellement nuageux"]

    input_data = feature_engineering(input_data)

    # Remplacer les valeurs manquantes par des zéros
    input_data.fillna(0, inplace=True)

    # Réordonner les colonnes selon l'ordre attendu
    if expected_columns:
        missing_columns = set(expected_columns) - set(input_data.columns)
        for col in missing_columns:
            input_data[col] = 0  # Ajouter les colonnes manquantes avec des valeurs par défaut (par exemple, 0)
        input_data = input_data[expected_columns]
    
    # Supprimez la colonne 'id_jour' si elle existe
    if 'id_jour' in input_data.columns:
        input_data.drop('id_jour', axis=1, inplace=True)

    # Faites la prédiction
    prediction = predict_single(model, input_data)

    # MLops: Enregistrez la prédiction dans la base de données
    prediction_dict = {
        "prediction": int(prediction),
        "temperature": float(input_data.temp.iloc[0]),
        "nb_presence_sur_site": float(input_data.nb_presence_sur_site.iloc[0]),
        "id_jour": str(id_jour),  # Utilisez 'id_jour' stocké
        "timestamp": str(time.strftime("%Y-%m-%d %H:%M:%S")),
        "model": model_name,
    }
    create_db_prediction(prediction_dict, db)

    return SinglePredictionOutput(prediction=prediction)

