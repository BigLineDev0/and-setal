from django.urls import path
from .views import IncidentAdminListView, IncidentDetailView, IncidentListCreateView

urlpatterns = [
    path('', IncidentListCreateView.as_view(), name='incident-list-create'),
    path('<int:pk>/', IncidentDetailView.as_view(), name='incident-detail'),
    path('tous/', IncidentAdminListView.as_view(), name='incident-admin-list'),
]