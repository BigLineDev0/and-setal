from django.urls import path, include
from .views import  DemarrerInterventionView, TerminerInterventionView, AnnulerInterventionView


urlpatterns = [
    path('demarrer/<int:id_incident>/', DemarrerInterventionView.as_view(), name='demarrer-intervention'),
    path('terminer/<int:id_intervention>/', TerminerInterventionView.as_view(), name='terminer-intervention'),
    path('annuler/<int:id_intervention>/', AnnulerInterventionView.as_view(), name='annuler-intervention'),
]