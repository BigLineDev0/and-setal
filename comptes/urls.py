from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UtisateursViewset, InscriptionView, VerificationOTPViewSet, RenvoiOTPViewSet

router = DefaultRouter()

router.register(r'utilisateur', UtisateursViewset)
router.register(r"verification-otp", VerificationOTPViewSet, basename="verification-otp")
router.register(r"renvoi-otp", RenvoiOTPViewSet, basename="renvoi-otp")


urlpatterns = [
    path('inscription/', InscriptionView.as_view(), name='inscription')
] + router.urls
