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
#                 response = requests.post("http://optimeal-model.switzerlandnorth.azurecontainer.io:8000/predict", json=data, headers=headers)
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

def predict_view(request):
    with tracer.start_as_current_span("predict_view_span"):
        result = None
        error = None

        if request.method == "POST":
            form = PredictionForm(request.POST)
            if form.is_valid():
                with tracer.start_as_current_span("form_processing"):
                    temperature = form.cleaned_data['temperature']
                    nb_presence_sur_site = form.cleaned_data['nb_presence_sur_site']
                    id_jour = form.cleaned_data['id_jour']

                    # Log the received form data
                    logger.info(f"Temperature: {temperature}")
                    logger.info(f"Nombre de présences sur site: {nb_presence_sur_site}")
                    logger.info(f"ID Jour: {id_jour}")

                    data = {
                        "temperature": temperature,
                        "nb_presence_sur_site": nb_presence_sur_site,
                        "id_jour": id_jour.isoformat()
                    }

                    headers = {
                        "Authorization": f"Bearer {os.getenv('ENCODED_JWT')}"
                    }

                with tracer.start_as_current_span("external_api_request"):
                    try:
                        response = requests.post("http://optimeal-model.switzerlandnorth.azurecontainer.io:8000/predict", json=data, headers=headers)
                        response.raise_for_status()
                        result = response.json()

                        # Log the prediction result
                        prediction_value = result.get('prediction', 0)
                        logger.info(f"Prediction result: {prediction_value}")

                        # Record prediction metrics
                        prediction_counter_per_minute.add(1)

                    except requests.exceptions.RequestException as e:
                        error = str(e)
                        logger.error(f"API request failed: {error}")
        else:
            form = PredictionForm()

        return render(request, "blog/predict.html", {"form": form, "result": result, "error": error})



