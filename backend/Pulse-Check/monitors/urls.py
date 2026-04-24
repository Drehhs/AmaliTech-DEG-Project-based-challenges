from django.urls import path
from .views import MonitorCreateView, MonitorHeartbeatView

app_name = 'monitors'

urlpatterns = [
    # Create a new monitor
    path('', MonitorCreateView.as_view(), name='monitor-create'),
    
    # Send heartbeat to reset timer
    path('<str:monitor_id>/heartbeat/', MonitorHeartbeatView.as_view(), name='monitor-heartbeat'),
]
