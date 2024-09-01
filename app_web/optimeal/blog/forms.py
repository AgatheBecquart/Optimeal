# forms.py
from django import forms
from datetime import datetime

class PredictionForm(forms.Form):
    temperature = forms.FloatField(label='Temperature')
    nb_presence_sur_site = forms.FloatField(label='Nombre de présence sur site')
    id_jour = forms.DateTimeField(label='Date (id_jour)', initial=datetime.now, widget=forms.widgets.DateInput(attrs={'type': 'date'}))
