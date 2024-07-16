from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

def connect_to_database():
    load_dotenv()
    # Define your PostgreSQL connection parameters
    hostname = os.getenv("SERVER")
    database = os.getenv("DATABASE")
    username = os.getenv("AZUREUSER")
    password = os.getenv("PASSWORD")

    # Créer la chaîne de connexion
    azure_connection_string = f"mssql+pyodbc://{username}:{password}@{hostname}/{database}?driver=ODBC+Driver+17+for+SQL+Server"

    # Créer le moteur SQLAlchemy
    connection = create_engine(azure_connection_string)

    return connection

def get_run(run_name,experiment_name):
    from azureml.core import Workspace
    from azureml.core import Experiment
    from dotenv import load_dotenv
    import os

    load_dotenv()

    # Provide your workspace details
    subscription_id = os.getenv("SUBSCRIPTION_ID")
    resource_group = os.getenv("RESOURCE_GROUP")
    workspace_name = os.getenv("WORKSPACE_NAME")


    ws = Workspace(subscription_id=subscription_id,
                    resource_group=resource_group,
                    workspace_name=workspace_name)


    experiment = Experiment(ws, experiment_name)
    # runs = [run for run in experiment.get_runs()]
    run = next(run for run in experiment.get_runs() if run.tags['mlflow.runName']==run_name)
    return run