
from rest_framework import serializers
from .models import Incident


class IncidentSerializer(serializers.ModelSerializer):
    type_incident = serializers.SerializerMethodField()
    citoyen = serializers.SerializerMethodField()
    
    class Meta:
        model = Incident
        fields = ['id','statut', 'description', 'messageVocal', 'longitude', 'latitude', 'dateCreation', 'dateModification', 'priorite', 'urlImage', 'type_incident', 'citoyen']
        read_only_fields = ['id', 'statut', 'dateCreation', 'dateModification', 'priorite', 'type_incident', 'citoyen']



    def get_type_incident(self, obj):

        # Récupère le type d'incident associé à l'objet Incident via la relation avec AnalyseIA
        analyse = obj.analyseia_set.first()  #  first() pour obtenir le premier objet AnalyseIA associé à l'incident ou .get() avec try/except
        return analyse.type_incident if analyse else None

    def get_citoyen(self, obj):
        if obj.citoyen:
            return {
                "id": obj.citoyen.id,
                "prenom": obj.citoyen.first_name,
                "nom": obj.citoyen.last_name,
                "email": obj.citoyen.email,
            }
        return None  # signalement anonyme