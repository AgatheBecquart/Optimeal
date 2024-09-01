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
    model_name = "third_run_2023"
    model = get_model(model_name)

    # Préparez les données d'entrée en DataFrame
    input_data = prepare_input_data(canteen)

    # Stockez 'id_jour' séparément
    id_jour = input_data['id_jour'].iloc[0]

    expected_columns = ["id_jour", "temperature", "nb_presence_sur_site", "Vacances_Vacances de la Toussaint", "Vacances_Vacances d'Été", "Vacances_Vacances de Noël", "Vacances_Vacances de Printemps", "Vacances_Vacances d'Hiver",
    "Vacances_Pont de l'Ascension", "Vacances_Début des Vacances d'Été", "Jour_Semaine_Monday", "Jour_Semaine_Saturday", "Jour_Semaine_Sunday", "Jour_Semaine_Thursday", "Jour_Semaine_Tuesday", "Jour_Semaine_Wednesday"]
    
    input_data = feature_engineering(input_data, expected_columns=expected_columns)

    # Supprimez la colonne 'id_jour' si elle existe
    if 'id_jour' in input_data.columns:
        input_data.drop('id_jour', axis=1, inplace=True)

    # Faites la prédiction
    prediction = predict_single(model, input_data)

    # MLops: Enregistrez la prédiction dans la base de données
    prediction_dict = {
        "prediction": int(prediction),
        "temperature": canteen.temperature,
        "nb_presence_sur_site": canteen.nb_presence_sur_site,
        "id_jour": id_jour,  # Utilisez 'id_jour' stocké
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model": model_name
    }
    create_db_prediction(prediction_dict, db)

    return SinglePredictionOutput(prediction=prediction)
