FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

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
    
RUN mkdir /app/api_model

COPY ./requirements.txt /app/api_model/requirements.txt

RUN python -m pip install --no-cache-dir --upgrade  -r /app/api_model/requirements.txt

COPY . /app/api_model

# ENV PATH ${APP_ROOT}/.local/bin:${PATH}

CMD ["/app/api_model/launch_app.sh"]