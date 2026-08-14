from rest_framework import serializers
from .models import Intervention


class InterventionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intervention
        fields = ['id', 'signalement', 'agent', 'statut', 'photo', 'commentaire', 'date_creation', 'date_fin']
        read_only_fields = ['id', 'date_creation']
        