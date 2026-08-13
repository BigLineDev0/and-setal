from django.urls import path
from .views import IncidentDetailView, IncidentListCreateView

urlpatterns = [
    path('', IncidentListCreateView.as_view(), name='incident-list-create'),
    path('<int:pk>/', IncidentDetailView.as_view(), name='incident-detail'),
]