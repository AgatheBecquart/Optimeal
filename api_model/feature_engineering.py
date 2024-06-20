import pandas as pd
import requests

def get_vacation_data(location='Lille'):
    # Exemple d'appel à l'API des vacances scolaires
    url = "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records?where=location%20like%20%22lille%22&limit=100"
    response = requests.get(url)
    data = response.json()
    vacances = []
    for record in data['results']:
        fields = record
        if fields['location'] == location:
            vacances.append({
                'start_date': fields['start_date'],  # Remove timezone
                'end_date': fields['end_date'],      # Remove timezone
                'description': fields['description'],
                'location': fields['location'],
                'description': fields['description'],
                'annee_scolaire': fields['annee_scolaire'],
                'zone': fields['zones']
            })

    return pd.DataFrame(vacances)


def feature_engineering(df):

    df['id_jour'] = pd.to_datetime(df['id_jour'])  # Assurez-vous que 'id_jour' est de type datetime

    # Obtenir les données de vacances scolaires depuis l'API
    vacances_df = get_vacation_data()

    # Créer une colonne pour chaque type de vacances et initialiser à 0
    vacances_types = vacances_df['description'].unique()
    for vac in vacances_types:
        df[f'Vacances_{vac}'] = 0

    # Marquer les jours de chaque période de vacances avec la valeur 1
    for _, row in vacances_df.iterrows():
        vac_column = f'Vacances_{row["description"]}'
        df.loc[(df['id_jour'] >= row['start_date']) & (df['id_jour'] <= row['end_date']), vac_column] = 1

    # Créer une colonne 'Jour_Semaine' qui contient le nom du jour
    df['Jour_Semaine'] = df['id_jour'].dt.day_name()

    # Liste complète des jours de la semaine
    jours_semaine_complet = ['Jour_Semaine_Monday', 'Jour_Semaine_Saturday', 'Jour_Semaine_Sunday', 'Jour_Semaine_Thursday', 'Jour_Semaine_Tuesday', 'Jour_Semaine_Wednesday']

    # Encodage one-hot avec tous les jours de la semaine
    df_temp = pd.get_dummies(df['Jour_Semaine'], columns=['Jour_Semaine'], drop_first=False)
    for jour in jours_semaine_complet:
        jour_seul = jour[13:]
        if jour_seul not in df_temp.columns:
            df[jour] = 0
        else :
            df[jour] = 1

    df = df.drop(['Jour_Semaine'], axis=1)  
    
    return df