from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from waste_management.models import (
    Team, CollectionPoint, Truck, Report, Schedule, 
    ScheduleRoute, Incident, Statistics
)
from django.utils import timezone
from datetime import datetime, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Créer des utilisateurs
        self.create_users()
        
        # Créer des équipes
        self.create_teams()
        
        # Créer des points de collecte
        self.create_collection_points()
        
        # Créer des camions
        self.create_trucks()
        
        # Créer des signalements
        self.create_reports()
        
        # Créer des plannings
        self.create_schedules()
        
        # Créer des incidents
        self.create_incidents()
        
        # Créer des statistiques
       # self.create_statistics()

        # créer un super utilisateur
        self.create_superuser()
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
    
    def create_users(self):
        users_data = [
            {
            'username': f'Amadou_citizen',
            'email': 'amadou@citizen.sn',
            'role': 'citizen',
            'phone': '+221761234567',
            'first_name': 'Amadou',
            'last_name': 'Diallo'
            },
            {
            'username': f'Mohamed_collector',
            'email': 'mohamed@dechetsko.com',
            'role': 'collector',
            'phone': '+221772345678',
            'teamId': 'team-alpha',
            'first_name': 'Mohamed',
            'last_name': 'Diop'
            },
            {
            'username': f'Omar_coordinator',
            'email': 'omar@dechetsko.com',
            'role': 'coordinator',
            'phone': '+221773456789',
            'first_name': 'Omar',
            'last_name': 'Coordinator'
            },
            {
            'username': f'Maire_municipality',
            'email': 'maire@mairiedakar.com',
            'role': 'municipality',
            'phone': '+221774567890',
            'first_name': 'Maire',
            'last_name': 'Municipal'
            },
            {
            'username': f'Agent_prn_agent',
            'email': 'agent@dechetsko.com',
            'role': 'prn_agent',
            'phone': '+221785678901',
            'first_name': 'Agent',
            'last_name': 'PRN'
            },
            {
            'username': f'Daniel_collector',
            'email': 'daniel@dechetsko.com',
            'role': 'collector',
            'phone': '+221786789012',
            'teamId': 'team-gamma',
            'first_name': 'Daniel',
            'last_name': 'Tchaamie'
            },
            {
            'username': f'Mamadou_collector',
            'email': 'mamadou@dechetsko.com',
            'role': 'collector',
            'phone': '+221787890123',
            'teamId': 'team-alpha',
            'first_name': 'Mamadou',
            'last_name': 'Seck'
            },
            {
            'username': f'Khalifa_collector',
            'email': 'khalifa@dechetsko.com',
            'role': 'collector',
            'phone': '+221788901234',
            'teamId': 'team-beta',
            'first_name': 'Khalifa',
            'last_name': 'Ba'
            },
        ]
        
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'role': user_data['role'],
                    'phone': user_data['phone'],
                }
            )
            if created:
                user.set_password('password')
                user.save()
                self.stdout.write(f'Created user: {user.username}')
    
    def create_teams(self):
        teams_data = [
            {'name': 'Équipe Alpha', 'leader_username': 'Mohamed_collector', },
            {'name': 'Équipe Beta', 'leader_username': 'Khalifa_collector', },
            {'name': 'Équipe Gamma', 'leader_username': 'Daniel_collector', },
        ]
        
        for team_data in teams_data:
            try:
                leader = User.objects.get(username=team_data['leader_username'])
                team, created = Team.objects.get_or_create(
                    name=team_data['name'],
                    defaults={
                        'leader': leader,
                        
                    }
                )
                if created:
                    # Assigner le leader à l'équipe
                    leader.team = team
                    leader.save()
                    self.stdout.write(f'Created team: {team.name}')
            except User.DoesNotExist:
                self.stdout.write(f'Leader not found for team: {team_data["name"]}')
    
    def create_collection_points(self):
        points_data = [
            {
            'name': 'Marché de Yoff',
            'address': 'Avenue Léopold Sédar Senghor, Yoff, Dakar',
            'latitude': 14.7395,
            'longitude': -17.4734,
            'type': 'container',
            'status': 'half',
            'last_collection': '2025-01-15T08:00:00Z',
            'next_collection': '2025-01-17T08:00:00Z'
            },
            {
            'name': 'Ouest Foire Centre',
            'address': 'Route de l\'Aéroport, Ouest Foire, Dakar',
            'latitude': 14.7167,
            'longitude': -17.4833,
            'type': 'bin',
            'status': 'full',
            'last_collection': '2025-01-14T10:30:00Z',
            'next_collection': '2025-01-16T10:30:00Z'
            },
            {
            'name': 'HLM Grand Yoff',
            'address': 'Cité HLM Grand Yoff, Dakar',
            'latitude': 14.7500,
            'longitude': -17.4667,
            'type': 'recycling',
            'status': 'empty',
            'last_collection': '2025-01-15T14:00:00Z',
            'next_collection': '2025-01-18T14:00:00Z'
            },
            {
            'name': 'Point E',
            'address': 'Avenue Cheikh Anta Diop, Point E, Dakar',
            'latitude': 14.6928,
            'longitude': -17.4467,
            'type': 'container',
            'status': 'overflow',
            'last_collection': '2025-01-13T16:00:00Z',
            'next_collection': '2025-01-16T09:00:00Z'
            },
            
            {
            'name': 'Ouakam Village',
            'address': 'Route de la Corniche Ouest, Ouakam, Dakar',
            'latitude': 14.7167,
            'longitude': -17.5000,
            'type': 'bin',
            'status': 'full',
            'last_collection': '2025-01-14T15:00:00Z',
            'next_collection': '2025-01-16T15:00:00Z'
            },
            {
            'name': 'Ngor Almadies',
            'address': 'Route des Almadies, Ngor, Dakar',
            'latitude': 14.7500,
            'longitude': -17.5167,
            'type': 'recycling',
            'status': 'empty',
            'last_collection': '2025-01-15T09:00:00Z',
            'next_collection': '2025-01-18T09:00:00Z'
            },
            {
            'name': 'Guédiawaye Marché',
            'address': 'Marché Central, Guédiawaye',
            'latitude': 14.7667,
            'longitude': -17.4167,
            'type': 'container',
            'status': 'full',
            'last_collection': '2025-01-14T12:00:00Z',
            'next_collection': '2025-01-16T12:00:00Z'
            },
            {
            'name': 'Pikine Icotaf',
            'address': 'Avenue Blaise Diagne, Pikine',
            'latitude': 14.7547,
            'longitude': -17.3928,
            'type': 'bin',
            'status': 'half',
            'last_collection': '2025-01-15T13:00:00Z',
            'next_collection': '2025-01-17T13:00:00Z'
            },
            {
            'name': 'Dakar Plateau',
            'address': 'Place de l\'Indépendance, Dakar Plateau',
            'latitude': 14.6928,
            'longitude': -17.4467,
            'type': 'container',
            'status': 'empty',
            'last_collection': '2025-01-15T16:00:00Z',
            'next_collection': '2025-01-18T16:00:00Z'
            }
        ]
        """{
            'name': 'Mbao Centre',
            'address': 'Route Nationale, Mbao, Pikine',
            'latitude': 14.7297,
            'longitude': -17.3436,
            'type': 'container',
            'status': 'half',
            'last_collection': '2025-01-15T11:00:00Z',
            'next_collection': '2025-01-17T11:00:00Z'
            },"""
        
        for point_data in points_data:
            point, created = CollectionPoint.objects.get_or_create(
                name=point_data['name'],
                defaults={
                    **point_data,
                    'last_collection': timezone.now() - timedelta(days=1),
                    'next_collection': timezone.now() + timedelta(days=1)
                }
            )
            if created:
                self.stdout.write(f'Created collection point: {point.name}')
    
    def create_trucks(self):
        trucks_data = [
            {'plate_number': 'DK-001-AB', 'driver_username': 'Mohamed_collector', 'status': 'collecting'},
            {'plate_number': 'DK-002-CD', 'driver_username': 'Khalifa_collector', 'status': 'available'},
            {'plate_number': 'DK-003-EF', 'driver_username': 'Daniel_collector', 'status': 'maintenance'},
        ]
        
        for truck_data in trucks_data:
            try:
                driver = User.objects.get(username=truck_data['driver_username'])
                truck, created = Truck.objects.get_or_create(
                    plate_number=truck_data['plate_number'],
                    defaults={
                        'driver': driver,
                        'status': truck_data['status'],
                        'current_latitude': 14.7167 + random.uniform(-0.01, 0.01),
                        'current_longitude': -17.5000 + random.uniform(-0.01, 0.01),
                        'estimated_time': random.randint(15, 60) if truck_data['status'] == 'collecting' else None
                    }
                )
                if created:
                    self.stdout.write(f'Created truck: {truck.plate_number}')
            except User.DoesNotExist:
                self.stdout.write(f'Driver not found for truck: {truck_data["plate_number"]}')
    
    def create_reports(self):
        reports_data = [
            {
            'type': 'overflow',
            'description': 'Conteneur débordant depuis 2 jours au marché de Yoff, odeurs nauséabondes',
            'latitude': 14.7395,
            'longitude': -17.4734,
            'address': 'Marché de Yoff, Avenue Léopold Sédar Senghor',
            'reporter_name': 'Amadou Diallo',
            'reporter_phone': '+221701234567',
            'reporter_email': '',
            'reporter_type': 'citizen',
            'status': 'pending',
            'priority': 'high',
            'assigned_to': ''
            },
            {
            'type': 'damage',
            'description': 'Poubelle cassée à Ouest Foire, couvercle arraché par le vent',
            'latitude': 14.7167,
            'longitude': -17.4833,
            'address': 'Route de l\'Aéroport, Ouest Foire',
            'reporter_name': 'Mohamed Diop',
            'reporter_phone': '+221702345678',
            'reporter_email': '',
            'reporter_type': 'collector',
            'status': 'in_progress',
            'priority': 'medium',
            'assigned_to': 'Équipe maintenance',
            'created_at': datetime(2025, 1, 14, 16, 45, 0, tzinfo=timezone.utc)
            },
            {
            'type': 'missed_collection',
            'description': 'Collecte non effectuée selon le planning à Point E',
            'latitude': 14.6928,
            'longitude': -17.4467,
            'address': 'Avenue Cheikh Anta Diop, Point E',
            'reporter_name': 'Agent PRN Service',
            'reporter_phone': '+221705678901',
            'reporter_email': 'agent@dechetsko.com',
            'reporter_type': 'agent',
            'status': 'resolved',
            'priority': 'medium',
            'assigned_to': 'Équipe Alpha',
            'created_at': datetime(2025, 1, 13, 11, 20, 0, tzinfo=timezone.utc)
            }
        ]
        
        for report_data in reports_data:
            report, created = Report.objects.get_or_create(
                description=report_data['description'],
                defaults=report_data
            )
            if created:
                self.stdout.write(f'Created report: {report.type}')
    
    def create_schedules(self):
        """
        Crée des plannings d'équipe avec des routes, camions et points de collecte associés.
        """
        # Récupérer les équipes, camions et points de collecte existants
        teams = {t.name.lower(): t for t in Team.objects.all()}
        trucks = list(Truck.objects.all())
        points = list(CollectionPoint.objects.all())

        # Mapping pour accès rapide par index (comme mockCollectionPoints)
        points_by_index = {i: p for i, p in enumerate(points)}

        # Définition des plannings à créer (structure inspirée du mock fourni)
        schedules_data = [
            {
                'team_key': 'équipe alpha',
                'date': '2025-01-16',
                'route_indexes': [0, 1, 4],
                'truck_index': 0,
                'start_time': '08:00',
                'estimated_end_time': '12:00',
                'status': 'planned'
            },
            {
                'team_key': 'équipe beta',
                'date': '2025-01-16',
                'route_indexes': [5, 6],
                'truck_index': 1,
                'start_time': '09:00',
                'estimated_end_time': '13:00',
                'status': 'in_progress'
            },
            {
                'team_key': 'équipe gamma',
                'date': '2025-01-17',
                'route_indexes': [7, 8, 2],  # 9 n'existe pas, on prend 2 pour 3 points
                'truck_index': 2,
                'start_time': '14:00',
                'estimated_end_time': '16:00',
                'status': 'planned'
            }
        ]

        for sched in schedules_data:
            team = teams.get(sched['team_key'])
            truck = trucks[sched['truck_index']] if sched['truck_index'] < len(trucks) else None
            if not team or not truck:
                self.stdout.write(f"Team or truck not found for schedule: {sched}")
                continue

            schedule, created = Schedule.objects.get_or_create(
                team=team,
                truck=truck,
                date=sched['date'],
                defaults={
                    'start_time': sched['start_time'],
                    'estimated_end_time': sched['estimated_end_time'],
                    'status': sched['status']
                }
            )
            if created:
                # Créer les points de route associés
                for order, point_idx in enumerate(sched['route_indexes'], start=1):
                    point = points_by_index.get(point_idx)
                    if point:
                        ScheduleRoute.objects.create(
                            schedule=schedule,
                            collection_point=point,
                            order=order
                        )
                self.stdout.write(f'Created schedule for {team.name} ({sched["date"]})')
    
    def create_incidents(self):
        """
        Crée des incidents d'exemple pour la base de données.
        """
        from datetime import datetime
        from django.utils import timezone

        incidents_data = [
            {
                'type': 'traffic',
                'description': 'Embouteillage important sur la VDN suite à un accident',
                'latitude': 14.7167,
                'longitude': -17.4500,
                'address': 'Voie de Dégagement Nord (VDN)',
                'reported_by': 'Fatou Ba',
                'severity': 'high',
                'impact': 'Retard de 45 minutes sur la collecte à Ouest Foire',
                'estimated_delay': 45,
                'status': 'active',
                'created_at': datetime(2025, 1, 15, 10, 15, 0, tzinfo=timezone.utc)
            },
            {
                'type': 'breakdown',
                'description': 'Panne moteur du camion DK-2024-EF à Guédiawaye',
                'latitude': 14.7667,
                'longitude': -17.4167,
                'address': 'Marché Central, Guédiawaye',
                'reported_by': 'Daniel Tchaamie',
                'severity': 'high',
                'impact': 'Camion immobilisé, besoin de remplacement urgent',
                'estimated_delay': 120,
                'status': 'active',
                'created_at': datetime(2025, 1, 15, 7, 30, 0, tzinfo=timezone.utc)
            }
        ]

        for incident_data in incidents_data:
            incident, created = Incident.objects.get_or_create(
                description=incident_data['description'],
                defaults=incident_data
            )
            if created:
                self.stdout.write(f'Created incident: {incident.type}')
    
    def create_statistics(self):
        """
        Crée des statistiques d'exemple pour la base de données.
        """
        from datetime import datetime
        from django.utils import timezone

        statistics_data = [
            {
                'date': '2025-01-15',
                'total_collections': 150,
                'missed_collections': 10,
                'incidents_reported': 5,
                'average_delay': 30,
                'team': 'Équipe Alpha'
            },
            {
                'date': '2025-01-15',
                'total_collections': 120,
                'missed_collections': 8,
                'incidents_reported': 3,
                'average_delay': 25,
                'team': 'Équipe Beta'
            },
            {
                'date': '2025-01-15',
                'total_collections': 130,
                'missed_collections': 5,
                'incidents_reported': 4,
                'average_delay': 35,
                'team': 'Équipe Gamma'
            }
        ]

        for stat_data in statistics_data:
            date_obj = datetime.strptime(stat_data['date'], '%Y-%m-%d').date()
            team = Team.objects.filter(name=stat_data['team']).first()
            if team:
                statistic, created = Statistics.objects.get_or_create(
                    date=date_obj,
                    team=team,
                    defaults={
                        'total_collections': stat_data['total_collections'],
                        'missed_collections': stat_data['missed_collections'],
                        'incidents_reported': stat_data['incidents_reported'],
                        'average_delay': stat_data['average_delay'],
                    }
                )
                if created:
                    self.stdout.write(f'Created statistic for {team.name} on {stat_data["date"]}')

    def create_superuser(self):
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='passer'
            )
            self.stdout.write(self.style.SUCCESS('Super utilisateur créé.'))
        else:
            self.stdout.write(self.style.WARNING('Un super utilisateur existe déjà.'))