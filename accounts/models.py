from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Modèle utilisateur personnalisé pour l'application Déchets KO
    """
    ROLE_CHOICES = [
        ('citizen', 'Citoyen'),
        ('collector', 'Collecteur'),
        ('coordinator', 'Coordinateur'),
        ('municipality', 'Municipalité'),
        ('admin', 'Administrateur'),
        ('prn_agent', 'Agent PRN'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='citizen')
    phone = models.CharField(max_length=20, blank=True, null=True)
    team = models.ForeignKey('waste_management.Team', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    @property
    def name(self):
        return self.get_full_name() or self.username