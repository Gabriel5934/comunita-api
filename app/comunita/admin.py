from django.contrib import admin

from .models import Address, Building, BuildingMembership, Form, FormSubmission


admin.site.register(Building)
admin.site.register(BuildingMembership)
admin.site.register(Address)
admin.site.register(Form)
admin.site.register(FormSubmission)
