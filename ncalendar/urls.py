from django.urls import path
from .views import calendar_page

urlpatterns = [
    path("", calendar_page, name="calendar"),
]
