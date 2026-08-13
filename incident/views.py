from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import render
from rest_framework import generics
from .models import Incident
from .serializers import IncidentSerializer
from .services import declencher_analyse_ia  
from rest_framework.permissions import AllowAny

class IncidentListCreateView(generics.ListCreateAPIView):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    
    #  CORRECTION : Déplacez les parseurs ici, au niveau de la classe
    parser_classes = [MultiPartParser, FormParser] 
    permission_classes = [AllowAny]  # ✅ autorise les non-connectés

    def perform_create(self, serializer):
        # Associe l'utilisateur connecté à l'incident si authentifié
        if self.request.user.is_authenticated:
            incident = serializer.save(citoyen=self.request.user)
        else:
            incident = serializer.save() # Création anonyme si non connecté
            
        declencher_analyse_ia(incident)