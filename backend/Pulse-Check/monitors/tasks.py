import logging
from celery import shared_task
from django.utils import timezone
from django.db import transaction
from .models import Monitor
from .services import AlertService

logger = logging.getLogger(__name__)


@shared_task
def check_expired_monitors():
    """
    Background task to check for expired monitors and trigger alerts.
    This task should be run periodically (e.g., every 10 seconds) by Celery Beat.
    """
    now = timezone.now()
    
    # Find all active monitors that have expired
    expired_monitors = Monitor.objects.filter(
        status='active',
        expires_at__lte=now
    ).select_for_update()
    
    alerts_triggered = []
    
    for monitor in expired_monitors:
        try:
            with transaction.atomic():
                # Re-check status within transaction to handle race conditions
                monitor = Monitor.objects.select_for_update().get(id=monitor.id)
                
                # Double-check that monitor is still active and expired
                if monitor.status == 'active' and monitor.expires_at and monitor.expires_at <= now:
                    # Mark as down and trigger alert
                    monitor.mark_as_down()
                    
                    # Trigger alert using AlertService
                    alert_data = AlertService.trigger_alert(
                        monitor_id=monitor.id,
                        alert_email=monitor.alert_email,
                        timeout=monitor.timeout,
                        last_heartbeat=monitor.last_heartbeat
                    )
                    
                    alerts_triggered.append(alert_data)
        
        except Monitor.DoesNotExist:
            continue
        except Exception as e:
            logger.error(f"Error processing monitor {monitor.id}: {str(e)}")
            continue
    
    if alerts_triggered:
        logger.info(f"Triggered {len(alerts_triggered)} alerts for expired monitors")
    
    return {
        'checked_at': now.isoformat(),
        'alerts_triggered': len(alerts_triggered),
        'alerts': alerts_triggered
    }


@shared_task
def cleanup_old_down_monitors(days=30):
    """
    Optional task to clean up monitors that have been down for a long time.
    This helps manage database size.
    """
    cutoff_date = timezone.now() - timezone.timedelta(days=days)
    
    deleted_count = Monitor.objects.filter(
        status='down',
        updated_at__lt=cutoff_date
    ).delete()[0]
    
    logger.info(f"Cleaned up {deleted_count} old down monitors")
    return {'deleted_count': deleted_count, 'cutoff_date': cutoff_date.isoformat()}
