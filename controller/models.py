import datetime
from django.utils import timezone
from django.db import models

# Zone / Room
class Zone(models.Model):
    name = models.CharField(max_length=100)
    pin = models.PositiveIntegerField(
        unique=True, null=True, blank=True)  # Arduino pin
    current_temperature = models.FloatField(default=20.0)

    def __str__(self):
        return self.name
    
    @property
    def get_active_target(self):
        now = timezone.localtime()
        manual = self.manualoverride_set.filter(
            active_from__lte=now
        ).filter(
            models.Q(active_until__gte=now) | models.Q(active_until__isnull=True)
        ).first()
        if manual:
            return manual.target_temperature
        # fallback to schedule
        next_sched, _ = self.next_schedule(now)
        if next_sched:
            return next_sched.target_temperature
        return 20.0
    
    def next_schedule(self, now=None):
        """
        Returns the next Schedule instance and its next start datetime for this zone.
        """
        if now is None:
            now = timezone.localtime()

        today_weekday = now.weekday()
        upcoming = []

        for sched in self.schedule_set.all():
            days_ahead = (sched.day_of_week - today_weekday) % 7
            sched_date = now.date() + datetime.timedelta(days=days_ahead)
            start_dt = datetime.datetime.combine(sched_date, sched.start_time)
            start_dt = timezone.make_aware(start_dt, timezone.get_current_timezone())
            if start_dt <= now:
                # Already started today, look for next week
                start_dt += datetime.timedelta(days=7)
            upcoming.append((start_dt, sched))

        if not upcoming:
            return None, None

        next_dt, next_sched = min(upcoming, key=lambda x: x[0])
        return next_sched, next_dt    


class Schedule(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(
        choices=[
            (0, "Monday"),
            (1, "Tuesday"),
            (2, "Wednesday"),
            (3, "Thursday"),
            (4, "Friday"),
            (5, "Saturday"),
            (6, "Sunday"),
        ]
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    target_temperature = models.FloatField()
    priority = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["priority", "start_time"]
        unique_together = (
            "zone",
            "day_of_week",
            "start_time",
            "end_time",
        )
        
    @property
    def day_name(self):
        return dict(self._meta.get_field('day_of_week').choices).get(self.day_of_week)

class ManualOverride(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    target_temperature = models.FloatField()
    active_from = models.DateTimeField(default=timezone.now)
    active_until = models.DateTimeField(null=True, blank=True)

    def is_active(self, now):
        return self.active_until is None or now < self.active_until


class TemperatureLog(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    temperature = models.FloatField()
    source = models.CharField(
        max_length=20,
        choices=[("schedule", "Schedule"), ("manual", "Manual")]
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.zone.name} - {self.temperature}°C ({self.source})"
