from django.shortcuts import render
from rest_framework import viewsets
from .models import Utilisateurs
from .serializers import UtilisateurSerializers, VerificationOTPSerializer
from rest_framework import generics, status
from .serializers import InscriptionSerializer
from .services import generer_et_envoyer_otp
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Otp
from drf_spectacular.utils import extend_schema


# Create your views here.

class UtisateursViewset(viewsets.ModelViewSet):
    queryset = Utilisateurs.objects.all()
    serializer_class = UtilisateurSerializers


class InscriptionView(generics.CreateAPIView):
    queryset = Utilisateurs.objects.all()
    serializer_class = InscriptionSerializer

    permission_classes = [AllowAny]


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Compte créé mais inactif tant que l'OTP n'est pas validé
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


            telephone = serializer.validated_data["telephone"]
            code = serializer.validated_data["code"]

            try:
                  utilisateur = Utilisateurs.objects.get(
                       telephone=telephone
                  )
            except Utilisateurs.DoesNotExist:
                 return Response (
                      {"message": "Utilisateur introuvable."},
                      status=status.HTTP_404_NOT_FOUND
                 )
            try:
                otp = Otp.objects.filter(
                     utilisateur=utilisateur,
                     code=code,
                     est_utilise= False
                ).latest("date_creation")
            except Otp.DoesNotExist:
                 return Response(
                      { "message": "Code OTP incorrect ou expiré."},
                      status=status.HTTP_400_BAD_REQUEST
                 )

            # OTP VALIDE
            otp.est_utilise = True
            otp.save()

            # Activation du compte
            utilisateur.is_active = True
            utilisateur.save()

            return Response(
                 {"message": "Compte vérifié avec succès."},
                 status=status.HTTP_200_OK
            )
            

            