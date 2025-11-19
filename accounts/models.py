# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class Company(models.Model):
    name = models.CharField("Nome da Empresa", max_length=200)
    slug = models.SlugField(unique=True)
    active = models.BooleanField("Ativa", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    timezone = models.CharField(max_length=50, default='America/Sao_Paulo')
    
    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class User(AbstractUser):
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name="Empresa"
    )
    phone = models.CharField("Telefone", max_length=20, blank=True)
    
    # Vínculo opcional com profissional
    professional = models.OneToOneField(
        'ncalendar.Professional',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_account',
        verbose_name="Profissional Vinculado"
    )
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
    
    def __str__(self):
        company_name = self.company.name if self.company else "(sem empresa)"
        return f"{self.get_full_name()} - {company_name}"
    
    @property
    def is_professional(self):
        """Verifica se o usuário está vinculado a um profissional"""
        return self.professional is not None