from django.urls import path, include
from rest_framework import routers
from . import views
from accounts.serializers import UserSerializer
from accounts.models import User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

router = routers.DefaultRouter()
router.register(r'teams', views.TeamViewSet)
router.register(r'collection-points', views.CollectionPointViewSet)
router.register(r'trucks', views.TruckViewSet)
router.register(r'reports', views.ReportViewSet)
router.register(r'schedules', views.ScheduleViewSet)
router.register(r'schedule-routes', views.ScheduleRouteViewSet)
router.register(r'incidents', views.IncidentViewSet)
router.register(r'statistics', views.StatisticsViewSet)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]