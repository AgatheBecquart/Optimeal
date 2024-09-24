from model.utils import connect_to_database
import requests
import pandas as pd


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
                'start_date': pd.to_datetime(fields['start_date']).tz_localize(None),  # Remove timezone
                'end_date': pd.to_datetime(fields['end_date']).tz_localize(None),      # Remove timezone
                'description': fields['description'],
                'location': fields['location'],
                'description': fields['description'],
                'annee_scolaire': fields['annee_scolaire'],
                'zone': fields['zones']
            })

    return pd.DataFrame(vacances)

def feature_engineering(connection, run_name):

    df = pd.read_sql_query(f"SELECT * FROM {run_name}_CleanDataset",connection)

    # Convertir la colonne 'Date' en type datetime
    df['Jour_Semaine'] = df['id_jour'].dt.day_name()

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

    # Convertir la variable catégorielle 'Jour_Semaine' en variables indicatrices
    df = pd.get_dummies(df, columns=['Jour_Semaine'], drop_first=True)

     # Convertir les colonnes indicatrices de booléen à entier
    for col in df.columns:
        if df[col].dtype == 'bool':
            df[col] = df[col].astype(int)

    return df
    