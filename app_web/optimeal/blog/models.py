from django.db import models

class Prediction(models.Model):
    # Assurez-vous que ces champs correspondent exactement à ceux de votre table SQL
    prediction = models.IntegerField()
    temperature = models.FloatField()
    nb_presence_sur_site = models.FloatField()
    id_jour = models.DateField()
    timestamp = models.DateTimeField()
    model = models.CharField(max_length=100)

    class Meta:
        db_table = 'predictions'  # Assurez-vous que cela correspond au nom de votre table
        # Si vous n'avez pas de champ 'id' dans votre table SQL, ajoutez ceci :
        managed = False  # Cela empêche Django de gérer cette table
        # Ajoutez cette ligne pour indiquer à Django de ne pas utiliser d'ID automatique
        abstract = True

    def __str__(self):
        return f"Prediction for {self.id_jour}"