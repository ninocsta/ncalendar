from rest_framework import serializers
from ..models import Professional, Client, Service, Event
from datetime import timedelta


class ProfessionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    # duração em minutos (int) para o frontend
    duration_minutes = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ['id', 'name', 'duration', 'value', 'duration_minutes']

    def get_duration_minutes(self, obj):
        # espera obj.duration ser timedelta
        if not obj.duration:
            return 0
        return int(obj.duration.total_seconds() // 60)


class EventSerializer(serializers.ModelSerializer):
    professional_name = serializers.CharField(source='professional.name', read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'start', 'end', 'professional', 'professional_name',
            'client', 'client_name', 'service', 'service_name',
            'description', 'status', 'duration', 'value',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['end', 'created_at', 'updated_at']
        extra_kwargs = {
            'description': {'required': False, 'allow_blank': True},
        }

    def to_internal_value(self, data):
        """
        Allow the frontend to send `duration` as HH:MM:SS string (e.g. "01:30:00")
        or to omit it (we'll fill from service). Convert to timedelta here so
        validation works with a proper type.
        """
        internal = super().to_internal_value(data)
        dur = data.get('duration') or data.get('duration_minutes')
        # if duration provided as HH:MM:SS
        if isinstance(dur, str) and dur.count(':') == 2:
            h, m, s = map(int, dur.split(':'))
            internal['duration'] = timedelta(hours=h, minutes=m, seconds=s)
        elif 'duration_minutes' in data and data['duration_minutes'] not in (None, ''):
            try:
                mins = int(data['duration_minutes'])
                internal['duration'] = timedelta(minutes=mins)
            except Exception:
                pass
        return internal

    def validate(self, attrs):
        """
        Simplified validation:
        - professional, client, service, start must be present
        - duration/value: if missing, try to fill from service
        - compute end as start + duration
        """
        errors = {}

        professional = attrs.get('professional') or getattr(self.instance, 'professional', None)
        client = attrs.get('client') or getattr(self.instance, 'client', None)
        service = attrs.get('service') or getattr(self.instance, 'service', None)
        start = attrs.get('start') or getattr(self.instance, 'start', None)
        duration = attrs.get('duration') or getattr(self.instance, 'duration', None)
        value = attrs.get('value') or getattr(self.instance, 'value', None)

        if service and not duration:
            # if service has duration (timedelta), use it
            if getattr(service, 'duration', None):
                duration = service.duration
                attrs['duration'] = duration
        if service and (value in (None, '')):  # fill from service if available
            if getattr(service, 'value', None) is not None:
                attrs['value'] = service.value
                value = attrs['value']

        if not professional:
            errors['professional'] = 'Professional is required.'
        if not client:
            errors['client'] = 'Client is required.'
        if not service:
            errors['service'] = 'Service is required.'
        if not start:
            errors['start'] = 'Start is required.'
        if not duration:
            errors['duration'] = 'Duration is required.'
        if value in (None, ''):
            errors['value'] = 'Value is required.'

        if errors:
            raise serializers.ValidationError(errors)

        # compute end
        if start and duration:
            attrs['end'] = start + duration

        return attrs


class ProfessionalResourceSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='name')

    class Meta:
        model = Professional
        fields = ['id', 'title']


class EventCalendarSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    resourceId = serializers.IntegerField(source='professional_id')

    class Meta:
        model = Event
        fields = ['id', 'title', 'start', 'end', 'resourceId']

    def get_title(self, obj):
        service = obj.service.name if obj.service else ""
        client = obj.client.name if obj.client else ""
        return f"{service} - {client}"
