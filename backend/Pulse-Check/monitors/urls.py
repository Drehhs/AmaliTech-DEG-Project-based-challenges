from django.urls import path
from .views import (
    MonitorCreateView,
    MonitorHeartbeatView,
    MonitorPauseView,
    MonitorDetailView,
    MonitorListView,
    MonitorStatisticsView,
)

app_name = 'monitors'

urlpatterns = [
    # Create a new monitor
    path('', MonitorCreateView.as_view(), name='monitor-create'),
    
    # List all monitors
    path('list/', MonitorListView.as_view(), name='monitor-list'),
    
    # Get statistics dashboard
    path('statistics/', MonitorStatisticsView.as_view(), name='monitor-statistics'),
    
    # Get monitor details
    path('<str:monitor_id>/', MonitorDetailView.as_view(), name='monitor-detail'),
    
    # Send heartbeat to reset timer
    path('<str:monitor_id>/heartbeat/', MonitorHeartbeatView.as_view(), name='monitor-heartbeat'),
    
    # Pause a monitor
    path('<str:monitor_id>/pause/', MonitorPauseView.as_view(), name='monitor-pause'),
]
