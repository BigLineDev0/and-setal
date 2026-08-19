from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet permettant de gérer les notifications d'un utilisateur.

    Cette classe fournit automatiquement les opérations CRUD :
    - GET : récupérer les notifications
    - POST : créer une notification
    - GET /<id>/ : récupérer une notification précise
    - PUT/PATCH : modifier une notification
    - DELETE : supprimer une notification

    Les notifications sont limitées à l'utilisateur actuellement connecté.
    """

    # Serializer utilisé pour transformer les objets Notification
    # en données JSON et inversement.
    serializer_class = NotificationSerializer

    # Seuls les utilisateurs authentifiés peuvent accéder
    # aux endpoints de cette classe.
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retourne uniquement les notifications de l'utilisateur connecté.

        Les notifications sont triées de la plus récente
        à la plus ancienne grâce à '-date_creation'.
        """

        return Notification.objects.filter(
            utilisateur=self.request.user
        ).order_by('-date_creation')

    def perform_create(self, serializer):
        """
        Crée une nouvelle notification.

        L'utilisateur connecté est automatiquement associé
        à la notification.

        Cela évite de laisser le client envoyer lui-même
        l'identifiant de l'utilisateur.
        """

        serializer.save(
            utilisateur=self.request.user
        )

    @action(
        detail=True,
        methods=['patch'],
        url_path='lire'
    )
    def marquer_comme_lue(self, request, pk=None):
        """
        Marque une notification spécifique comme lue.

        Endpoint :
        PATCH /api/notifications/<id>/lire/

        La notification récupérée est celle appartenant
        à l'utilisateur connecté grâce à get_object().
        """

        # Récupère la notification correspondant à l'identifiant
        # présent dans l'URL.
        notification = self.get_object()

        # Modifie l'état de la notification.
        notification.lu = True

        # Sauvegarde uniquement le champ 'lu' en base de données.
        notification.save(update_fields=['lu'])

        # Retourne une réponse HTTP 200 avec un message de confirmation.
        return Response(
            {
                'message': 'Notification marquée comme lue.'
            },
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='non-lues'
    )
    def non_lues(self, request):
        """
        Retourne uniquement les notifications non lues
        de l'utilisateur connecté.

        Endpoint :
        GET /api/notifications/non-lues/
        """

        # Récupère les notifications de l'utilisateur connecté
        # puis conserve uniquement celles qui ne sont pas lues.
        notifications = self.get_queryset().filter(
            lu=False
        )

        # Transforme les objets Django en données JSON.
        # many=True indique qu'il y a plusieurs notifications.
        serializer = self.get_serializer(
            notifications,
            many=True
        )

        # Retourne la liste des notifications au format JSON.
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['patch'],
        url_path='lire-tout'
    )
    def marquer_tout_comme_lu(self, request):
        """
        Marque toutes les notifications non lues
        de l'utilisateur connecté comme lues.

        Endpoint :
        PATCH /api/notifications/lire-tout/
        """

        # Récupère les notifications non lues de l'utilisateur
        # connecté et les marque toutes comme lues.
        self.get_queryset().filter(
            lu=False
        ).update(lu=True)

        # Retourne une confirmation après la mise à jour.
        return Response(
            {
                'message': 'Toutes les notifications ont été marquées comme lues.'
            },
            status=status.HTTP_200_OK
        )