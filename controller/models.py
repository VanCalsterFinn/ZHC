from django.db import models

# Zone / Room

class DayOfWeek(models.Model):
    DAY_CHOICES = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]
    day = models.IntegerField(choices=DAY_CHOICES, unique=True)

    def __str__(self):
        return self.get_day_display()

class Zone(models.Model):
    name = models.CharField(max_length=100)
    pin = models.PositiveIntegerField(
        unique=True, null=True, blank=True)  # Arduino pin
    current_temperature = models.FloatField(default=20.0)
    target_temperature = models.FloatField(default=20.0)

    def __str__(self):
        return self.name
    
    @property
    def get_active_target(self):
        override = getattr(self, "manual_override", None)
        if override and override.active:
            return override.target_temperature
        return self.target_temperature


class Schedule(models.Model):
    zones = models.ManyToManyField('Zone')
    days_of_week = models.ManyToManyField('DayOfWeek')
    start_time = models.TimeField()
    end_time = models.TimeField()
    target_temperature = models.FloatField()

    class Meta:
        ordering = ['start_time']  # or any other field
        verbose_name = "Schedule"
        verbose_name_plural = "Schedules"

    def __str__(self):
        zone_names = ", ".join([z.name for z in self.zones.all()])
        days = ", ".join([str(d) for d in self.days_of_week.all()])
        return f"{zone_names} ({days}) {self.start_time}-{self.end_time}"


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
