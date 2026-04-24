from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.db import transaction
from django.utils import timezone
from django.db.models import Count, Q
from .models import Monitor
from .serializers import MonitorCreateSerializer, MonitorStatusSerializer, MonitorStatisticsSerializer


class MonitorCreateView(APIView):
    """API endpoint to create a new monitor."""
    
    def post(self, request):
        """Create a new monitor with device ID, timeout, and alert email."""
        serializer = MonitorCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    monitor = Monitor.objects.create(
                        id=serializer.validated_data['id'],
                        timeout=serializer.validated_data['timeout'],
                        alert_email=serializer.validated_data['alert_email'],
                        status='active'
                    )
                
                response_data = {
                    'id': monitor.id,
                    'timeout': monitor.timeout,
                    'alert_email': monitor.alert_email,
                    'status': monitor.status,
                    'expires_at': monitor.expires_at,
                    'message': 'Monitor created successfully'
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                return Response(
                    {'error': f'Failed to create monitor: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MonitorHeartbeatView(APIView):
    """API endpoint to reset the monitor timer (heartbeat)."""
    
    def get_object(self, monitor_id):
        """Get monitor by ID or raise 404."""
        try:
            return Monitor.objects.get(id=monitor_id)
        except Monitor.DoesNotExist:
            raise NotFound(f"Monitor with ID '{monitor_id}' not found.")
    
    def post(self, request, monitor_id):
        """Reset the countdown timer for a specific monitor."""
        monitor = self.get_object(monitor_id)
        
        # Check if monitor is already down
        if monitor.status == 'down':
            return Response(
                {'error': 'Monitor is already down. Cannot reset timer.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reset the timer (this also un-pauses if paused)
        monitor.reset_timer()
        
        serializer = MonitorStatusSerializer(monitor)
        return Response({
            'message': 'Heartbeat received, timer reset',
            'monitor': serializer.data
        }, status=status.HTTP_200_OK)


class MonitorPauseView(APIView):
    """API endpoint to pause a monitor."""
    
    def get_object(self, monitor_id):
        """Get monitor by ID or raise 404."""
        try:
            return Monitor.objects.get(id=monitor_id)
        except Monitor.DoesNotExist:
            raise NotFound(f"Monitor with ID '{monitor_id}' not found.")
    
    def post(self, request, monitor_id):
        """Pause the monitor to prevent false alarms during maintenance."""
        monitor = self.get_object(monitor_id)
        
        # Check if monitor is already down
        if monitor.status == 'down':
            return Response(
                {'error': 'Monitor is already down. Cannot pause.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Pause the monitor
        monitor.pause()
        
        serializer = MonitorStatusSerializer(monitor)
        return Response({
            'message': 'Monitor paused successfully',
            'monitor': serializer.data
        }, status=status.HTTP_200_OK)


class MonitorDetailView(APIView):
    """API endpoint to retrieve monitor details."""
    
    def get_object(self, monitor_id):
        """Get monitor by ID or raise 404."""
        try:
            return Monitor.objects.get(id=monitor_id)
        except Monitor.DoesNotExist:
            raise NotFound(f"Monitor with ID '{monitor_id}' not found.")
    
    def get(self, request, monitor_id):
        """Retrieve details of a specific monitor."""
        monitor = self.get_object(monitor_id)
        serializer = MonitorStatusSerializer(monitor)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MonitorListView(APIView):
    """API endpoint to list all monitors."""
    
    def get(self, request):
        """List all monitors with optional status filtering."""
        status_filter = request.query_params.get('status', None)
        
        if status_filter:
            monitors = Monitor.objects.filter(status=status_filter)
        else:
            monitors = Monitor.objects.all()
        
        serializer = MonitorStatusSerializer(monitors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MonitorStatisticsView(APIView):
    """API endpoint to get monitor statistics and dashboard data."""
    
    def get(self, request):
        """Get statistics about all monitors including status breakdown."""
        now = timezone.now()
        
        # Count monitors by status
        stats = Monitor.objects.aggregate(
            total_monitors=Count('id'),
            active_monitors=Count('id', filter=Q(status='active')),
            paused_monitors=Count('id', filter=Q(status='paused')),
            down_monitors=Count('id', filter=Q(status='down')),
        )
        
        # Count monitors expiring in the next 5 minutes
        five_minutes_from_now = now + timezone.timedelta(minutes=5)
        expiring_soon = Monitor.objects.filter(
            status='active',
            expires_at__lte=five_minutes_from_now,
            expires_at__gt=now
        ).count()
        
        # Calculate uptime percentage (active / total * 100)
        total = stats['total_monitors']
        uptime_percentage = 0.0
        if total > 0:
            uptime_percentage = (stats['active_monitors'] / total) * 100
        
        statistics_data = {
            'total_monitors': stats['total_monitors'],
            'active_monitors': stats['active_monitors'],
            'paused_monitors': stats['paused_monitors'],
            'down_monitors': stats['down_monitors'],
            'expiring_soon': expiring_soon,
            'uptime_percentage': round(uptime_percentage, 2),
        }
        
        serializer = MonitorStatisticsSerializer(statistics_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

