
from rest_framework import serializers

from incident.utilis import reverse_geocode
from .models import Incident


class IncidentSerializer(serializers.ModelSerializer):
    type_incident = serializers.SerializerMethodField()
    citoyen = serializers.SerializerMethodField()
    
    class Meta:
        model = Incident
        fields = ['id','statut', 'description', 'messageVocal', 'longitude', 'latitude', 'adresse','dateCreation', 'dateModification', 'priorite', 'urlImage', 'type_incident', 'citoyen']
        read_only_fields = ['id', 'statut', 'dateCreation', 'dateModification', 'priorite', 'type_incident', 'citoyen', 'adresse']  # Champs en lecture seule



    def get_type_incident(self, obj):

        # Récupère le type d'incident associé à l'objet Incident via la relation avec AnalyseIA
        analyse = obj.analyseia_set.first()  #  first() pour obtenir le premier objet AnalyseIA associé à l'incident ou .get() avec try/except
        return analyse.type_incident if analyse else None

    # Récupère les informations du citoyen associé à l'incident
    def get_citoyen(self, obj):
        if obj.citoyen:
            return {
                "id": obj.citoyen.id,
                "prenom": obj.citoyen.first_name,
                "nom": obj.citoyen.last_name,
                "email": obj.citoyen.email,
            }
        return None  # signalement anonyme

    # Lors de la création d'un incident, on peut utiliser la fonction reverse_geocode pour remplir automatiquement le champ adresse à partir des coordonnées GPS fournies.
    def create(self, validated_data):
        latitude = validated_data.get('latitude')
        longitude = validated_data.get('longitude')

        if latitude is not None and longitude is not None:
            validated_data['adresse'] = reverse_geocode(
                latitude,
                longitude
            )

        return super().create(validated_data)