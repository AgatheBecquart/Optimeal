from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import requests
from django.db import connection
from .forms import PredictionForm
from django.conf import settings
from optimeal.opentelemetry_setup import prediction_counter_per_minute, logger, tracer
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


def home(request):
    return render(request, "blog/home.html")


import os
from dotenv import load_dotenv

load_dotenv()


def predict_view(request):
    with tracer.start_as_current_span("predict_view_span"):
        context = {"form": PredictionForm(), "temperature": None, "error": None}

        if request.method == "POST":
            form = PredictionForm(request.POST)
            context["form"] = form
            if form.is_valid():
                with tracer.start_as_current_span("form_processing"):
                    id_jour = form.cleaned_data["id_jour"].strftime("%Y-%m-%d")
                    formatted_date = id_jour
                    data = {"id_jour": formatted_date}
                    headers = {"Authorization": f"Bearer {os.getenv('ENCODED_JWT')}"}

                with tracer.start_as_current_span("external_api_request"):
                    try:
                        response = requests.post(
                            "http://optimeal-model.switzerlandnorth.azurecontainer.io:8000/predict",
                            json=data,
                            headers=headers,
                        )
                        response.raise_for_status()
                        context["result"] = response.json()

                        prediction_value = context["result"].get("prediction", 0)
                        rounded_prediction_value = round(prediction_value)
                        logger.info(f"Prediction result: {rounded_prediction_value}")
                        prediction_counter_per_minute.add(1)

                    except requests.exceptions.RequestException as e:
                        context["error"] = str(e)
                        logger.error(f"API request failed: {context['error']}")
            else:
                context["error"] = "Formulaire invalide. Veuillez réessayer."

        return render(request, "blog/predict.html", context)


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Prediction  # Assurez-vous d'avoir un modèle Prediction


@login_required
def predictions_view(request):
    with tracer.start_as_current_span("mes_predictions_view_span"):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM predictions ORDER BY timestamp DESC")
            columns = [col[0] for col in cursor.description]
            raw_predictions = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # Formater les prédictions
        predictions = []
        for pred in raw_predictions:
            formatted_pred = pred.copy()

            # Formater id_jour en date sans les secondes
            if isinstance(pred["id_jour"], datetime):
                formatted_pred["id_jour"] = pred["id_jour"].strftime("%Y-%m-%d")
            elif isinstance(pred["id_jour"], str):
                try:
                    date_obj = datetime.strptime(pred["id_jour"], "%Y-%m-%d %H:%M:%S")
                    formatted_pred["id_jour"] = date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    # Si le format est déjà YYYY-MM-DD, on le laisse tel quel
                    pass

            # S'assurer que nb_presence_sur_site est un entier
            formatted_pred["nb_presence_sur_site"] = int(
                float(pred["nb_presence_sur_site"])
            )

            # Ramener les prédictions négatives à 0
            formatted_pred["prediction"] = max(0, int(float(pred["prediction"])))

            predictions.append(formatted_pred)

        context = {"predictions": predictions}

        return render(request, "blog/predictions.html", context)
