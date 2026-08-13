
from rest_framework import serializers
from .models import Incident


class IncidentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Incident
        fields = ['id','statut', 'description', 'messageVocal', 'longitude', 'latitude', 'dateCreation', 'dateModification', 'priorite', 'urlImage']
        read_only_fields = ['id', 'statut', 'dateCreation', 'dateModification', 'priorite']