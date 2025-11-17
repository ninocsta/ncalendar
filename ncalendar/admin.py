from django.contrib import admin
from .models import Professional, Client, Service, Event

admin.site.register(Professional)
admin.site.register(Client)
admin.site.register(Service)
admin.site.register(Event)