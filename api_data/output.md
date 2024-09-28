README - Script d\'extraction des données
=========================================

Description
-----------

Ce dossier contient les scripts nécessaires pour l\'extraction, le
traitement et l\'insertion des données dans une base de données SQL
Server pour le projet de prévision des couverts de la cantine de la
Banque Populaire du Nord.

Fichiers principaux
-------------------

-   **create\_table.py** : Script principal pour la création des tables
    et l\'insertion des données.
-   **drop\_table.py** : Script pour supprimer les tables existantes.
-   **models.py** : Définition des modèles de données utilisés dans le
    projet.

Dépendances
-----------

Le script utilise plusieurs bibliothèques Python. Assurez-vous d\'avoir
installé :

-   pyodbc
-   python-dotenv
-   requests
-   pytz

Vous pouvez les installer avec pip :

    pip install pyodbc python-dotenv requests pytz

Configuration
-------------

Créez un fichier **.env** à la racine du projet avec les variables
suivantes :

Assurez-vous d\'avoir le pilote ODBC 17 pour SQL Server installé sur
votre système.

Fonctionnalités principales
---------------------------

### Création des tables

Le script crée trois tables principales :

-   **Meteo** : Stocke les données météorologiques.
-   **RepasVendus** : Enregistre le nombre de couverts vendus par jour.
-   **PresenceRH** : Contient les données de présence des employés.

La structure de ces tables est définie dans : *\[ajoutez le lien ou la
référence ici\]*

### Extraction et insertion des données météorologiques

Les données météorologiques sont récupérées via l\'API OpenWeatherMap.
La fonction **get\_weather\_data\_for\_period** effectue les requêtes
API pour une période donnée. Les données sont ensuite insérées dans la
table Meteo à l\'aide de la fonction **insert\_weather\_data**.

Voir les détails dans : *\[ajoutez le lien ou la référence ici\]*

### Importation des données CSV

Les données de repas vendus et de présence RH sont importées à partir de
fichiers CSV. La fonction **insert\_csv\_data** gère l\'insertion de ces
données dans les tables respectives.

Pour la table PresenceRH, les identifiants des agents sont anonymisés
avant l\'insertion.

Référez-vous à : *\[ajoutez le lien ou la référence ici\]*

### Anonymisation des données

Pour respecter le RGPD, les identifiants des agents sont anonymisés
avant l\'insertion dans la base de données :

Utilisation
-----------

Pour créer les tables et insérer les données :

    python create_table.py

Pour supprimer les tables existantes :

    python drop_table.py

Gestion des erreurs
-------------------

Le script inclut une gestion des erreurs pour chaque étape du processus,
avec des messages d\'erreur détaillés en cas de problème lors de
l\'insertion ou de la récupération des données.

Modèles de données
------------------

Les modèles de données sont définis dans **models.py** pour assurer la
cohérence et la validation des données :

Remarques importantes
---------------------

-   Assurez-vous que les fichiers CSV sont placés dans le dossier
    **data/** avant l\'exécution du script.
-   Le script est configuré pour récupérer les données météorologiques
    de Marcq-en-Baroeul (coordonnées : lat = 50.6788, lon = 3.0915).
-   La période de récupération des données météorologiques est
    actuellement fixée du **01/09/2023 au 28/09/2024**. Modifiez ces
    dates si nécessaire.

Sécurité
--------

-   Les informations sensibles (identifiants de connexion, clés API)
    sont stockées dans le fichier **.env** et ne doivent pas être
    partagées ou versionnées.
-   Les identifiants des agents sont anonymisés pour respecter le RGPD.

Ce README fournit une documentation détaillée du script d\'extraction
des données, couvrant sa configuration, ses fonctionnalités principales,
et son utilisation.
