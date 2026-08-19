from django.contrib import admin
from .models import Notification

@admin.register(Notification)

class NotificationAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "utilisateur",
        "titre",
        "message",
        "lu",
        "date_fin",
        "date_creation",
    ] 

    list_filter = [
        "id",
        "date_creation"
    ]

    search_fields = [
        "titre",
        "message",
        "utilisateur__username"
    ]
