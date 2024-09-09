# forms.py
from django import forms
from datetime import datetime

class PredictionForm(forms.Form):
    id_jour = forms.DateTimeField(label='Date à prédire :', widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    temperature = forms.FloatField(label='Temperature :')
    nb_presence_sur_site = forms.FloatField(label='Nombre de présence sur site :')

