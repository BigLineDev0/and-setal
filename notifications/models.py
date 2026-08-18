from django.db import models
from django.conf import settings

class Notification(models.Model):
    '''Modèle représentant une notification pour un utilisateur. Chaque notification est liée à un utilisateur spécifique et contient un titre, un message, un indicateur de lecture, ainsi que des dates de création et de fin optionnelles.'''

    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='notifications')
    titre = models.CharField(max_length=255)
    message = models.TextField()
    lu = models.BooleanField(default=False)
    date_fin = models.DateTimeField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        '''Renvoie une représentation lisible de la notification, incluant le nom d'utilisateur et le titre de la notification.'''
        return f"Notification pour {self.utilisateur.username}: {self.titre}"

    def marquer_comme_lue(self):
        """Marque la notification comme lue."""

        self.lu = True
        self.save(update_fields=['lu'])

    