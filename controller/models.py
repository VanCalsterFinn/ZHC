import datetime
from django.utils import timezone
from django.db import models
from django.db.models import Q
# Zone / Room


import datetime
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Zone(models.Model):
    name = models.CharField(max_length=100)
    pin = models.PositiveIntegerField(unique=True, null=True, blank=True)
    current_temperature = models.FloatField(default=20.0)

    def __str__(self):
        return self.name

    def current_schedule(self, now=None):
        """
        Returns the currently active schedule, handling overnight schedules.
        """
        if now is None:
            now = timezone.localtime()

        weekday = now.weekday()
        current_time = now.time()

        # Get schedules for today
        today_schedules = self.schedule_set.filter(day_of_week=weekday)

        for sched in today_schedules:
            # Normal schedule
            if sched.start_time < sched.end_time:
                if sched.start_time <= current_time < sched.end_time:
                    return sched
            else:
                # Overnight schedule: e.g., 22:00 - 06:00
                if current_time >= sched.start_time or current_time < sched.end_time:
                    return sched

        return None

    def next_schedule(self, now=None):
        """
        Returns the next schedule and its start datetime.
        Handles overnight schedules correctly.
        """
        if now is None:
            now = timezone.localtime()

        today_weekday = now.weekday()
        upcoming = []

        for sched in self.schedule_set.all():
            days_ahead = (sched.day_of_week - today_weekday) % 7
            sched_date = now.date() + datetime.timedelta(days=days_ahead)
            start_dt = datetime.datetime.combine(sched_date, sched.start_time)
            start_dt = timezone.make_aware(
                start_dt, timezone.get_current_timezone())

            # If already started, skip to next occurrence
            current_time = now.time()
            if days_ahead == 0 and (
                (sched.start_time < sched.end_time and sched.start_time <= current_time)
                or (sched.start_time > sched.end_time and current_time >= sched.start_time)
            ):
                start_dt += datetime.timedelta(days=7)

            upcoming.append((start_dt, sched))

        if not upcoming:
            return None, None

        next_dt, next_sched = min(upcoming, key=lambda x: x[0])
        return next_sched, next_dt

    def next_temperature_event(self, now=None, include_manual=True):
        if now is None:
            now = timezone.localtime()

        events = []

        # 🔹 Manual overrides
        if include_manual:
            manual = self.manualoverride_set.filter(
                active_from__lte=now
            ).filter(
                Q(active_until__gt=now) | Q(active_until__isnull=True)
            ).first()

            if manual and manual.active_until:
                events.append({
                    "time": manual.active_until,
                    "type": "manual_end",
                    "target": None,
                })

            next_manual = self.manualoverride_set.filter(
                active_from__gt=now
            ).order_by('active_from').first()

            if next_manual:
                events.append({
                    "time": next_manual.active_from,
                    "type": "manual_start",
                    "target": next_manual.target_temperature,
                })

        # 🔹 Schedule end
        current = self.current_schedule(now)
        if current:
            # Determine end date (today or tomorrow for overnight)
            if current.start_time < current.end_time:
                end_date = now.date()
            else:
                end_date = now.date() if now.time() < current.end_time else now.date() + \
                    datetime.timedelta(days=1)

            end_dt = timezone.make_aware(
                datetime.datetime.combine(end_date, current.end_time),
                timezone.get_current_timezone()
            )
            if end_dt > now:
                events.append({
                    "time": end_dt,
                    "type": "schedule_end",
                    "target": None,
                })

        # 🔹 Schedule start
        next_sched, start_dt = self.next_schedule(now)
        if next_sched and start_dt > now:
            events.append({
                "time": start_dt,
                "type": "schedule_start",
                "target": next_sched.target_temperature,
            })

        return min(events, key=lambda e: e["time"]) if events else None

    @property
    def get_active_target(self):
        now = timezone.localtime()

        # 1️ Active manual override wins
        manual = self.manualoverride_set.filter(
            active_from__lte=now
        ).filter(
            Q(active_until__gte=now) | Q(active_until__isnull=True)
        ).first()

        if manual:
            return manual.target_temperature

        # 2️ Active schedule
        current = self.current_schedule(now)
        if current:
            return current.target_temperature

        # 3️ Fallback
        return 20.0

    def next_temperature_change(self, now=None):
        # Next event ignoring manual overrides
        return self.next_temperature_event(now, include_manual=False)

    def next_target_temperature(self, now=None):
        event = self.next_temperature_event(now)
        return event["target"] if event and event["target"] is not None else self.get_active_target

    @property
    def next_change(self):
        # Use sparingly
        return self.next_temperature_event()


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
