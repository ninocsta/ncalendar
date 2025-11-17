# ncalendar/api/views.py
from rest_framework import viewsets
from ..models import Professional, Client, Service, Event
from .serializers import (
    ProfessionalSerializer,
    ProfessionalResourceSerializer,
    ClientSerializer,
    ServiceSerializer,
    EventSerializer,
    EventCalendarSerializer,
)


class ProfessionalViewSet(viewsets.ReadOnlyModelViewSet):
    """Return professionals formatted for FullCalendar resources (id, title).
    This is ReadOnly since resources are usually managed separately in admin.
    """
    queryset = Professional.objects.all()
    serializer_class = ProfessionalResourceSerializer


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    
    def get_queryset(self):
        """Allow filtering clients by `q` query param (simple name search).
        Used by the frontend autocomplete to avoid returning all clients.
        """
        qs = super().get_queryset()
        q = self.request.query_params.get('q') or self.request.query_params.get('search')
        if q:
            return qs.filter(name__icontains=q)[:50]
        # quando não há query, retornar um subconjunto razoável (ex.: últimos 20)
        return qs.order_by('-id')[:20]


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.select_related('service', 'client', 'professional').all()
    serializer_class = EventSerializer

    def get_serializer_class(self):
        # For listing (FullCalendar) use the compact calendar serializer
        if self.action in ['list', 'retrieve']:
            return EventCalendarSerializer
        return EventSerializer

    # Filtrar por período para o FullCalendar
    def get_queryset(self):
        qs = super().get_queryset()

        start = self.request.query_params.get("start")
        end = self.request.query_params.get("end")

        if start and end:
            # filter events that start inside the requested window
            qs = qs.filter(start__gte=start, start__lt=end)

        return qs
