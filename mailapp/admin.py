from django.contrib import admin
from .models import Email

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ("subject", "sender", "recipients", "is_read", "timestamp")
    search_fields = ("subject", "sender", "recipients", "body")
