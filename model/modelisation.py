from model.utils import connect_to_database
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_squared_log_error, mean_absolute_error
import mlflow
from dotenv import load_dotenv
import os


def modelisation(connection, run_name, start_date="2023-01-01", end_date="2024-03-01"):

    # Perform model training and evaluation using linear regression.

    # Args:
    #     connection (object): Database connection object.
    #     run_name (str): Name of the run.
    #     start_date (str, optional): Start date for the experiment. Defaults to "2023-01-01".
    #     end_date (str, optional): End date for the experiment. Defaults to "2024-03-01".

    # Returns:
    #     str: The ID of the MLflow run.

    load_dotenv()

    mlflow.set_tracking_uri(os.environ.get("ML_FLOW_TRACKING_UI"))

    modelisation_query = f"""
    SELECT 
        *
    FROM 
        {run_name}_TrainingDataset
    """

    df = pd.read_sql_query(modelisation_query, connection)
    # df = df.dropna()

    # Séparer les caractéristiques (X) de la variable cible (y)
    X = df.drop(['nb_couvert', 'id_jour'], axis=1)  # Caractéristiques
    y = df['nb_couvert']  # Variable cible
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.8, random_state=42)

    # Set the experiment name or ID
    experiment_name = "predict_couverts" if run_name != "test_run" else "test_experiment"

    # Get or create the experiment
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        experiment_id = mlflow.create_experiment(experiment_name)
    else:
        experiment_id = experiment.experiment_id

    with mlflow.start_run(experiment_id=experiment_id, run_name=run_name) as run:
        model = LinearRegression()
        model.fit(X_train, y_train)

        mlflow.set_tag("start_date", start_date)
        mlflow.set_tag("end_date", end_date)

        # Predictions for training set
        y_train_pred = model.predict(X_train)
        y_train_pred = [max(0, pred) for pred in y_train_pred]  # Handling negative predictions

        # Metrics for the training set
        mse_train = round(mean_squared_error(y_train, y_train_pred), 4)
        r2_train = round(r2_score(y_train, y_train_pred), 4)
        rmse_train = round(mean_squared_error(y_train, y_train_pred, squared=False), 4)  # RMSE
        mae_train = round(mean_absolute_error(y_train, y_train_pred), 4)
        msle_train = round(mean_squared_log_error(y_train, y_train_pred), 4)

        mlflow.log_metric("mse_train", mse_train)
        mlflow.log_metric("r2_train", r2_train)
        mlflow.log_metric("rmse_train", rmse_train)
        mlflow.log_metric("mae_train", mae_train)
        mlflow.log_metric("msle_train", msle_train)

        print(f"Pour le jeu d'entrainement: \n le R2 est de {r2_train}, \n le MSE est de {mse_train}, \n le RMSE de {rmse_train}, \n le MAE de {mae_train}, \n et le MSLE de {msle_train}")

        # Predictions for test set
        y_test_pred = model.predict(X_test)
        y_test_pred = [max(0, pred) for pred in y_test_pred]  # Handling negative predictions

        # Metrics for the test set
        mse_test = round(mean_squared_error(y_test, y_test_pred), 4)
        r2_test = round(r2_score(y_test, y_test_pred), 4)
        rmse_test = round(mean_squared_error(y_test, y_test_pred, squared=False), 4)  # RMSE
        mae_test = round(mean_absolute_error(y_test, y_test_pred), 4)
        msle_test = round(mean_squared_log_error(y_test, y_test_pred), 4)

        mlflow.log_metric("mse_test", mse_test)
        mlflow.log_metric("r2_test", r2_test)
        mlflow.log_metric("rmse_test", rmse_test)
        mlflow.log_metric("mae_test", mae_test)
        mlflow.log_metric("msle_test", msle_test)

        print(f"Pour le jeu de test: \n le R2 est de {r2_test}, \n le MSE est de {mse_test}, \n le RMSE de {rmse_test}, \n le MAE de {mae_test}, \n et le MSLE de {msle_test}")

        # Save the model to MLflow
        mlflow.sklearn.log_model(model, run_name)
        run_id = run.info.run_id
    return run_id

if __name__ == "__main__":
    connection = connect_to_database()

# Le Mean Squared Logarithmic Error (MSLE) est pertinent dans le cadre de ce projet, car il pénalise plus fortement les sous-prévisions que les sur-prévisions. 
# Dans le contexte de la prévision du nombre de couverts dans une cantine, il est crucial de s'assurer que le nombre de repas prévus soit au moins égal 
# au nombre réel de personnes présentes, pour éviter qu'il manque des repas.
# Le MSLE utilise une transformation logarithmique qui accentue les erreurs lorsque le modèle sous-estime, mais reste plus tolérant vis-à-vis des sur-prévisions. 
# Cela correspond bien à votre besoin de minimiser les risques de sous-prévisions, car prévoir trop peu de repas peut entraîner des conséquences plus importantes 
# (des personnes sans repas) que d'en prévoir trop (surplus de nourriture).