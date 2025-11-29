from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Zone, Schedule, ManualOverride, TemperatureLog
from .serializers import ZoneSerializer, ScheduleSerializer, ManualOverrideSerializer, TemperatureLogSerializer
from rest_framework.permissions import IsAuthenticated


class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    permission_classes = [IsAuthenticated]


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]


class ManualOverrideViewSet(viewsets.ModelViewSet):
    queryset = ManualOverride.objects.all()
    serializer_class = ManualOverrideSerializer
    permission_classes = [IsAuthenticated]


class TemperatureLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TemperatureLog.objects.all()
    serializer_class = TemperatureLogSerializer
    permission_classes = [IsAuthenticated]
