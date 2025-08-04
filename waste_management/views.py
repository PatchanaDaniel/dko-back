from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated ,AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import (
    Team, CollectionPoint, Truck, Report, Schedule, 
    ScheduleRoute, Incident, Statistics
)
from .serializers import (
    TeamSerializer, CollectionPointSerializer, TruckSerializer,
    ReportSerializer, ReportCreateSerializer, ScheduleSerializer,
    ScheduleCreateSerializer, ScheduleRouteSerializer, IncidentSerializer, IncidentCreateSerializer,
    StatisticsSerializer
)

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'specialization']

    def perform_create(self, serializer):
        team = serializer.save()
        leader = team.leader
        if leader:
            # Vérifie si l'utilisateur est déjà leader d'une autre équipe
            other_leader_teams = Team.objects.filter(leader=leader).exclude(id=team.id)
            if other_leader_teams.exists():
                raise serializers.ValidationError("Cet utilisateur est déjà chef d'une autre équipe.")
            # Vérifie que le leader est bien membre de l'équipe (team.user_set)
            if leader.team_id != team.id:
                leader.team = team
                leader.save()

    def perform_update(self, serializer):
        team = serializer.save()
        leader = team.leader
        if leader:
            # Vérifie si l'utilisateur est déjà leader d'une autre équipe
            other_leader_teams = Team.objects.filter(leader=leader).exclude(id=team.id)
            if other_leader_teams.exists():
                raise serializers.ValidationError("Cet utilisateur est déjà chef d'une autre équipe.")
            # Vérifie que le leader est bien membre de l'équipe (team.user_set)
            if leader.team_id != team.id:
                leader.team = team
                leader.save()

class CollectionPointViewSet(viewsets.ModelViewSet):
    queryset = CollectionPoint.objects.all()
    serializer_class = CollectionPointSerializer
    permission_classes = [AllowAny]  # Public access for collection points
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'type']

    def get_permissions(self):
        """
        Permissions spécifiques par action:
        - GET (list, retrieve): Accès public
        - POST, PUT, PATCH, DELETE: Authentification requise
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Mettre à jour le statut d'un point de collecte
        """
        collection_point = self.get_object()
        new_status = request.data.get('status')
        
        if new_status in dict(CollectionPoint.STATUS_CHOICES):
            collection_point.status = new_status
            if new_status == 'empty':
                collection_point.last_collection = timezone.now()
            collection_point.save()
            
            serializer = self.get_serializer(collection_point)
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Statut mis à jour avec succès'
            })
        
        return Response({
            'success': False,
            'message': 'Statut invalide'
        }, status=status.HTTP_400_BAD_REQUEST)

