# ncalendar/api/serializers.py
from rest_framework import serializers
from ..models import Professional, Client, Service, Event


class ProfessionalResourceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk')
    title = serializers.CharField(source='name')
    has_user_account = serializers.BooleanField(read_only=True)

    class Meta:
        model = Professional
        fields = ['id', 'title', 'has_user_account']


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'name', 'phone']


class ServiceSerializer(serializers.ModelSerializer):
    duration_minutes = serializers.SerializerMethodField()
    professional_name = serializers.CharField(source='professional.name', read_only=True)

    class Meta:
        model = Service
        fields = ['id', 'name', 'duration_minutes', 'value', 'professional', 'professional_name']

    def get_duration_minutes(self, obj):
        try:
            return int(obj.duration.total_seconds() // 60)
        except Exception:
            return 0


class EventCalendarSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    resourceId = serializers.IntegerField(source='professional.id')
    clientPhone = serializers.SerializerMethodField()
    client = ClientSerializer(read_only=True)
    backgroundColor = serializers.SerializerMethodField()
    borderColor = serializers.SerializerMethodField()
    textColor = serializers.SerializerMethodField()
    status = serializers.IntegerField()
    statusDisplay = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'start', 'end', 'resourceId',
                  'backgroundColor', 'borderColor', 'textColor', 
                  'clientPhone', 'client', 'status', 'statusDisplay']

    def get_title(self, obj):
        return f"{obj.service.name} - {obj.client.name}"

    def get_backgroundColor(self, obj):
        return obj.background_color

    def get_borderColor(self, obj):
        return obj.background_color

    def get_textColor(self, obj):
        return obj.text_color

    def get_clientPhone(self, obj):
        try:
            return obj.client.phone
        except Exception:
            return None


class EventSerializer(serializers.ModelSerializer):
    professional = serializers.PrimaryKeyRelatedField(queryset=Professional.objects.all())
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())

    duration_minutes = serializers.IntegerField(write_only=True, required=False)
    value = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    client_data = ClientSerializer(source='client', read_only=True)
    
    # Campos de auditoria são read-only, preenchidos automaticamente na view
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'start', 'professional', 'client', 'client_data',
            'service', 'description', 'status', 'status_display',
            'duration_minutes', 'value', 'created_at', 'updated_at',
            'created_by', 'updated_by', 'created_by_username', 'updated_by_username'
        ]
        read_only_fields = [
            'end', 'status_display', 'created_at', 'updated_at',
            'created_by', 'updated_by', 'created_by_username', 'updated_by_username'
        ]

    def validate(self, attrs):
        # Converte duração
        if 'duration_minutes' in attrs:
            from datetime import timedelta
            attrs['duration'] = timedelta(minutes=attrs.pop('duration_minutes'))

        return attrs

    # Mantemos apenas username; não precisamos de métodos auxiliares