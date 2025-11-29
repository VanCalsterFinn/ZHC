from django.db import models

# Zone / Room


class Zone(models.Model):
    name = models.CharField(max_length=100)
    pin = models.PositiveIntegerField(
        unique=True, null=True, blank=True)  # Arduino pin
    current_temperature = models.FloatField(default=20.0)
    target_temperature = models.FloatField(default=20.0)

    def __str__(self):
        return self.name


# Schedule for a zone
class Schedule(models.Model):
    DAY_CHOICES = [
        (0, "Monday"), (1, "Tuesday"), (2, "Wednesday"),
        (3, "Thursday"), (4, "Friday"), (5, "Saturday"),
        (6, "Sunday"),
    ]

    zone = models.ForeignKey(
        Zone, on_delete=models.CASCADE, related_name="schedules")
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    target_temperature = models.FloatField()

    class Meta:
        ordering = ["day_of_week", "start_time"]

    def __str__(self):
        return f"{self.zone.name} - {self.get_day_of_week_display()} {self.start_time} -- {self.end_time}"


# Manual override for a zone
class ManualOverride(models.Model):
    zone = models.OneToOneField(
        Zone, on_delete=models.CASCADE, related_name='manual_override')
    target_temperature = models.FloatField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.zone.name} - {'Active' if self.active else 'Inactive'}"


# Optional: Temperature log
class TemperatureLog(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    temperature = models.FloatField()
    source = models.CharField(
        max_length=20,
        choices=[("schedule", "Schedule"), ("manual", "Manual")]
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.zone.name} - {self.temperature}°C ({self.source})"
