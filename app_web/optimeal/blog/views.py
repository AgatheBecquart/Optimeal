from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import requests
from .forms import PredictionForm
from django.conf import settings

from optimeal.opentelemetry_setup import prediction_counter_per_minute, logger, tracer

import os
from dotenv import load_dotenv
load_dotenv()

def home(request):
    return render(request, 'blog/home.html')

# def predict_view(request):
#     result = None
#     error = None

#     if request.method == "POST":
#         form = PredictionForm(request.POST)
#         if form.is_valid():
#             temperature = form.cleaned_data['temperature']
#             nb_presence_sur_site = form.cleaned_data['nb_presence_sur_site']
#             id_jour = form.cleaned_data['id_jour']

#             data = {
#                 "temperature": temperature,
#                 "nb_presence_sur_site": nb_presence_sur_site,
#                 "id_jour": id_jour.isoformat()
#             }

#             headers = {
#                 "Authorization": f"Bearer {ENCODED_JWT}"
#             }

#             try:
#                 response = requests.post("http://optimeal-model.francecentrale.azurecontainer.io:8000/predict", json=data, headers=headers)
#                 response.raise_for_status()
#                 result = response.json()
#             except requests.exceptions.RequestException as e:
#                 error = str(e)

#     else:
#         form = PredictionForm()

#     return render(request, "blog/predict.html", {"form": form, "result": result, "error": error})

from optimeal.opentelemetry_setup import prediction_counter_per_minute, logger, tracer

import os
from dotenv import load_dotenv
load_dotenv()

# Endpoint de l'API météo
URL = "https://public.opendatasoft.com/api/records/1.0/search/"
resource = "?dataset=donnees-synop-essentielles-omm&q="
station = f"&refine.nom=LILLE-LESQUIN"
start_date = '2023-09-01'
end_date = '2024-12-31'
row_limit = "&rows=10000"

import requests

def fetch_weather_data(target_date=None):
    if target_date:
        # Utilisation du format YYYY-MM-DD sans heure
        date_fork = f"date%3A%5B{target_date}+TO+{target_date}%5D"
    else:
        date_fork = f"date%3A%5B{start_date}+TO+{end_date}%5D"

    endpoint = URL + resource + date_fork + row_limit + station
    response = requests.get(endpoint)

    # Vérification du statut de la réponse
    if response.status_code != 200:
        print(f"Erreur HTTP: {response.status_code}")
        print(f"Contenu de la réponse: {response.text}")
        return []

    # Vérifier si 'records' est dans la réponse JSON
    response_json = response.json()
    if "records" not in response_json:
        print("La clé 'records' n'est pas présente dans la réponse.")
        print(f"Contenu de la réponse: {response_json}")
        return []

    daily_temperatures = []
    for record in response_json["records"]:
        date_time = record["fields"]["date"]
        if date_time.endswith("T12:00:00+00:00"):
            date = date_time[:10]  # Garde uniquement la partie date
            if "tc" not in record["fields"]:
                continue
            temperature = round(record["fields"]["tc"], 1)
            daily_temperatures.append({'date': date, 'temperature': temperature})

    return daily_temperatures


def predict_view(request):
    with tracer.start_as_current_span("predict_view_span"):
        result = None
        error = None
        temperature = None

        if request.method == "POST":
            form = PredictionForm(request.POST)
            if form.is_valid():
                with tracer.start_as_current_span("form_processing"):
                    nb_presence_sur_site = form.cleaned_data['nb_presence_sur_site']
                    id_jour = form.cleaned_data['id_jour'].strftime('%Y-%m-%d')  # Formatage de la date au format YYYY-MM-DD


                    # Convertir la date au format ISO avec heure (ajout de l'heure pour correspondre à ce que l'API attend)
                    formatted_date = id_jour

                    # Fetch temperature for the selected date only
                    daily_temperatures = fetch_weather_data(target_date=id_jour)

                    for record in daily_temperatures:
                        if record['date'] == id_jour :
                            temperature = record['temperature']
                            break

                    if temperature is None:
                        error = "Aucune température trouvée pour la date sélectionnée."
                        logger.error(error)

                    # Créer les données pour l'API en utilisant la date formatée
                    data = {
                        "temperature": temperature,
                        "nb_presence_sur_site": nb_presence_sur_site,
                        "id_jour": formatted_date  # Envoi de la date avec heure
                    }

                    headers = {
                        "Authorization": f"Bearer {os.getenv('ENCODED_JWT')}"
                    }

                with tracer.start_as_current_span("external_api_request"):
                    try:
                        response = requests.post("http://optimeal-model.francecentrale.azurecontainer.io:8000/predict", json=data, headers=headers)
                        response.raise_for_status()
                        result = response.json()

                       
                        prediction_value = result.get('prediction', 0)
                        rounded_prediction_value = round(prediction_value)
                        logger.info(f"Prediction result: {rounded_prediction_value}")
                        prediction_counter_per_minute.add(1)

                    except requests.exceptions.RequestException as e:
                        error = str(e)
                        logger.error(f"API request failed: {error}")
        else:
            form = PredictionForm()

        return render(request, "blog/predict.html", {"form": form, "result": result, "temperature": temperature, "error": error})