class TruckViewSet(viewsets.ModelViewSet):
    queryset = Truck.objects.all()
    serializer_class = TruckSerializer
    permission_classes = [AllowAny]  # Public access for trucks
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_permissions(self):
        """
        Permissions spécifiques par action:
        - GET (list, retrieve): Accès public
        - POST, PUT, PATCH, DELETE: Authentification requise
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """
        Créer un nouveau camion
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            truck = serializer.save()
            response_serializer = self.get_serializer(truck)
            return Response({
                'success': True,
                'data': response_serializer.data,
                'message': 'Camion créé avec succès'
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors,
            'message': 'Erreur lors de la création du camion'
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def update_location(self, request, pk=None):
        """
        Mettre à jour la position d'un camion
        """
        truck = self.get_object()
        location = request.data.get('current_location', {})
        
        if 'latitude' in location and 'longitude' in location:
            truck.current_latitude = location['latitude']
            truck.current_longitude = location['longitude']
            truck.save()
            
            serializer = self.get_serializer(truck)
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Position mise à jour avec succès'
            })
        
        return Response({
            'success': False,
            'message': 'Coordonnées invalides'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Mettre à jour le statut d'un camion
        """
        truck = self.get_object()
        new_status = request.data.get('status')
        
        if new_status in dict(Truck.STATUS_CHOICES):
            truck.status = new_status
            truck.save()
            
            serializer = self.get_serializer(truck)
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Statut mis à jour avec succès'
            })
        
        return Response({
            'success': False,
            'message': 'Statut invalide'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'], url_path='estimated-time')
    def update_estimated_time(self, request, pk=None):
        """
        Mettre à jour le temps estimé pour atteindre le prochain point de collecte
        PATCH /api/trucks/{id}/estimated-time/
        Body: {"estimated_time": 15}
        """
        truck = self.get_object()
        estimated_time = request.data.get('estimated_time')
        
        if estimated_time is not None:
            try:
                estimated_time = int(estimated_time)
                if estimated_time < 0:
                    return Response({
                        'success': False,
                        'message': 'Le temps estimé doit être positif'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                truck.estimated_time = estimated_time
                truck.save()
                
                serializer = self.get_serializer(truck)
                return Response({
                    'success': True,
                    'data': serializer.data,
                    'message': 'Temps estimé mis à jour avec succès'
                })
            except (ValueError, TypeError):
                return Response({
                    'success': False,
                    'message': 'Temps estimé invalide. Veuillez fournir un nombre entier.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'message': 'Le champ estimated_time est requis'
        }, status=status.HTTP_400_BAD_REQUEST)

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all().order_by('-created_at')
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'priority', 'type', 'reporter_type']
    def get_permissions(self):
        """
        Permissions spécifiques par action:
        - GET (list, retrieve): Accès public
        - POST, PUT, PATCH, DELETE: Authentification requise
        """
        if self.action in ['list', 'retrieve', 'create']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
   
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReportCreateSerializer
        return ReportSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print("Creating report with data:", request.data)
        if serializer.is_valid():
            report = serializer.save()
            response_serializer = ReportSerializer(report)
            return Response({
                'success': True,
                'data': response_serializer.data,
                'message': 'Signalement créé avec succès'
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors,
            'message': 'Erreur lors de la création du signalement'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def assign(self, request, pk=None):
        """
        Assigner un signalement à une équipe
        """
        report = self.get_object()
        assigned_to = request.data.get('assigned_to')
        
        if assigned_to:
            report.assigned_to = assigned_to
            report.status = 'in_progress'
            report.save()
            
            serializer = self.get_serializer(report)
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Signalement assigné avec succès'
            })
        
        return Response({
            'success': False,
            'message': 'Équipe non spécifiée'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def resolve(self, request, pk=None):
        """
        Marquer un signalement comme résolu
        """
        report = self.get_object()
        report.status = 'resolved'
        report.save()
        
        serializer = self.get_serializer(report)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Signalement marqué comme résolu'
        })

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all().order_by('-date', '-start_time')
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'team', 'date']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ScheduleCreateSerializer
        return ScheduleSerializer
    def get_permissions(self):
        """
        Permissions spécifiques par action:
        - GET (list, retrieve): Accès public
        - POST, PUT, PATCH, DELETE: Authentification requise
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print("Creating schedule with data:", request.data)
        if serializer.is_valid():
            schedule = serializer.save()
            response_serializer = ScheduleSerializer(schedule)
            return Response({
                'success': True,
                'data': response_serializer.data,
                'message': 'Planning créé avec succès'
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors,
            'message': 'Erreur lors de la création du planning'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def start(self, request, pk=None):
        """
        Démarrer un planning
        """
        schedule = self.get_object()
        schedule.status = 'in_progress'
        schedule.save()
        
        serializer = self.get_serializer(schedule)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Planning démarré'
        })
    
    @action(detail=True, methods=['patch'])
    def complete(self, request, pk=None):
        """
        Terminer un planning
        """
        schedule = self.get_object()
        schedule.status = 'completed'
        schedule.save()
        
        serializer = self.get_serializer(schedule)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Planning terminé'
        })

class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all().order_by('-created_at')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'severity', 'type']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return IncidentCreateSerializer
        return IncidentSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print("Creating incident with data:", request.data)
        
        if serializer.is_valid() :
            incident = serializer.save()
            response_serializer = IncidentSerializer(incident)
            return Response({
                'success': True,
                'data': response_serializer.data,
                'message': 'Incident créé avec succès'
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors,
            'message': 'Erreur lors de la création de l\'incident'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def resolve(self, request, pk=None):
        """
        Résoudre un incident
        """
        incident = self.get_object()
        incident.status = 'resolved'
        incident.save()
        
        serializer = self.get_serializer(incident)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Incident résolu'
        })

class StatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Statistics.objects.all().order_by('-created_at')
    serializer_class = StatisticsSerializer
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        """
        Récupérer les statistiques avec période optionnelle
        """
        period = request.query_params.get('period')
        
        if period:
            try:
                stats = Statistics.objects.filter(period=period).first()
                if stats:
                    serializer = self.get_serializer(stats)
                    return Response({
                        'success': True,
                        'data': serializer.data
                    })
            except Statistics.DoesNotExist:
                pass
        
        # Retourner les statistiques les plus récentes
        latest_stats = self.queryset.first()
        if latest_stats:
            serializer = self.get_serializer(latest_stats)
            return Response({
                'success': True,
                'data': serializer.data
            })
        
        # Retourner des statistiques par défaut si aucune n'existe
        default_stats = {
            'period': 'Janvier 2025',
            'total_collections': 1247,
            'total_waste': 8435,
            'recycling_rate': 67.8,
            'efficiency': 89.2,
            'reports_resolved': 156,
            'average_response_time': 4.2
        }
        
        return Response({
            'success': True,
            'data': default_stats
        })

class ScheduleRouteViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les points de route des plannings
    """
    queryset = ScheduleRoute.objects.all()
    serializer_class = ScheduleRouteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['schedule', 'completed']

    @action(detail=True, methods=['patch'])
    def mark_completed(self, request, pk=None):
        """
        Marquer un point de route comme complété
        """
        route_point = self.get_object()
        route_point.completed = True
        route_point.completed_at = timezone.now()
        route_point.save()
        
        serializer = self.get_serializer(route_point)
        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=True, methods=['patch'])
    def mark_incomplete(self, request, pk=None):
        """
        Marquer un point de route comme non complété
        """
        route_point = self.get_object()
        route_point.completed = False
        route_point.completed_at = None
        route_point.save()
        
        serializer = self.get_serializer(route_point)
        return Response({
            'success': True,
            'data': serializer.data
        })