from azureml.core import Workspace
from azureml.core import Experiment
from dotenv import load_dotenv
import os

load_dotenv()

# Provide your workspace details
subscription_id = os.getenv("SUBSCRIPTION_ID")
resource_group = os.getenv("RESSOURCE_GROUP")
workspace_name = os.getenv("WORKSPACE_NAME")


ws = Workspace(subscription_id=subscription_id,
                resource_group=resource_group,
                workspace_name=workspace_name)
# Replace 'experiment_name' and 'run_name' with your actual experiment name and run name



experiment = Experiment(ws, 'predict_couverts')
print(dir(experiment))
# runs = [run for run in experiment.get_runs()]
# runs = next(run for run in experiment.get_runs() if run.tags['mlflow.runName']=='remote_run')
# print(runs.data.metrics)
