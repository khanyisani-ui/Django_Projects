
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Assignment, Progress

@receiver(post_save, sender=Assignment)
def create_progress_for_assignment(sender, instance, created, **kwargs):
    if created:  # Only create Progress when a new Assignment is created
        Progress.objects.create(assignment=instance)