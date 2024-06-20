import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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

# Connexion à la base de données SQLite
conn = connect_to_database()

# Fonction pour charger les données à partir de la base de données
def load_data_prediction():
    query = f"SELECT * FROM predictions;"
    df = pd.read_sql(query, conn)
    return df

def load_data_training(model_name):
    if model_name != "tous":
        query = f"SELECT * FROM {model_name}_TrainingDataset;"
    else:
        query = f"SELECT * FROM first_run_2023_TrainingDataset;"
    df = pd.read_sql(query, conn)
    return df

def plot_score_distribution(predictions_data,training_data):
    # Créer une figure avec deux sous-graphiques
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    # Premier sous-graphique : Distribution des nb_couverts pour la table "predictions"
    sns.countplot(data=predictions_data, x='prediction', ax=axes[0])
    axes[0].set_title('Distribution du nombre de couverts - Prédictions')
    # Deuxième sous-graphique : Distribution des nb_couverts pour la table "Training"
    sns.countplot(data=training_data, x='nb_couvert', ax=axes[1])
    axes[1].set_title('Distribution du nombre de couverts - Entraînement')
    # Afficher les graphiques
    st.pyplot(fig)

def plot_variable_distribution(predictions_data,training_data,variable):
    # Créer une figure avec deux sous-graphiques
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    # Premier sous-graphique : Distribution des scores pour la table "predictions"
    sns.histplot(data=predictions_data,  x=variable, ax=axes[0], kde=True)
    axes[0].set_title('Distribution de {variable} - Prédictions')
    # Deuxième sous-graphique : Distribution des scores pour la table "Training"
    sns.histplot(data=training_data,  x=variable, ax=axes[1], kde=True)
    axes[1].set_title('Distribution de {variable} - Entraînement')
    # Afficher les graphiques
    st.pyplot(fig)



# Charger les données des tables "predictions" et "Training"
predictions_data = load_data_prediction()

# Sidebar pour la sélection du modèle
st.sidebar.header('Sélection du modèle')
selected_model = st.sidebar.selectbox('Choisissez un modèle',['tous'] + list(predictions_data['model'].unique()))

# Filtrer les données en fonction du modèle sélectionné
if selected_model != 'tous':
    filtered_predictions_data = predictions_data[predictions_data['model'] == selected_model]
else:
    filtered_predictions_data = predictions_data

filtered_training_data = load_data_training(selected_model)


# Titre de l'application
st.title('Evaluation du drift')

# Partie "Evaluation du prediction drift"
st.header('Evaluation du drift sur la distribution des prédictions')

plot_score_distribution(filtered_predictions_data,filtered_training_data)

# Partie "Evaluation du data drift"
st.header('Evaluation du drift sur la distribution des variables explicatives')

# Sélection de la variable explicative à afficher
selected_variable = st.selectbox('Sélectionnez une variable explicative', ['temperature', 'nb_presence_sur_site'])

# Affichage de la distribution de la variable explicative sélectionnée
plot_variable_distribution(filtered_predictions_data,filtered_training_data, selected_variable)

