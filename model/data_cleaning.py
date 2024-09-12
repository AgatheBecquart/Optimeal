import pandas as pd
from model.utils import connect_to_database


def data_cleaning(connection, run_name, start_date="2023-01-01", end_date="2024-03-01"):
    # Query to get presence data
    presence_query = """
    SELECT * FROM PresenceRH
    """
    df_presence = pd.read_sql_query(presence_query, connection)

    # Convert 'date_demi_j' column to datetime
    df_presence['date_demi_j'] = pd.to_datetime(df_presence['date_demi_j'])

    # Extract hour and determine time of day (morning or afternoon)
    df_presence['Moment'] = df_presence['date_demi_j'].dt.hour.apply(lambda x: 'Matin' if x == 8 else 'Après-midi')
    df_presence['date_demi_j'] = df_presence['date_demi_j'].dt.date

    # Motifs de présence correspondant à une présence sur site
    motifs_sur_site = ['Lieu de travail Forfait Jour']

    # Renommer le type de présence en 'PS' pour les motifs sur site
    df_presence.loc[df_presence['lib_motif'].isin(motifs_sur_site), 'type_presence'] = 'PS'

    # Filter data for presence type "PS"
    presence_data = df_presence[df_presence['type_presence'] == 'PS']

    # Aggregate presence data by date
    presence_aggregated = presence_data.groupby('date_demi_j').size().reset_index(name='nb_presence_sur_site')
    
    # Convert 'date_demi_j' column to datetime
    presence_aggregated['date_demi_j'] = pd.to_datetime(presence_aggregated['date_demi_j'])

    # Query to get meal sales data
    couverts_query = """
    SELECT * FROM RepasVendus
    """
    df_couverts = pd.read_sql_query(couverts_query, connection)

    # Convert 'id_jour' column to datetime
    df_couverts['id_jour'] = pd.to_datetime(df_couverts['id_jour'], dayfirst=True)

    # Query to get weather data
    temperature_query = """ 
    SELECT * FROM Meteo 
    """
    df_temperature = pd.read_sql_query(temperature_query, connection)

    # Convert 'id_jour' column to datetime
    df_temperature['id_jour'] = pd.to_datetime(df_temperature['id_jour'])

    # Merge presence data with weather data on 'date_demi_j' and 'id_jour'
    df_merged = pd.merge(df_temperature, presence_aggregated, left_on='id_jour', right_on='date_demi_j', how='left')

    # Drop the redundant 'date_demi_j' column
    df_merged.drop('date_demi_j', axis=1, inplace=True)

    # Merge the result with meal sales data on 'id_jour'
    df = pd.merge(df_merged, df_couverts, on='id_jour', how='inner')

    # Filter df between start_date and end_date
    df = df[(df.id_jour >= start_date) & (df.id_jour <= end_date)] 

    # Fill NaN values with 0
    df = df.fillna(0)

    return df

if __name__ == "__main__":

    # Créer le moteur SQLAlchemy
    connection = connect_to_database()
    df = data_cleaning(connection, "first_run_2023", start_date="2023-01-01", end_date="2024-03-01")
    df.to_sql("first_run_2023" +'_CleanDataset', connection, index=False, if_exists='replace')
