from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
 
from .models import Utilisateurs, Otp
from .serializers import (
    UtilisateurSerializers,
    VerificationOTPSerializer,
    InscriptionSerializer,
    RenvoiOTPSerializer,
    ChangerRoleSerializer,
    CreationAgentSerializer
)
from .services import generer_et_envoyer_otp
from drf_spectacular.utils import extend_schema
import secrets
from django.core.mail import send_mail
from django.conf import settings


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
    permission_classes = [AllowAny]

    @extend_schema(
        request=VerificationOTPSerializer,
        responses={200: dict}
    )
    def create(self, request, *args, **kwargs):

        serializer = VerificationOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        # 1. L'utilisateur existe-t-il ?
        try:
            utilisateur = Utilisateurs.objects.get(email=email)
        except Utilisateurs.DoesNotExist:
            return Response(
                {"message": "Utilisateur introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. Récupère le dernier OTP encore actif
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

        # 3. Expiration
        if otp.est_expire():
            otp.est_utilise = True
            otp.save()
            return Response(
                {"message": "Code expiré. Veuillez en redemander un."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4. Anti brute-force
        MAX_TENTATIVES = 3

        if otp.tentative >= MAX_TENTATIVES:
            otp.est_utilise = True
            otp.save()
            return Response(
                {"message": "Trop de tentatives. Redemandez un nouveau code."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 5. Le code est-il correct ?
        if otp.code != code:
            otp.tentative += 1

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

        # 6. Code valide
        otp.est_utilise = True
        otp.save()

        utilisateur.is_active = True
        utilisateur.save()

        return Response(
            {"message": "Compte vérifié avec succès."},
            status=status.HTTP_200_OK
        )


class RenvoiOTPViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RenvoiOTPSerializer,
        responses={200: dict}
    )
    def create(self, request, *args, **kwargs):
        serializer = RenvoiOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            utilisateur = Utilisateurs.objects.get(email=email)
        except Utilisateurs.DoesNotExist:
            return Response(
                {"message": "Utilisateur introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        if utilisateur.is_active:
            return Response(
                {"message": "Ce compte est déjà vérifié."},
                status=status.HTTP_400_BAD_REQUEST
            )

        Otp.objects.filter(utilisateur=utilisateur, est_utilise=False).update(est_utilise=True)

        generer_et_envoyer_otp(utilisateur)

        return Response(
            {"message": "Un nouveau code de vérification a été envoyé."},
            status=status.HTTP_200_OK
        )


 
class EstAdmin(BasePermission):
    """
    Autorise uniquement les utilisateurs dont le rôle vaut 'admin'.
    Contrairement à Django is_staff/is_superuser, ici le rôle est un champ
    métier (Utilisateurs.role), donc on le vérifie directement.
    """
 
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.role == "admin"
        )
 
  
 
 
class ChangerRoleView(APIView):
    """
    PATCH /comptes/utilisateurs/{id}/role/
    Réservé aux admins. Permet de changer le rôle d'un AUTRE utilisateur
    (jamais du sien via cet endpoint, mais rien n'empêche techniquement
    un admin de changer son propre rôle ici si besoin).
    Body attendu : {"role": "agent"} (valeurs possibles : citoyen, agent, admin)
    """
    permission_classes = [EstAdmin]
 
    def patch(self, request, pk):
        utilisateur_cible = get_object_or_404(Utilisateurs, pk=pk)
 
        serializer = ChangerRoleSerializer(utilisateur_cible, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
 
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreationAgentView(generics.CreateAPIView):

    queryset = Utilisateurs.objects.all()
    serializer_class = CreationAgentSerializer
    permission_classes = [EstAdmin]

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Génération du mot de passe temporaire
        mot_de_passe_temporaire = secrets.token_urlsafe(8)

        # Création du compte
        utilisateur = serializer.save(
            role="agent",
            is_active=True
        )

        # IMPORTANT : on définit le mot de passe
        utilisateur.set_password(mot_de_passe_temporaire)
        utilisateur.save()

        # Envoi des identifiants par email
        send_mail(
            subject="Votre compte agent And Setal",

            message=(
                f"Bonjour {utilisateur.first_name},\n\n"
                f"Votre compte agent a été créé par un administrateur.\n\n"
                f"Email : {utilisateur.email}\n"
                f"Mot de passe temporaire : {mot_de_passe_temporaire}\n\n"
                f"Vous pouvez utiliser ces informations pour vous connecter.\n"
                f"Merci de changer votre mot de passe après votre première connexion."
            ),

            from_email=settings.DEFAULT_FROM_EMAIL,

            recipient_list=[
                utilisateur.email
            ],

            fail_silently=False,
        )

        return Response(
            {
                "message": "Compte agent créé avec succès."
            },
            status=status.HTTP_201_CREATED
        )