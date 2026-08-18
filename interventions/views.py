from django.shortcuts import render
from rest_framework import generics, request
from rest_framework.response import Response
from rest_framework.permissions import  IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser

from incident.models import Incident
from interventions.models import Intervention
from comptes.permissions import EstAdmin 
from interventions.serializers import InterventionSerializer
from interventions.services import annuler_intervention, demarrer_intervention, terminer_intervention

# Create your views here.

class DemarrerInterventionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id_incident):
        incident = get_object_or_404(Incident, id=id_incident)
        intervention = demarrer_intervention(incident, request.user)
        serializer = InterventionSerializer(intervention)
        return Response(serializer.data, status=201)


class TerminerInterventionView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, id_intervention):
        intervention = get_object_or_404(Intervention, id=id_intervention)
        
        commentaire = request.data.get('commentaire') # Retourne None si le champ n'est pas présent contrairement à request.data['commentaire'] qui lèverait une exception
        photo = request.FILES.get('photo') # FILES est utilisé pour récupérer les fichiers envoyés dans la requête, comme les images ou les documents. Si le champ 'photo' n'est pas présent, photo sera None.
        
        terminer_intervention(intervention, commentaire, photo)
        
        serializer = InterventionSerializer(intervention)
        return Response(serializer.data, status=200)

class AnnulerInterventionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id_intervention):
        intervention = get_object_or_404(Intervention, id=id_intervention)
        annuler_intervention(intervention)
        serializer = InterventionSerializer(intervention)
        return Response(serializer.data, status=200)


 
class InterventionListView(generics.ListAPIView):
    serializer_class = InterventionSerializer
    permission_classes = [EstAdmin]  # seuls l'admin peut voir toutes les interventions

    def get_queryset(self):
        return Intervention.objects.all()


class MesInterventionsView(generics.ListAPIView):
    serializer_class = InterventionSerializer
    permission_classes = [IsAuthenticated]  # seul l'agent connecté peut voir ses propres interventions

    def get_queryset(self):
        return Intervention.objects.filter(agent=self.request.user) # filtrer par l'agent