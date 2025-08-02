from django.contrib import admin
from .models import (
    Team, CollectionPoint, Truck, Report, Schedule, 
    ScheduleRoute, Incident, Statistics
)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'leader', 'specialization', 'status', 'created_at')
    list_filter = ('specialization', 'status')
    search_fields = ('name', 'leader__username')

@admin.register(CollectionPoint)
class CollectionPointAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'status', 'address', 'last_collection')
    list_filter = ('type', 'status')
    search_fields = ('name', 'address')

@admin.register(Truck)
class TruckAdmin(admin.ModelAdmin):
    list_display = ('plate_number', 'driver', 'status', 'estimated_time')
    list_filter = ('status',)
    search_fields = ('plate_number', 'driver__username')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('type', 'reporter_name', 'status', 'priority', 'created_at')
    list_filter = ('type', 'status', 'priority', 'reporter_type')
    search_fields = ('description', 'reporter_name', 'address')

class ScheduleRouteInline(admin.TabularInline):
    model = ScheduleRoute
    extra = 0

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('team', 'truck', 'date', 'start_time', 'status')
    list_filter = ('status', 'date')
    inlines = [ScheduleRouteInline]

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('type', 'severity', 'status', 'estimated_delay', 'created_at')
    list_filter = ('type', 'severity', 'status')
    search_fields = ('description', 'address')

@admin.register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    list_display = ('period', 'total_collections', 'efficiency', 'recycling_rate', 'created_at')
    list_filter = ('created_at',)