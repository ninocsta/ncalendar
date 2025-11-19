# ncalendar/api/urls.py
from rest_framework.routers import DefaultRouter
from .views import ProfessionalViewSet, ClientViewSet, ServiceViewSet, EventViewSet

router = DefaultRouter()
router.register('professionals', ProfessionalViewSet, basename='professional')
router.register('clients', ClientViewSet)
router.register('services', ServiceViewSet)
router.register('events', EventViewSet, basename='event')

urlpatterns = router.urls