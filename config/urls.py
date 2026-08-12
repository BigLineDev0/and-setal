from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (SpectacularAPIView, SpectacularSwaggerView)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from comptes.views import UtisateursViewset, InscriptionView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/comptes', include('comptes.urls')),
    path('api/inscriptions/', InscriptionView.as_view(), name='inscription'),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view( url_name="schema"),name="swagger-ui"),
    path('api-auth/', include('rest_framework.urls')), # login/logout DRF
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
