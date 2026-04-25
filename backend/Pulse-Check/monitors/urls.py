from django.urls import path
from .views import (
    MonitorListCreateView,
    MonitorHeartbeatView,
    MonitorPauseView,
    MonitorDetailView,
    MonitorListView,
    MonitorStatisticsView,
)

app_name = 'monitors'

urlpatterns = [
    # List and create monitors
    path('', MonitorListCreateView.as_view(), name='monitor-list-create'),
    
    # List all monitors (with filtering)
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
