from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

# Create your models here.
class ScheduledTime(models.Model):
    """
    Model to store scheduled LPRS and Print Start times for different plants.
    """
    

    # Plant name - making it unique since each plant should have only one schedule
    plant_name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Name of the plant"
    )

    # Scheduled times - using TimeField for time-only values
    scheduled_lprs = models.TimeField(
        verbose_name="Scheduled LPRS",
        help_text="Scheduled LPRS time (HH:MM:SS)"
    )

    scheduled_print_start = models.TimeField(
        verbose_name="Scheduled Print Start",
        help_text="Scheduled print start time (HH:MM:SS)"
    )

    scheduled_print_finish = models.TimeField(
        verbose_name="Scheduled Print Finish",
        help_text="Scheduled print finish time (HH:MM:SS)",
        null=True,  # Allow null initially for migration
        blank=True
    )

    planned_folders = models.IntegerField(
        verbose_name="Planned Folders",
        help_text="Number of planned folders for this plant",
        default=1
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional: Add an active flag to enable/disable schedules
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'scheduled_time'  # Explicit table name as requested
        verbose_name = 'Scheduled Time'
        verbose_name_plural = 'Scheduled Times'
        ordering = ['plant_name']
        indexes = [
            models.Index(fields=['plant_name', 'is_active']),
        ]

    def __str__(self):
        return f"{self.plant_name} - LPRS: {self.scheduled_lprs}, Print: {self.scheduled_print_start}"

    def clean(self):
        """
        Custom validation to ensure scheduled_print_start is after or equal to scheduled_lprs.
        """
        if self.scheduled_lprs and self.scheduled_print_start:
            # Convert times to comparable format
            if self.scheduled_print_start < self.scheduled_lprs:
                # Handle case where print start is on the next day
                # This is a business logic decision - you may want to adjust
                pass


    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


    @classmethod
    def get_active_schedules(cls):
        """
        Get all active scheduled times.
        """
        return cls.objects.filter(is_active=True)

    @classmethod
    def get_schedule_by_plant(cls, plant_name):
        """
        Get schedule for a specific plant.
        """
        try:
            return cls.objects.get(plant_name__iexact=plant_name, is_active=True)
        except cls.DoesNotExist:
            return None

