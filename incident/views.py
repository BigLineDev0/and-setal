from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import render
from rest_framework import generics
from .models import Incident
from .serializers import IncidentSerializer
from .services import declencher_analyse_ia  
from rest_framework.permissions import AllowAny, IsAuthenticated

class IncidentListCreateView(generics.ListCreateAPIView):  # ListCreateAPIView est une vue générique qui combine la liste et la création d'objets
    serializer_class = IncidentSerializer
    
    # Obligatoire pour intercepter les fichiers et les formulaires
    parser_classes = [MultiPartParser, FormParser] 
    

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]        # création : autorise les non-connectés
        return [IsAuthenticated()]     # lecture : connexion obligatoire


    def perform_create(self, serializer):
        # Associe l'utilisateur connecté à l'incident si authentifié
        if self.request.user.is_authenticated:
            incident = serializer.save(citoyen=self.request.user)
        else:
            incident = serializer.save() # Création anonyme si non connecté
            
        declencher_analyse_ia(incident)


    def get_queryset(self):
        
        queryset = Incident.objects.filter(citoyen=self.request.user)
        statut = self.request.query_params.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)  
        
        priorite = self.request.query_params.get('priorite')  
        if priorite:
            queryset = queryset.filter(priorite=priorite)

        return queryset


class IncidentDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = IncidentSerializer

    def get_queryset(self):
        return Incident.objects.filter(citoyen=self.request.user)