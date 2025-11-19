# ncalendar/admin.py
from django.contrib import admin
from .models import Professional, Client, Service, Event


@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'active', 'has_user_account', 'created_at']
    list_filter = ['company', 'active']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'professional', 'company', 'value', 'duration', 'active']
    list_filter = ['company', 'professional', 'active']
    search_fields = ['name', 'professional__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['client', 'service', 'professional', 'start', 'status', 'created_by']
    list_filter = ['status', 'professional', 'created_at']
    search_fields = ['client__name', 'service__name']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    
    def save_model(self, request, obj, form, change):
        if not change:  # Criando novo
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)