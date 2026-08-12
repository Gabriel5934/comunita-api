from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

from comunita.views import EmailTokenObtainPairView, RegisterView, health

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health, name="health"),
    path("register", RegisterView.as_view(), name="register"),
    path("register/", RegisterView.as_view(), name="register_slash"),
    path("token", EmailTokenObtainPairView.as_view(), name="token"),
    path("token/", EmailTokenObtainPairView.as_view(), name="token_slash"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh_slash"),
    path("api/auth/register/", RegisterView.as_view(), name="api_register"),
    path("api/auth/token/", EmailTokenObtainPairView.as_view(), name="api_token"),
    path(
        "api/auth/token/refresh/", TokenRefreshView.as_view(), name="api_token_refresh"
    ),
    path("api/", include("comunita.urls")),
]
