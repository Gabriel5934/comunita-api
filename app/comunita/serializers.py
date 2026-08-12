import re
import uuid

from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Address, Building, BuildingMembership, Form, FormSubmission

User = get_user_model()
FIELD_TYPES = {"name", "street", "rg", "cpf"}


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "email", "password")

    def validate_email(self, email):
        email = User.objects.normalize_email(email)
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("A user with this email already exists")
        return email

    def create(self, validated_data):
        email = validated_data["email"]
        return User.objects.create_user(
            username=email,
            email=email,
            password=validated_data["password"],
        )


class EmailTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user_record = User.objects.filter(email__iexact=attrs["email"]).first()
        user = authenticate(
            request=self.context.get("request"),
            username=user_record.username if user_record else attrs["email"],
            password=attrs["password"],
        )
        if not user or not user.is_active:
            raise AuthenticationFailed("No active account found with the given credentials")
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {"id": user.id, "email": user.email},
        }


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ("id", "cep")


class BuildingSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, required=False)

    class Meta:
        model = Building
        fields = ("id", "name", "slug", "addresses", "created_at", "updated_at")
        read_only_fields = ("slug", "created_at", "updated_at")

    def create(self, validated_data):
        addresses = validated_data.pop("addresses", [])
        user = self.context["request"].user
        building = Building.objects.create(created_by=user, updated_by=user, **validated_data)
        BuildingMembership.objects.create(user=user, building=building)
        Address.objects.bulk_create([Address(building=building, **item) for item in addresses])
        return building

    def update(self, instance, validated_data):
        addresses = validated_data.pop("addresses", None)
        instance.updated_by = self.context["request"].user
        instance = super().update(instance, validated_data)
        if addresses is not None:
            instance.addresses.all().delete()
            Address.objects.bulk_create([Address(building=instance, **item) for item in addresses])
        return instance


class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = (
            "id", "building", "name", "description", "schema",
            "created_at", "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")

    def validate_building(self, building):
        if not building.users.filter(pk=self.context["request"].user.pk).exists():
            raise serializers.ValidationError("You do not have access to this building")
        return building

    def validate_schema(self, schema):
        if not isinstance(schema, list):
            raise serializers.ValidationError("Schema must be a list of fields")
        normalized = []
        seen_ids = set()
        for field in schema:
            if not isinstance(field, dict):
                raise serializers.ValidationError("Each field must be an object")
            field_id = str(field.get("id") or uuid.uuid4())
            label = str(field.get("label", "")).strip()
            field_type = field.get("type")
            validation = field.get("validation", {})
            if not label or field_type not in FIELD_TYPES or field_id in seen_ids:
                raise serializers.ValidationError("Fields require a unique id, label, and valid type")
            seen_ids.add(field_id)
            normalized.append({
                "id": field_id,
                "label": label,
                "type": field_type,
                "validation": {"required": bool(validation.get("required", False))},
            })
        return normalized

    def create(self, validated_data):
        user = self.context["request"].user
        return Form.objects.create(created_by=user, updated_by=user, **validated_data)

    def update(self, instance, validated_data):
        instance.updated_by = self.context["request"].user
        return super().update(instance, validated_data)


class PublicFormSerializer(serializers.ModelSerializer):
    building = serializers.CharField(source="building.name")
    building_slug = serializers.CharField(source="building.slug")

    class Meta:
        model = Form
        fields = ("id", "building", "building_slug", "name", "description", "schema")


class FormSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormSubmission
        fields = ("id", "form", "data", "field_ids", "created_at")
        read_only_fields = ("id", "field_ids", "created_at")

    def validate(self, attrs):
        form = attrs["form"]
        data = attrs["data"]
        if not isinstance(data, dict):
            raise serializers.ValidationError({"data": "Submission data must be an object"})
        errors = {}
        allowed_ids = set()
        schema_ids = []
        for field in form.schema:
            field_id = str(field["id"])
            allowed_ids.add(field_id)
            schema_ids.append(field_id)
            value = str(data.get(field_id, "")).strip()
            if field["validation"]["required"] and not value:
                errors[field_id] = "This field is required"
            if value and field["type"] == "name" and not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ]+", value):
                errors[field_id] = "Use one word containing letters only"
            if value and field["type"] == "rg" and not re.fullmatch(r"[A-Za-z0-9]+", value):
                errors[field_id] = "Use letters and numbers only"
            if value and field["type"] == "cpf" and not re.fullmatch(r"\d{3}\.\d{3}\.\d{3}-\d{2}", value):
                errors[field_id] = "Use the format 000.000.000-00"
        unknown = set(data) - allowed_ids
        if unknown:
            errors["data"] = "Submission contains unknown field ids"
        if errors:
            raise serializers.ValidationError(errors)
        attrs["field_ids"] = schema_ids
        return attrs
