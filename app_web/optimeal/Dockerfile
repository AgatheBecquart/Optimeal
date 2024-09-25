# pull official base image
FROM python:3.10-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Installer les dépendances nécessaires pour SQL Server et gnupg
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    apt-transport-https \
    unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg \
    && curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17
# Set work directory
WORKDIR /app

RUN mkdir /app/optimeal

# Install dependencies
COPY ./requirements.txt /app/optimeal/requirements.txt
RUN python -m pip install --no-cache-dir --upgrade -r /app/optimeal/requirements.txt

# Copy project
COPY . /app/optimeal

# Collect static files
RUN python /app/optimeal/manage.py collectstatic --noinput

# Expose port 8000
EXPOSE 8000

# Run the application
CMD ["gunicorn", "--bind", ":8000", "--chdir", "/app/optimeal", "--workers", "4", "optimeal.wsgi:application"]