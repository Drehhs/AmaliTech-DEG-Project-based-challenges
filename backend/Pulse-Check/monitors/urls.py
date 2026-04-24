from django.urls import path
from .views import MonitorCreateView, MonitorHeartbeatView, MonitorPauseView

app_name = 'monitors'

urlpatterns = [
    # Create a new monitor
    path('', MonitorCreateView.as_view(), name='monitor-create'),
    
    # Send heartbeat to reset timer
    path('<str:monitor_id>/heartbeat/', MonitorHeartbeatView.as_view(), name='monitor-heartbeat'),
    
    # Pause a monitor
    path('<str:monitor_id>/pause/', MonitorPauseView.as_view(), name='monitor-pause'),
]
