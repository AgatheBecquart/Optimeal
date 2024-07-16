# Utiliser une image de base tiangolo/uvicorn-gunicorn-fastapi:python3.10
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

# Définir le répertoire de travail
WORKDIR /app

# Installer unixodbc et le pilote ODBC pour SQL Server
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Installer le pilote ODBC pour SQL Server
RUN apt-get update && apt-get install -y \
    curl \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Créer le répertoire de l'application
RUN mkdir -p /app/api_data

# Copier les fichiers de dépendances
COPY ./requirements.txt /app/api_data/requirements.txt

# Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade -r /app/api_data/requirements.txt

# Copier le code de l'application
COPY . /app/api_data

# Définir le répertoire de travail pour l'application
WORKDIR /app/api_data

# Exposer le port de l'application
EXPOSE 8000

# Commande pour démarrer l'application avec Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
