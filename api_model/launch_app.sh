#!/bin/bash

model_name="third_run_2023"
absolute_path=$(readlink -f "$0")
script_dir=$(dirname "$absolute_path")
# Spécifiez le chemin du fichier à rechercher
fichier_a_chercher="${script_dir}/${model_name}.pkl"
echo $fichier_a_chercher
# Vérifiez si le fichier existe
if [ -f "$fichier_a_chercher" ]; then
    echo "Modele déja chargé"
else
    echo "Le model n est pas trouvé, chargement du modèle"
    # Exécutez votre script Python alternatif
    python -m api_model.model_loader $model_name;
fi
python -m api_model.main
# uvicorn api.main:app 