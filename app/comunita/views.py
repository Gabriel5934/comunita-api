from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Building, Form
from .serializers import (
    BuildingSerializer,
    EmailTokenObtainPairSerializer,
    FormSerializer,
    FormSubmissionSerializer,
    PublicFormSerializer,
    RegisterSerializer,
)


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"})


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
    permission_classes = [AllowAny]


class BuildingViewSet(viewsets.ModelViewSet):
    serializer_class = BuildingSerializer

    def get_queryset(self):
        return Building.objects.filter(users=self.request.user).prefetch_related("addresses")


class FormViewSet(viewsets.ModelViewSet):
    serializer_class = FormSerializer

    def get_queryset(self):
        return Form.objects.filter(building__users=self.request.user).select_related("building")


class PublicBuildingFormView(generics.RetrieveAPIView):
    serializer_class = PublicFormSerializer
    permission_classes = [AllowAny]
    lookup_url_kwarg = "slug"

    def get_object(self):
        return get_object_or_404(
            Form.objects.select_related("building"),
            building__slug=self.kwargs["slug"],
        )


class FormSubmissionCreateView(generics.CreateAPIView):
    serializer_class = FormSubmissionSerializer
    permission_classes = [AllowAny]
