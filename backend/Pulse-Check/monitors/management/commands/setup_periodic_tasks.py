from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule


class Command(BaseCommand):
    help = 'Set up periodic tasks for monitor expiration checking'

    def handle(self, *args, **options):
        # Create or get the interval schedule (every 10 seconds)
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=10,
            period=IntervalSchedule.SECONDS,
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created interval schedule: {schedule}'))
        else:
            self.stdout.write(self.style.WARNING(f'Using existing interval schedule: {schedule}'))
        
        # Create or update the periodic task
        task, created = PeriodicTask.objects.get_or_create(
            name='Check Expired Monitors',
            defaults={
                'interval': schedule,
                'task': 'monitors.tasks.check_expired_monitors',
                'enabled': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created periodic task: {task.name}'))
        else:
            task.interval = schedule
            task.enabled = True
            task.save()
            self.stdout.write(self.style.WARNING(f'Updated periodic task: {task.name}'))
        
        self.stdout.write(self.style.SUCCESS('Periodic tasks setup complete!'))
