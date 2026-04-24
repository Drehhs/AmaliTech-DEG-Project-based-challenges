from rest_framework import serializers
from .models import Monitor


class MonitorSerializer(serializers.ModelSerializer):
    """Serializer for Monitor model with validation."""
    
    class Meta:
        model = Monitor
        fields = [
            'id',
            'timeout',
            'alert_email',
            'status',
            'last_heartbeat',
            'expires_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'status',
            'last_heartbeat',
            'expires_at',
            'created_at',
            'updated_at',
        ]
    
    def validate_timeout(self, value):
        """Validate that timeout is a positive integer."""
        if value <= 0:
            raise serializers.ValidationError("Timeout must be a positive integer.")
        return value


class MonitorCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new monitor."""
    
    class Meta:
        model = Monitor
        fields = ['id', 'timeout', 'alert_email']
    
    def validate_timeout(self, value):
        """Validate that timeout is a positive integer."""
        if value <= 0:
            raise serializers.ValidationError("Timeout must be a positive integer.")
        return value


class MonitorStatusSerializer(serializers.ModelSerializer):
    """Serializer for monitor status updates."""
    
    class Meta:
        model = Monitor
        fields = [
            'id',
            'status',
            'last_heartbeat',
            'expires_at',
            'timeout',
            'alert_email',
        ]
        read_only_fields = ['id', 'timeout', 'alert_email']


class MonitorStatisticsSerializer(serializers.Serializer):
    """Serializer for monitor statistics dashboard."""
    
    total_monitors = serializers.IntegerField()
    active_monitors = serializers.IntegerField()
    paused_monitors = serializers.IntegerField()
    down_monitors = serializers.IntegerField()
    expiring_soon = serializers.IntegerField(help_text="Monitors expiring in next 5 minutes")
    uptime_percentage = serializers.FloatField(help_text="Percentage of monitors that are active")
