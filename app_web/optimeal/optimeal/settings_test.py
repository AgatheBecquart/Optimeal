import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Définir les chemins de base
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuration de sécurité
SECRET_KEY = os.getenv("SECRET_KEY", "votre-cle-secrete-defaut")
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "0.0.0.0",
    "optimeal-web-app.switzerlandnorth.azurecontainer.io",
]
ENCODED_JWT = os.getenv("ENCODED_JWT", "votre-cle-secrete-defaut")


# Applications installées
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "authentication",  # Assurez-vous que cette ligne est présente
    "blog",
]

# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Configuration des URLs principales
ROOT_URLCONF = "optimeal.urls"

# Configuration des templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR.joinpath("templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Configuration WSGI
WSGI_APPLICATION = "optimeal.wsgi.application"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}


# Validation des mots de passe
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    {
        "NAME": "authentication.validators.ContainsLetterValidator",
    },
    {
        "NAME": "authentication.validators.ContainsNumberValidator",
    },
]

# Configuration internationale
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Fichiers statiques
STATIC_URL = "/static/"
# STATICFILES_DIRS = [BASE_DIR.joinpath('static/')]
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Configuration par défaut pour les clés primaires
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Modèle utilisateur personnalisé
AUTH_USER_MODEL = "authentication.CustomUser"

# URLs de redirection après login/logout
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "login"

# # Monitoring

MONITORING = os.getenv("MONITORING", default=False)

if MONITORING:
    import optimeal.opentelemetry_setup

