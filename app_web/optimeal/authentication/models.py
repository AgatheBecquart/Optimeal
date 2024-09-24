from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Les champs username, password, email, first_name et last_name sont déjà inclus dans AbstractUser
    # Nous ajoutons donc seulement les champs supplémentaires
    zip_code_prefix = models.CharField(max_length=10, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)

