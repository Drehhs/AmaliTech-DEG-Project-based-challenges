import json
import logging
from datetime import datetime
from typing import Dict, Any
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


class AlertService:
    """Service for handling alert notifications."""
    
    @staticmethod
    def trigger_alert(monitor_id: str, alert_email: str, timeout: int, last_heartbeat) -> Dict[str, Any]:
        """
        Trigger an alert for a device that has gone offline.
        
        Args:
            monitor_id: The ID of the monitor that triggered the alert
            alert_email: Email address to send alert to
            timeout: The timeout duration in seconds
            last_heartbeat: The last heartbeat timestamp
            
        Returns:
            Dictionary containing alert details
        """
        now = timezone.now()
        
        alert_data = {
            'ALERT': f'Device {monitor_id} is down!',
            'time': now.isoformat(),
            'alert_email': alert_email,
            'timeout': timeout,
            'last_heartbeat': last_heartbeat.isoformat() if last_heartbeat else None,
            'monitor_id': monitor_id
        }
        
        # Log the alert (console output as per requirements)
        logger.critical(json.dumps(alert_data))
        print(f"ALERT: {json.dumps(alert_data)}")
        
        # In production, you would:
        # 1. Send email via Django's send_mail()
        # 2. Call a webhook URL
        # 3. Push to a notification service (e.g., Sentry, PagerDuty)
        # 4. Store in an Alert model for history
        
        return alert_data
    
    @staticmethod
    def send_webhook(url: str, data: Dict[str, Any]) -> bool:
        """
        Send alert data to a webhook URL.
        
        Args:
            url: The webhook URL to send data to
            data: The alert data to send
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import requests
            
            response = requests.post(
                url,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"Webhook sent successfully to {url}")
                return True
            else:
                logger.error(f"Webhook failed with status {response.status_code}")
                return False
        
        except ImportError:
            logger.warning("requests library not installed, webhook not sent")
            return False
        except Exception as e:
            logger.error(f"Error sending webhook: {str(e)}")
            return False
    
    @staticmethod
    def send_email(subject: str, message: str, recipient: str) -> bool:
        """
        Send an email alert.
        
        Args:
            subject: Email subject
            message: Email body
            recipient: Recipient email address
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from django.core.mail import send_mail
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@pulsecheck.com',
                [recipient],
                fail_silently=False,
            )
            
            logger.info(f"Email sent successfully to {recipient}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
