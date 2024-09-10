import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Définir les chemins de base
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuration de sécurité
SECRET_KEY = os.getenv('SECRET_KEY', 'votre-cle-secrete-defaut')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0', 'optimeal-web-app.switzerlandnorth.azurecontainer.io']
ENCODED_JWT = os.getenv('ENCODED_JWT', 'votre-cle-secrete-defaut')
APPLICATIONINSIGHTS_CONNECTION_STRING = os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING', 'votre-cle-secrete-defaut')
print(APPLICATIONINSIGHTS_CONNECTION_STRING)
# Applications installées
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'authentication',
    'blog',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuration des URLs principales
ROOT_URLCONF = 'optimeal.urls'

# Configuration des templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.joinpath('templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Configuration WSGI
WSGI_APPLICATION = 'optimeal.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': os.getenv('DATABASE'),
        'USER': os.getenv('AZUREUSER'),
        'PASSWORD': os.getenv('PASSWORD'),
        'HOST': os.getenv('SERVER'),
        'PORT': '1433',  # Par défaut, SQL Server utilise le port 1433
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'extra_params': 'TrustServerCertificate=yes;',  # Utilisé si SSL est requis sans certificat valide
        },
    }
}


# Validation des mots de passe
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'authentication.validators.ContainsLetterValidator',
    },
    {
        'NAME': 'authentication.validators.ContainsNumberValidator',
    },
]

# Configuration internationale
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Fichiers statiques
STATIC_URL = '/static/'
# STATICFILES_DIRS = [BASE_DIR.joinpath('static/')]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Configuration par défaut pour les clés primaires
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Modèle utilisateur personnalisé
AUTH_USER_MODEL = 'authentication.User'

# URLs de redirection après login/logout
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = LOGIN_URL

# # Monitoring

MONITORING = os.getenv('MONITORING', default='True')

if MONITORING == 'True':
    # SET UP CONNECTION STRING
    from dotenv import load_dotenv
    import os
    load_dotenv()


    # PART 1 : SET UP LOGGING EXPORTER
    import logging
    from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
    from opentelemetry._logs import set_logger_provider
    from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
    from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter

    connection_string = APPLICATIONINSIGHTS_CONNECTION_STRING
    if not connection_string:
        raise ValueError("Instrumentation key or connection string cannot be none or empty.")

    exporter = AzureMonitorLogExporter(connection_string=connection_string)

    logger_provider = LoggerProvider()
    set_logger_provider(logger_provider)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))

    # Attach LoggingHandler to namespaced logger
    handler = LoggingHandler()
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)

    logger.setLevel(logging.INFO)


    # PART 2 : SET UP TRACE EXPORTER
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

    connection_string = APPLICATIONINSIGHTS_CONNECTION_STRING
    if not connection_string:
        raise ValueError("Instrumentation key or connection string cannot be none or empty.")

    trace_exporter = AzureMonitorTraceExporter(connection_string=connection_string)
    resource = Resource(attributes={"cloud.role": "DjangoApplication","service.name":"DjangoApplication"})
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))

    trace.set_tracer_provider(tracer_provider)
    tracer = trace.get_tracer(__name__)


    # PART 3 : Instrument Django and Request for automatic HTTP logging and tracing
    from opentelemetry.instrumentation.django import DjangoInstrumentor
    DjangoInstrumentor().instrument()
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    RequestsInstrumentor().instrument()




    # PART 4 : SET UP METRICS EXPORTER
    from opentelemetry import metrics
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter

    connection_string = APPLICATIONINSIGHTS_CONNECTION_STRING
    if not connection_string:
        raise ValueError("Instrumentation key or connection string cannot be none or empty.")

    metric_exporter = AzureMonitorMetricExporter(connection_string=connection_string)

    frequency_millis = 60000 #min
    reader = PeriodicExportingMetricReader(exporter=metric_exporter, export_interval_millis=frequency_millis)
    metrics.set_meter_provider(MeterProvider(metric_readers=[reader]))
    meter = metrics.get_meter_provider().get_meter("satisfaction_metrics")

    # Create metric instruments
    prediction_counter_per_minute = meter.create_counter("prediction_counter_per_minute")


