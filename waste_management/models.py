from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Team(models.Model):
    """
    Modèle pour les équipes de collecte
    """
    SPECIALIZATION_CHOICES = [
        ('general', 'Collecte générale'),
        ('recycling', 'Recyclage'),
        ('organic', 'Déchets organiques'),
        ('hazardous', 'Déchets dangereux'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    name = models.CharField(max_length=100)
    leader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='led_teams')
    specialization = models.CharField(max_length=20, choices=SPECIALIZATION_CHOICES, default='general')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    @property
    def leader_name(self):
        return self.leader.name if self.leader else ''

class CollectionPoint(models.Model):
    """
    Modèle pour les points de collecte
    """
    TYPE_CHOICES = [
        ('bin', 'Poubelle'),
        ('container', 'Conteneur'),
        ('recycling', 'Recyclage'),
    ]
    
    STATUS_CHOICES = [
        ('empty', 'Vide'),
        ('half', 'À moitié plein'),
        ('full', 'Plein'),
        ('overflow', 'Débordement'),
    ]
    
    name = models.CharField(max_length=200)
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='empty')
    last_collection = models.DateTimeField(null=True, blank=True)
    next_collection = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"

class Truck(models.Model):
    """
    Modèle pour les camions
    """
    STATUS_CHOICES = [
        ('available', 'Disponible'),
        ('collecting', 'En collecte'),
        ('maintenance', 'Maintenance'),
        ('offline', 'Hors ligne'),
        ('unavailable', 'Indisponible'),
    ]
    
    plate_number = models.CharField(max_length=20, unique=True)
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    current_latitude = models.FloatField(default=0)
    current_longitude = models.FloatField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    estimated_time = models.IntegerField(null=True, blank=True, help_text="Temps estimé en minutes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.plate_number} - {self.get_status_display()}"
    
    @property
    def driver_name(self):
        return self.driver.name if self.driver else ''

class Report(models.Model):
    """
    Modèle pour les signalements
    """
    TYPE_CHOICES = [
        ('overflow', 'Débordement'),
        ('damage', 'Dommage'),
        ('illegal_dump', 'Dépôt sauvage'),
        ('missed_collection', 'Collecte manquée'),
        ('other', 'Autre'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('in_progress', 'En cours'),
        ('resolved', 'Résolu'),
        ('closed', 'Fermé'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Faible'),
        ('medium', 'Moyenne'),
        ('high', 'Haute'),
        ('urgent', 'Urgente'),
    ]
    
    REPORTER_TYPE_CHOICES = [
        ('citizen', 'Citoyen'),
        ('collector', 'Collecteur'),
        ('agent', 'Agent'),
    ]
    
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.TextField()
    reported_by = models.CharField(max_length=200)
    reporter_name = models.CharField(max_length=200, blank=True)
    reporter_phone = models.CharField(max_length=20, blank=True)
    reporter_email = models.EmailField(blank=True)
    reporter_type = models.CharField(max_length=20, choices=REPORTER_TYPE_CHOICES, default='citizen')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    assigned_to = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.address[:50]}"

class Schedule(models.Model):
    """
    Modèle pour les plannings
    """
    STATUS_CHOICES = [
        ('planned', 'Planifié'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
    ]
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    truck = models.ForeignKey(Truck, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    estimated_end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.team.name} - {self.date}"

class ScheduleRoute(models.Model):
    """
    Modèle pour les routes des plannings
    """
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='route_points')
    collection_point = models.ForeignKey(CollectionPoint, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.schedule} - {self.collection_point.name} (#{self.order})"

class Incident(models.Model):
    """
    Modèle pour les incidents
    """
    TYPE_CHOICES = [
        ('traffic', 'Circulation'),
        ('breakdown', 'Panne'),
        ('accident', 'Accident'),
        ('weather', 'Météo'),
        ('other', 'Autre'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Faible'),
        ('medium', 'Moyenne'),
        ('high', 'Élevée'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('resolved', 'Résolu'),
    ]
    
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.TextField()
    reported_by = models.CharField(max_length=200)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    impact = models.TextField()
    estimated_delay = models.IntegerField(default=0, help_text="Délai estimé en minutes")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.address[:50]}"

class Statistics(models.Model):
    """
    Modèle pour les statistiques
    """
    period = models.CharField(max_length=50)
    total_collections = models.IntegerField(default=0)
    total_waste = models.FloatField(default=0)  # en tonnes
    recycling_rate = models.FloatField(default=0)  # en pourcentage
    efficiency = models.FloatField(default=0)  # en pourcentage
    reports_resolved = models.IntegerField(default=0)
    average_response_time = models.FloatField(default=0)  # en heures
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Statistiques - {self.period}"
    
    class Meta:
        verbose_name_plural = "Statistics"