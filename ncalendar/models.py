# ncalendar/models.py
from django.db import models
from django.utils import timezone
from django.conf import settings
from datetime import timedelta


class Professional(models.Model):
    company = models.ForeignKey('accounts.Company', on_delete=models.CASCADE, related_name='professionals')
    name = models.CharField("Nome", max_length=100)
    active = models.BooleanField("Ativo", default=True)
    
    # Campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profissional"
        ordering = ['name']
        unique_together = (('company', 'name'),)

    def __str__(self):
        return self.name
    
    @property
    def has_user_account(self):
        """Verifica se o profissional tem usuário vinculado"""
        return hasattr(self, 'user_account') and self.user_account is not None


class Client(models.Model):
    company = models.ForeignKey('accounts.Company', on_delete=models.CASCADE, related_name='clients')
    name = models.CharField("Nome", max_length=100)
    phone = models.CharField("Telefone", max_length=20, unique=True, null=True, blank=True)
    
    # Campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = (('company', 'name'),)

    def __str__(self):
        return f'{self.name} ({self.phone})'


class Service(models.Model):
    """Serviços vinculados a profissionais específicos"""
    company = models.ForeignKey('accounts.Company', on_delete=models.CASCADE, related_name='services')
    professional = models.ForeignKey(
        Professional, 
        on_delete=models.CASCADE, 
        related_name='services',
        verbose_name="Profissional"
    )
    name = models.CharField("Serviço", max_length=100)
    duration = models.DurationField("Duração padrão", default=timedelta(minutes=60))
    value = models.DecimalField("Valor padrão", max_digits=10, decimal_places=2, default=0.00)
    active = models.BooleanField(default=True)
    
    # Campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Serviço"
        verbose_name_plural = "Serviços"
        ordering = ['professional', 'name']
        unique_together = (('company', 'professional', 'name'),)

    def __str__(self):
        return f"{self.name} - {self.professional.name}"

    @property
    def duration_minutes(self):
        return int(self.duration.total_seconds() // 60)


class Event(models.Model):
    STATUS_CHOICES = [
        (1, "Agendado"),
        (2, "Concluído"),
        (3, "Cancelado"),
        (4, "Não compareceu"),
        (6, "Em andamento"),
        (7, "Pendente pagamento"),
    ]

    STATUS_COLORS = {
        1: "#3788d8",
        2: "#28a745",
        3: "#dc3545",
        4: "#fd7e14",
        6: "#17a2b8",
        7: "#6f42c1",
    }

    start = models.DateTimeField("Início")
    end = models.DateTimeField("Fim", editable=False)

    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, verbose_name="Profissional")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Cliente")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, verbose_name="Serviço")

    description = models.TextField("Observações", blank=True, null=True)
    status = models.PositiveSmallIntegerField("Status", choices=STATUS_CHOICES, default=1)

    duration = models.DurationField("Duração real", default=timedelta(minutes=60))
    value = models.DecimalField("Valor cobrado", max_digits=10, decimal_places=2, default=0.00)

    # Campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='events_created',
        verbose_name="Criado por"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='events_updated',
        verbose_name="Atualizado por"
    )

    class Meta:
        verbose_name = "Agendamento"
        ordering = ['-start']
        indexes = [
            models.Index(fields=['start', 'professional']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.client} - {self.service} ({self.get_status_display()})"

    def clean(self):
        """Valida se o serviço pertence ao profissional"""
        from django.core.exceptions import ValidationError
        if self.service and self.professional:
            if self.service.professional != self.professional:
                raise ValidationError({
                    'service': f'O serviço "{self.service.name}" não pertence ao profissional "{self.professional.name}"'
                })

    def save(self, *args, **kwargs):
        # Validação
        self.full_clean()
        
        # Sempre recalcula o end com base na duração atual
        try:
            self.end = self.start + self.duration
        except Exception:
            pass

        # Corrige timezone
        if timezone.is_naive(self.start):
            self.start = timezone.make_aware(self.start)
        if self.end and timezone.is_naive(self.end):
            self.end = timezone.make_aware(self.end)

        super().save(*args, **kwargs)

    @property
    def background_color(self):
        return self.STATUS_COLORS.get(self.status, "#3788d8")

    @property
    def text_color(self):
        dark = {3, 6, 7}
        return "#ffffff" if self.status in dark else "#000000"