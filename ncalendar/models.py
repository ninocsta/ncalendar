from django.db import models
from datetime import timedelta


class Professional(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Client(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=100)
    duration = models.DurationField(default=timedelta(minutes=0))
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name


class Event(models.Model):
    STATUS_CHOICES = [
        (1, 'Scheduled'),
        (2, 'Completed'),
        (3, 'Cancelled'),
        (4, 'No Show'),
        (5, 'Rescheduled'),
        (6, 'In Progress'),
        (7, 'Pending Payment'),
    ]

    start = models.DateTimeField()
    end = models.DateTimeField()

    professional = models.ForeignKey(
        Professional,
        on_delete=models.CASCADE,
        related_name='events'
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='events'
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name='events'
    )

    description = models.TextField(blank=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    duration = models.DurationField(default=timedelta(minutes=0))
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.client} - {self.start}'
