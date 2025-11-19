# ncalendar/api/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError
from ..models import Professional, Client, Service, Event
from .serializers import (
    ProfessionalResourceSerializer, ClientSerializer,
    ServiceSerializer, EventSerializer, EventCalendarSerializer
)


class CompanyFilteredViewSet(viewsets.ModelViewSet):
    """ViewSet base que filtra automaticamente por company"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.company)
    
    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)


class ProfessionalViewSet(CompanyFilteredViewSet):
    queryset = Professional.objects.filter(active=True)
    serializer_class = ProfessionalResourceSerializer


class ClientViewSet(CompanyFilteredViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get('q')
        if q:
            qs = qs.filter(name__icontains=q)[:50]
        return qs


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """Serviços filtrados por company e opcionalmente por profissional"""
    permission_classes = [IsAuthenticated]
    queryset = Service.objects.filter(active=True)
    serializer_class = ServiceSerializer
    
    def get_queryset(self):
        qs = super().get_queryset().filter(company=self.request.user.company)
        
        # Filtrar por profissional se especificado
        professional_id = self.request.query_params.get('professional')
        if professional_id:
            qs = qs.filter(professional_id=professional_id)
        
        return qs


class EventViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        qs = Event.objects.filter(
            professional__company=self.request.user.company
        ).select_related('client', 'service', 'professional', 'created_by', 'updated_by')
        
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')
        if start and end:
            qs = qs.filter(end__gt=start, start__lt=end)
        return qs
    
    def get_serializer_class(self):
        return EventCalendarSerializer if self.action == 'list' else EventSerializer
    
    def perform_create(self, serializer):
        """Adiciona created_by automaticamente ao criar"""
        try:
            serializer.save(created_by=self.request.user, updated_by=self.request.user)
        except DjangoValidationError as e:
            # Converte ValidationError do Django para DRF
            raise ValidationError(e.message_dict if hasattr(e, 'message_dict') else {'detail': str(e)})
    
    def perform_update(self, serializer):
        """Adiciona updated_by automaticamente ao atualizar"""
        try:
            serializer.save(updated_by=self.request.user)
        except DjangoValidationError as e:
            # Converte ValidationError do Django para DRF
            raise ValidationError(e.message_dict if hasattr(e, 'message_dict') else {'detail': str(e)})
    
    @action(detail=False, methods=['get'])
    def status_choices(self, request):
        return Response([
            {'value': status[0], 'label': status[1]} 
            for status in Event.STATUS_CHOICES
        ])
