from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import requests
from .forms import PredictionForm
from django.conf import settings

ENCODED_JWT = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiJ9.DtUK8DITE8x58OxMgG0x6BEysUl9F1QxOkHE8XxgjH0'

def home(request):
    return render(request, 'blog/home.html')

def predict_view(request):
    result = None
    error = None

    if request.method == "POST":
        form = PredictionForm(request.POST)
        if form.is_valid():
            temperature = form.cleaned_data['temperature']
            nb_presence_sur_site = form.cleaned_data['nb_presence_sur_site']
            id_jour = form.cleaned_data['id_jour']

            data = {
                "temperature": temperature,
                "nb_presence_sur_site": nb_presence_sur_site,
                "id_jour": id_jour.isoformat()
            }

            headers = {
                "Authorization": f"Bearer {ENCODED_JWT}"
            }

            try:
                response = requests.post("http://optimeal-model.switzerlandnorth.azurecontainer.io:8000/predict", json=data, headers=headers)
                response.raise_for_status()
                result = response.json()
            except requests.exceptions.RequestException as e:
                error = str(e)

    else:
        form = PredictionForm()

    return render(request, "blog/predict.html", {"form": form, "result": result, "error": error})