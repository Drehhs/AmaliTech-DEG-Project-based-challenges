from django.urls import path
from .views import MonitorCreateView

app_name = 'monitors'

urlpatterns = [
    # Create a new monitor
    path('', MonitorCreateView.as_view(), name='monitor-create'),
]
