from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import slugify

class Building(models.Model):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="buildings_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="buildings_updated",
    )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="BuildingMembership",
        related_name="buildings",
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "building"
            slug = base
            suffix = 2
            while Building.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base}-{suffix}"
                suffix += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BuildingMembership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("user", "building"), name="unique_building_member")
        ]


class Address(models.Model):
    cep_validator = RegexValidator(r"^\d{8}$", "CEP must contain exactly 8 digits")

    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="addresses")
    cep = models.CharField(max_length=8, validators=[cep_validator], db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("building", "cep"), name="unique_building_cep")
        ]


class Form(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="forms")
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    schema = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="forms_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="forms_updated",
    )

    class Meta:
        ordering = ("-created_at",)


class FormSubmission(models.Model):
    form = models.ForeignKey(Form, on_delete=models.PROTECT, related_name="submissions")
    data = models.JSONField(default=dict)
    field_ids = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
