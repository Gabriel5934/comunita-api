from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

from api.views import EmailTokenObtainPairView, RegisterView, health

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health, name="health"),
    path("register", RegisterView.as_view(), name="register"),
    path("token", EmailTokenObtainPairView.as_view(), name="token"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include("api.urls")),
]
