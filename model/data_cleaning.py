import pandas as pd
from model.utils import connect_to_database


def data_cleaning(connection, run_name, start_date, end_date):

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    # Query to get presence data
    presence_query = """
                    SELECT 	
                        date_j,
                        count(id_agent_anonymise)/2 as nb_presence_sur_site
                    FROM
                        [dbo].[PresenceRH]
                    GROUP BY 
                        date_j
                    ORDER BY 
                        date_j DESC
                    """
    df_presence = pd.read_sql_query(presence_query, connection)

    # Convert 'date_demi_j' column to datetime
    df_presence["date_j"] = pd.to_datetime(df_presence["date_j"])

    # Query to get meal sales data
    couverts_query = """
    SELECT * FROM RepasVendus
    """
    df_couverts = pd.read_sql_query(couverts_query, connection)

    # Convert 'id_jour' column to datetime
    df_couverts["id_jour"] = pd.to_datetime(df_couverts["id_jour"], dayfirst=True)

    # Query to get weather data
    temperature_query = """ 
    SELECT * FROM Meteo 
    """
    df_temperature = pd.read_sql_query(temperature_query, connection)

    # Convert 'id_jour' column to datetime
    df_temperature["id_jour"] = pd.to_datetime(df_temperature["id_jour"])

    # Merge presence data with weather data on 'date_demi_j' and 'id_jour'
    df_merged = pd.merge(
        df_temperature, df_presence, left_on="id_jour", right_on="date_j", how="left"
    )

    # Drop the redundant 'date_demi_j' column
    df_merged.drop("date_j", axis=1, inplace=True)

    # Merge the result with meal sales data on 'id_jour'
    df = pd.merge(df_merged, df_couverts, on="id_jour", how="inner")

    # Filter df between start_date and end_date
    df = df[(df.id_jour >= start_date) & (df.id_jour <= end_date)]

    # Fill NaN values with 0
    df = df.fillna(0)

    return df
