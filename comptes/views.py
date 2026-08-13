from django.shortcuts import render
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Utilisateurs, Otp
from .serializers import (
    UtilisateurSerializers,
    VerificationOTPSerializer,
    InscriptionSerializer,
    RenvoiOTPSerializer
)
from .services import generer_et_envoyer_otp

from drf_spectacular.utils import extend_schema


class UtisateursViewset(viewsets.ModelViewSet):
    """CRUD sur les utilisateurs — visibilité restreinte selon le rôle."""
    queryset = Utilisateurs.objects.all()
    serializer_class = UtilisateurSerializers
    permission_classes = [IsAuthenticated]  # nécessite un token JWT valide

    def get_queryset(self):
        # Un admin voit tout le monde, un utilisateur normal ne voit que son propre profil
        if self.request.user.role == 'admin':
            return Utilisateurs.objects.all()

        return Utilisateurs.objects.filter(pk=self.request.user.pk)


class InscriptionView(generics.CreateAPIView):
    """Crée un compte inactif et déclenche l'envoi d'un OTP de vérification."""
    queryset = Utilisateurs.objects.all()
    serializer_class = InscriptionSerializer
    permission_classes = [AllowAny]  # accessible sans authentification

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # is_active=False : le compte reste bloqué tant que l'OTP n'est pas validé
        utilisateur = serializer.save(is_active=False)

        generer_et_envoyer_otp(utilisateur)

        return Response(
            {"message": "Compte créé. Un code de vérification a été envoyé."},
            status=status.HTTP_201_CREATED
        )


class VerificationOTPViewSet(viewsets.ViewSet):
    """Valide un code OTP et active le compte correspondant si tout est correct."""
    permission_classes = [AllowAny]

    @extend_schema(
        request=VerificationOTPSerializer,
        responses={200: dict}
    )
    def create(self, request, *args, **kwargs):

        serializer = VerificationOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        telephone = serializer.validated_data["telephone"]
        code = serializer.validated_data["code"]

        # 1. L'utilisateur existe-t-il ?
        try:
            utilisateur = Utilisateurs.objects.get(telephone=telephone)
        except Utilisateurs.DoesNotExist:
            return Response(
                {"message": "Utilisateur introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. Récupère le dernier OTP encore actif (non utilisé) pour cet utilisateur
        try:
            otp = Otp.objects.filter(
                utilisateur=utilisateur,
                est_utilise=False
            ).latest("date_creation")
        except Otp.DoesNotExist:
            return Response(
                {"message": "Code OTP incorrect ou expiré."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Le code a-t-il expiré (5 min) ?
        if otp.est_expire():
            otp.est_utilise = True  # on le neutralise pour qu'il ne soit plus réutilisable
            otp.save()
            return Response(
                {"message": "Code expiré. Veuillez en redemander un."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4. Protection anti brute-force : max 3 tentatives par code
        MAX_TENTATIVES = 3

        if otp.tentative >= MAX_TENTATIVES:
            otp.est_utilise = True
            otp.save()
            return Response(
                {"message": "Trop de tentatives. Redemandez un nouveau code."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 5. Le code saisi est-il correct ?
        if otp.code != code:
            otp.tentative += 1  # incrémente le compteur d'essais ratés

            if otp.tentative >= MAX_TENTATIVES:
                otp.est_utilise = True
                otp.save()
                return Response(
                    {"message": "Trop de tentatives. Redemandez un nouveau code."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            otp.save()
            return Response(
                {"message": "Code OTP incorrect."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 6. Code valide : on consomme l'OTP et on active le compte
        otp.est_utilise = True
        otp.save()

        utilisateur.is_active = True
        utilisateur.save()

        return Response(
            {"message": "Compte vérifié avec succès."},
            status=status.HTTP_200_OK
        )


class RenvoiOTPViewSet(viewsets.ViewSet):
    """Génère et envoie un nouveau code OTP si le compte n'est pas encore vérifié."""
    permission_classes = [AllowAny]

    @extend_schema(
        request=RenvoiOTPSerializer,
        responses={200: dict}
    )
    def create(self, request, *args, **kwargs):
        serializer = RenvoiOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        telephone = serializer.validated_data['telephone']

        try:
            utilisateur = Utilisateurs.objects.get(telephone=telephone)
        except Utilisateurs.DoesNotExist:
            return Response(
                {"message": "Utilisateur introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Inutile de renvoyer un OTP si le compte est déjà vérifié
        if utilisateur.is_active:
            return Response(
                {"message": "Ce compte est déjà vérifié."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Invalide tous les anciens codes non utilisés pour éviter d'avoir plusieurs codes valides en même temps
        Otp.objects.filter(utilisateur=utilisateur, est_utilise=False).update(est_utilise=True)

        generer_et_envoyer_otp(utilisateur)

        return Response(
            {"message": "Un nouveau code de vérification a été envoyé."},
            status=status.HTTP_200_OK
        )