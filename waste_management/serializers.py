from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import (
    Team, CollectionPoint, Truck, Report, Schedule, 
    ScheduleRoute, Incident, Statistics
)
from accounts.serializers import UserSerializer

class TeamSerializer(serializers.ModelSerializer):
    leader_name = serializers.ReadOnlyField()
    members = UserSerializer(source='user_set', many=True, read_only=True)
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'leader', 'leader_name', 'members', 'specialization', 'status', 'created_at']

class CollectionPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionPoint
        fields = [
            'id', 'name', 'address', 'latitude', 'longitude', 
            'type', 'status', 'last_collection', 'next_collection'
        ]

class TruckSerializer(serializers.ModelSerializer):
    driver_name = serializers.ReadOnlyField()
    current_location = serializers.SerializerMethodField()
    route = serializers.SerializerMethodField()

    # Accept driverId or driver for write, and plateNumber or plate_number, and estimatedTime or estimated_time
    driver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True, allow_null=False)
    plate_number = serializers.CharField(required=True)
    status = serializers.CharField(required=True)
    current_latitude = serializers.FloatField(required=False, allow_null=True)
    current_longitude = serializers.FloatField(required=False, allow_null=True)
    estimated_time = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Truck
        fields = [
            'id', 'plate_number', 'driver', 'driver_name', 'current_location',
            'status', 'estimated_time', 'route',
            'current_latitude', 'current_longitude'
        ]
        extra_kwargs = {
            'driver': {'required': True, 'allow_null': False},
            'plate_number': {'required': True},
            'status': {'required': True},
        }

    def to_internal_value(self, data):
        # Accept driverId or driver
        if 'driverId' in data and 'driver' not in data:
            data['driver'] = data['driverId']
        # Accept plateNumber or plate_number
        if 'plateNumber' in data and 'plate_number' not in data:
            data['plate_number'] = data['plateNumber']
        # Accept estimatedTime or estimated_time
        if 'estimatedTime' in data and 'estimated_time' not in data:
            data['estimated_time'] = data['estimatedTime']
        # Accept current_location dict
        if 'current_location' in data:
            loc = data['current_location']
            if isinstance(loc, dict):
                if 'latitude' in loc:
                    data['current_latitude'] = loc['latitude']
                if 'longitude' in loc:
                    data['current_longitude'] = loc['longitude']
        return super().to_internal_value(data)

    def get_current_location(self, obj):
        return {
            'latitude': obj.current_latitude,
            'longitude': obj.current_longitude
        }

    def get_route(self, obj):
        # Récupérer les points de collecte assignés à ce camion aujourd'hui
        from django.utils import timezone
        today = timezone.now().date()
        
        schedules = Schedule.objects.filter(
            truck=obj,
            date=today,
            status__in=['planned', 'in_progress']
        ).prefetch_related('route_points__collection_point')
        
        route_points = []
        for schedule in schedules:
            for route_point in schedule.route_points.all():
                route_points.append(CollectionPointSerializer(route_point.collection_point).data)
        
        return route_points

class ReportSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    reporter_contact = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = [
            'id', 'type', 'description', 'location', 'reported_by',
            'reporter_contact', 'reporter_type', 'status', 'priority',
            'assigned_to', 'created_at'
        ]
    
    def get_location(self, obj):
        return {
            'latitude': obj.latitude,
            'longitude': obj.longitude,
            'address': obj.address
        }
    
    def get_reporter_contact(self, obj):
        if obj.reporter_name or obj.reporter_phone or obj.reporter_email:
            return {
                'name': obj.reporter_name,
                'phone': obj.reporter_phone,
                'email': obj.reporter_email
            }
        return None

class ReportCreateSerializer(serializers.ModelSerializer):
    location = serializers.DictField(write_only=True)
    reporter_contact = serializers.DictField(write_only=True, required=False)
    
    class Meta:
        model = Report
        fields = [
            'type', 'description', 'location', 'reported_by',
            'reporter_contact', 'reporter_type', 'priority'
        ]
    
    def create(self, validated_data):
        location = validated_data.pop('location')
        reporter_contact = validated_data.pop('reporter_contact', {})
        
        report = Report.objects.create(
            latitude=location['latitude'],
            longitude=location['longitude'],
            address=location['address'],
            reporter_name=reporter_contact.get('name', ''),
            reporter_phone=reporter_contact.get('phone', ''),
            reporter_email=reporter_contact.get('email', ''),
            **validated_data
        )
        return report

class ScheduleRouteSerializer(serializers.ModelSerializer):
    collection_point = CollectionPointSerializer(read_only=True)
    
    class Meta:
        model = ScheduleRoute
        fields = ['collection_point', 'order', 'completed', 'completed_at']

class ScheduleSerializer(serializers.ModelSerializer):
    team_id = serializers.CharField(source='team.id', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    truck_id = serializers.CharField(source='truck.plate_number', read_only=True)
    route = ScheduleRouteSerializer(source='route_points', many=True, read_only=True)
    start_time = serializers.TimeField(format='%H:%M')
    estimated_end_time = serializers.TimeField(format='%H:%M')
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'team_id','team_name', 'truck_id', 'date', 'start_time',
            'estimated_end_time', 'status', 'route'
        ]

class ScheduleCreateSerializer(serializers.ModelSerializer):
    route = serializers.ListField(child=serializers.CharField(), write_only=True)
    
    class Meta:
        model = Schedule
        fields = ['team', 'truck', 'date', 'start_time', 'estimated_end_time', 'route']
    
    def create(self, validated_data):
        route_points = validated_data.pop('route')
        schedule = Schedule.objects.create(**validated_data)
        
        # Créer les points de route
        for index, point_id in enumerate(route_points):
            try:
                collection_point = CollectionPoint.objects.get(id=point_id)
                ScheduleRoute.objects.create(
                    schedule=schedule,
                    collection_point=collection_point,
                    order=index + 1
                )
            except CollectionPoint.DoesNotExist:
                continue
        
        return schedule

class IncidentSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    
    class Meta:
        model = Incident
        fields = [
            'id', 'type', 'description', 'location', 'reported_by',
            'severity', 'impact', 'estimated_delay', 'status', 'created_at'
        ]
    
    def get_location(self, obj):
        return {
            'latitude': obj.latitude,
            'longitude': obj.longitude,
            'address': obj.address
        }

class IncidentCreateSerializer(serializers.ModelSerializer):
    location = serializers.DictField(write_only=True)
    
    class Meta:
        model = Incident
        fields = [
            'type', 'description', 'location', 'reported_by',
            'severity', 'impact', 'estimated_delay'
        ]
    
    def create(self, validated_data):
        location = validated_data.pop('location')
        incident = Incident.objects.create(
            latitude=location['latitude'],
            longitude=location['longitude'],
            address=location['address'],
            **validated_data
        )
        return incident

class StatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistics
        fields = [
            'period', 'total_collections', 'total_waste', 'recycling_rate',
            'efficiency', 'reports_resolved', 'average_response_time'
        ]