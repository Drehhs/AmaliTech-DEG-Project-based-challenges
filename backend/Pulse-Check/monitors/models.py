from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class Monitor(models.Model):
    """Model representing a device monitor with timeout tracking."""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('down', 'Down'),
    ]
    
    id = models.CharField(max_length=255, primary_key=True, unique=True)
    timeout = models.PositiveIntegerField(help_text="Timeout duration in seconds")
    alert_email = models.EmailField(help_text="Email address for alert notifications")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True,
        help_text="Current status of the monitor"
    )
    last_heartbeat = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of the last heartbeat received"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Timestamp when the monitor will expire if no heartbeat"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'expires_at']),
        ]
    
    def __str__(self):
        return f"Monitor {self.id} ({self.status})"
    
    def clean(self):
        """Validate that timeout is a positive integer."""
        if self.timeout <= 0:
            raise ValidationError({'timeout': 'Timeout must be a positive integer.'})
    
    def save(self, *args, **kwargs):
        """Override save to set expires_at on creation and validate."""
        self.full_clean()
        
        # Set expires_at on initial creation
        if not self.created_at and not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(seconds=self.timeout)
        
        super().save(*args, **kwargs)
    
    def reset_timer(self):
        """Reset the countdown timer from the current time."""
        self.last_heartbeat = timezone.now()
        self.expires_at = timezone.now() + timezone.timedelta(seconds=self.timeout)
        self.status = 'active'
        self.save()
    
    def pause(self):
        """Pause the monitor by clearing expires_at."""
        self.status = 'paused'
        self.expires_at = None
        self.save()
    
    def mark_as_down(self):
        """Mark the monitor as down (device stopped sending heartbeats)."""
        self.status = 'down'
        self.expires_at = None
        self.save()
    
    @property
    def is_expired(self):
        """Check if the monitor has expired."""
        if self.status != 'active' or not self.expires_at:
            return False
        return timezone.now() > self.expires_at
