from rest_framework import serializers
from .models import Zone, Schedule, ManualOverride, TemperatureLog


class ManualOverrideSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManualOverride
        fields = ['id', 'zone', 'target_temperature', 'active', 'created_at']
        read_only_fields = ['id', 'created_at']


class ZoneSerializer(serializers.ModelSerializer):
    manual_override = ManualOverrideSerializer(read_only=True)

    class Meta:
        model = Zone
        fields = [
            'id',
            'name',
            'pin',
            'current_temperature',
            'target_temperature',
            'manual_override'
        ]
        read_only_fields = ['id']


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'zone', 'day_of_week', 'time', 'target_temperature']
        read_only_fields = ['id']


class TemperatureLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemperatureLog
        fields = ['id', 'zone', 'temperature', 'source', 'timestamp']
        read_only_fields = ['id']
