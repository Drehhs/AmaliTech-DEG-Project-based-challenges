from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from .models import Monitor
from .serializers import MonitorCreateSerializer


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

