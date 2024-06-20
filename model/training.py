from data_cleaning import data_cleaning
from feature_engineering import feature_engineering
from modelisation import modelisation
from utils import connect_to_database

def training(run_name, start_date="2023-01-01", end_date="2024-03-01"):

    connection = connect_to_database()
    df_clean = data_cleaning(connection,run_name,start_date,end_date)

    df_clean.to_sql(run_name +'_CleanDataset', connection, index=False, if_exists='replace')
    
    df_feat = feature_engineering(connection,run_name)
    df_feat.to_sql(run_name +'_TrainingDataset', connection, index=False, if_exists='replace')
    
    run_id = modelisation(connection,run_name)
    return run_id