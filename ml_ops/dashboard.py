import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_squared_log_error

def connect_to_database():
    load_dotenv()
    hostname = os.getenv("SERVER")
    database = os.getenv("DATABASE")
    username = os.getenv("AZUREUSER")
    password = os.getenv("PASSWORD")
    azure_connection_string = f"mssql+pyodbc://{username}:{password}@{hostname}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
    connection = create_engine(azure_connection_string)
    return connection

conn = connect_to_database()

def load_data_prediction():
    query = "SELECT * FROM predictions;"
    df = pd.read_sql(query, conn)
    df['id_jour'] = pd.to_datetime(df['id_jour'], format='%Y-%m-%d', errors='coerce')
    df = df.rename(columns={'temperature': 'temp'})
    return df

def load_data_training(model_name):
    if model_name != "tous":
        query = f"SELECT * FROM {model_name}_TrainingDataset;"
    else:
        query = "SELECT * FROM run_final_TrainingDataset;"
    df = pd.read_sql(query, conn)
    df['id_jour'] = pd.to_datetime(df['id_jour'], format='%Y-%m-%d', errors='coerce')
    return df

def plot_prediction_vs_actual(predictions_data, training_data):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.scatter(training_data['id_jour'], training_data['nb_couvert'], label='Valeurs réelles', alpha=0.5)
    ax.scatter(predictions_data['id_jour'], predictions_data['prediction'], label='Prédictions', alpha=0.5)
    ax.set_xlabel('Date')
    ax.set_ylabel('Nombre de couverts')
    ax.set_title('Prédictions vs Valeurs réelles')
    ax.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig)

def plot_error_distribution(predictions_data, training_data):
    merged_data = pd.merge(predictions_data, training_data[['id_jour', 'nb_couvert']], on='id_jour', how='inner')
    merged_data['error'] = merged_data['prediction'] - merged_data['nb_couvert']
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.histplot(data=merged_data, x='error', kde=True, ax=ax)
    ax.set_xlabel('Erreur de prédiction')
    ax.set_ylabel('Fréquence')
    ax.set_title('Distribution des erreurs de prédiction')
    st.pyplot(fig)

def calculate_metrics(predictions_data, training_data):
    merged_data = pd.merge(predictions_data, training_data[['id_jour', 'nb_couvert']], on='id_jour', how='inner')
    mae = mean_absolute_error(merged_data['nb_couvert'], merged_data['prediction'])
    rmse = np.sqrt(mean_squared_error(merged_data['nb_couvert'], merged_data['prediction']))
    mape = np.mean(np.abs((merged_data['nb_couvert'] - merged_data['prediction']) / merged_data['nb_couvert'])) * 100
    r2 = r2_score(merged_data['nb_couvert'], merged_data['prediction'])
    
    # Calculer MSLE en gérant les valeurs négatives
    y_true = np.maximum(merged_data['nb_couvert'], 0)  # Remplacer les valeurs négatives par 0
    y_pred = np.maximum(merged_data['prediction'], 0)  # Remplacer les valeurs négatives par 0
    msle = np.mean(np.square(np.log1p(y_true) - np.log1p(y_pred)))
    
    return mae, rmse, mape, r2, msle

st.set_page_config(layout="wide", page_title="Monitoring du Modèle OptimEAL")

st.title("Dashboard de Monitoring du Modèle OptimEAL")

st.sidebar.header("Paramètres")
selected_model = st.sidebar.selectbox("Choisissez un modèle", ["run_final"])

predictions_data = load_data_prediction()
if selected_model != "tous":
    predictions_data = predictions_data[predictions_data["model"] == selected_model]

training_data = load_data_training(selected_model)

st.header("Métriques de Performance du Modèle")
st.markdown("""
Les métriques suivantes sont utilisées pour évaluer la performance du modèle :
- **MAE (Mean Absolute Error)** : Mesure l'erreur moyenne absolue entre les prédictions et les valeurs réelles.
- **RMSE (Root Mean Square Error)** : Mesure la racine carrée de l'erreur quadratique moyenne, donnant plus de poids aux grandes erreurs.
- **MAPE (Mean Absolute Percentage Error)** : Mesure l'erreur moyenne en pourcentage, utile pour comprendre l'ampleur relative des erreurs.
- **R² (Coefficient de détermination)** : Indique la proportion de la variance dans la variable dépendante qui est prévisible à partir de la variable indépendante.
- **MSLE (Mean Squared Logarithmic Error)** : Mesure l'erreur quadratique moyenne des logarithmes, pénalisant davantage les sous-estimations que les surestimations.
""")

