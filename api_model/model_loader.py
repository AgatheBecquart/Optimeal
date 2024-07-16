import pickle
import mlflow.pyfunc
from azureml.core import Workspace, Experiment
from dotenv import load_dotenv
import os
import argparse

# Create an argument parser
parser = argparse.ArgumentParser()

# Add arguments
parser.add_argument('run_name', default='third_run_2023')

# Parse the command-line arguments
args = parser.parse_args()

# Access the arguments
run_name = args.run_name

load_dotenv()

# Provide your workspace details
subscription_id = os.getenv("SUBSCRIPTION_ID")
resource_group = os.getenv("RESOURCE_GROUP")
workspace_name = os.getenv("WORKSPACE_NAME")

ws = Workspace(subscription_id=subscription_id,
               resource_group=resource_group,
               workspace_name=workspace_name)

experiment = Experiment(ws, "predict_couverts")
run = next(run for run in experiment.get_runs()
           if run.tags['mlflow.runName'] == run_name)
model_uri = f"runs:/{run.id}/{run_name}"
mlflow.set_tracking_uri(os.getenv("ML_FLOW_TRACKING_UI"))
loaded_model = mlflow.pyfunc.load_model(model_uri)

# Specify the path where you want to save the pickle file
pickle_file_path = f"api_model/{run_name}.pkl"

# Save the loaded model to a pickle file
with open(pickle_file_path, 'wb') as f:
    pickle.dump(loaded_model, f)
