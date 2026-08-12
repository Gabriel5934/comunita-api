from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BuildingViewSet,
    FormSubmissionCreateView,
    FormViewSet,
    PublicBuildingFormView,
    health,
)

router = DefaultRouter()
router.register("buildings", BuildingViewSet, basename="building")
router.register("forms", FormViewSet, basename="form")

urlpatterns = [
    path("", include(router.urls)),
    path("public/buildings/<slug:slug>/form/", PublicBuildingFormView.as_view()),
    path("public/submissions/", FormSubmissionCreateView.as_view()),
    path("health/", health, name="health"),
]