mae, rmse, mape, r2, msle = calculate_metrics(predictions_data, training_data)
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("MAE", f"{mae:.2f}")
col2.metric("RMSE", f"{rmse:.2f}")
col3.metric("MAPE", f"{mape:.2f}%")
col4.metric("R²", f"{r2:.4f}")
col5.metric("MSLE", f"{msle:.4f}")

st.markdown(f"""
### Interprétation des métriques

1. **MAE (Mean Absolute Error)** : Cette métrique indique en moyenne de combien nos prédictions s'écartent des valeurs réelles. Une MAE de {mae:.2f} signifie qu'en moyenne, nos prédictions sont à plus ou moins {mae:.2f} couverts de la valeur réelle.

2. **RMSE (Root Mean Square Error)** : Le RMSE est similaire au MAE, mais il pénalise davantage les grandes erreurs. Un RMSE de {rmse:.2f} indique que la plupart de nos erreurs de prédiction se situent dans cette plage, mais qu'il peut y avoir des erreurs plus importantes.

3. **MAPE (Mean Absolute Percentage Error)** : Cette métrique nous donne une idée de l'ampleur relative de nos erreurs. Un MAPE de {mape:.2f}% signifie qu'en moyenne, nos prédictions s'écartent de {mape:.2f}% de la valeur réelle.

4. **R² (Coefficient de détermination)** : Cette valeur varie entre 0 et 1, où 1 indique une prédiction parfaite. Un R² de {r2:.4f} signifie que notre modèle explique {r2*100:.2f}% de la variabilité des données.

5. **MSLE (Mean Squared Logarithmic Error)** : Cette métrique est particulièrement pertinente pour notre cas d'usage. Elle pénalise plus fortement les sous-prévisions que les sur-prévisions, ce qui est crucial dans le contexte de la prévision du nombre de couverts dans une cantine. Un MSLE de {msle:.4f} indique la précision de nos prédictions en tenant compte de cette asymétrie.

### Quelle métrique privilégier ?

Pour la prédiction du nombre de couverts à la cantine, le MSLE et le MAPE sont probablement les métriques les plus pertinentes à considérer :

- Le **MSLE** est particulièrement important car il pénalise davantage les sous-estimations. Dans le contexte d'une cantine, prévoir trop peu de repas (sous-estimation) est plus problématique que d'en prévoir trop (surestimation). Le MSLE nous aide à minimiser le risque de manquer de repas.

- Le **MAPE** donne une idée claire de l'erreur en pourcentage, ce qui est facilement interprétable pour les gestionnaires de la cantine. Par exemple, un MAPE de 10% signifierait que nos prédictions sont en moyenne à plus ou moins 10% du nombre réel de couverts.

Le MAE et le RMSE sont également utiles pour une compréhension plus approfondie de la performance du modèle en termes absolus, tandis que le R² nous donne une idée de la qualité globale de l'ajustement du modèle.

En privilégiant le MSLE, nous nous assurons que notre modèle tend à légèrement surestimer plutôt que sous-estimer, ce qui est préférable dans le contexte de la gestion d'une cantine où il vaut mieux avoir un peu trop de repas que pas assez.
""".format(mae=mae, rmse=rmse, mape=mape, r2=r2, msle=msle))

st.header("Visualisation des Prédictions")
plot_prediction_vs_actual(predictions_data, training_data)

st.header("Distribution des Erreurs de Prédiction")
plot_error_distribution(predictions_data, training_data)

st.header("Analyse des Variables Explicatives")
column_mapping = {
    'temp': 'Température',
    'nb_presence_sur_site': 'Nombre de présences sur site'
}

common_variables = list(set(predictions_data.columns) & set(training_data.columns))
common_variables = [col for col in common_variables if col in column_mapping]

selected_variable = st.selectbox("Sélectionnez une variable explicative", [column_mapping[col] for col in common_variables])
selected_variable_original = [col for col, name in column_mapping.items() if name == selected_variable][0]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
sns.scatterplot(data=predictions_data, x=selected_variable_original, y='prediction', ax=ax1)
ax1.set_title(f"Relation entre {selected_variable} et les prédictions")
ax1.set_xlabel(selected_variable)
ax1.set_ylabel("Prédiction")

sns.scatterplot(data=training_data, x=selected_variable_original, y='nb_couvert', ax=ax2)
ax2.set_title(f"Relation entre {selected_variable} et les valeurs réelles")
ax2.set_xlabel(selected_variable)
ax2.set_ylabel("Nombre de couverts réels")

st.pyplot(fig)
