from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UtisateursViewset, InscriptionView, VerificationOTPViewSet, RenvoiOTPViewSet, ChangerRoleView, CreationAgentView, MonProfilView

router = DefaultRouter()

# ============================================================
# ROUTES GÉRÉES PAR LE ROUTER DRF
# ============================================================

# liste des utilisateurs et GET /utilisateur/{id}/ détail d'un utilisateur
router.register(r'utilisateur', UtisateursViewset)
# Vérification du compte avec un code OTP
router.register(r"verification-otp", VerificationOTPViewSet, basename="verification-otp")
# Renvoi d'un nouveau code OTP
# Permet à un utilisateur qui n'a pas reçu son OTP
# ou dont le code a expiré de demander un nouveau code.
router.register(r"renvoi-otp", RenvoiOTPViewSet, basename="renvoi-otp")


# ============================================================
# ENDPOINTS PERSONNALISÉS
# ============================================================
urlpatterns = [
    # PROFIL DE L'UTILISATEUR CONNECTÉ
    path('me/', MonProfilView.as_view(), name='mon-profil'),
    # Permet de créer un nouveau compte utilisateur.
    path('inscription/', InscriptionView.as_view(), name='inscription'),
    # Permet de modifier le rôle d'un utilisateur.
    path('utilisateur/<int:pk>/role/', ChangerRoleView.as_view(), name='changer-role'),
    # Admin crée un compte avec le rôle "agent".
    path("agents/", CreationAgentView.as_view(), name="creation-agent"),
] + router.urls
