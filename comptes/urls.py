from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UtisateursViewset, InscriptionView, VerificationOTPViewSet

router = DefaultRouter()

router.register(r'Utilsateur', UtisateursViewset)
router.register(r"verification-otp", VerificationOTPViewSet, basename="verification-otp")


urlpatterns = [
    path('inscription', InscriptionView.as_view(), name='inscription')
] + router.urls
