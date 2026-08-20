from rest_framework import serializers
from .models import Intervention


class InterventionSerializer(serializers.ModelSerializer):
    agent = serializers.SerializerMethodField()

    class Meta:
        model = Intervention
        fields = ['id', 'signalement', 'agent', 'statut', 'photo', 'commentaire', 'date_creation', 'date_fin']
        read_only_fields = ['id', 'date_creation', 'agent']


    def get_agent(self, obj):
        if obj.agent:
            return {
                "prenom": obj.agent.first_name,
                "nom": obj.agent.last_name
            }
        return None