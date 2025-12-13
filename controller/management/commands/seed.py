from django.core.management.base import BaseCommand
from django.utils import timezone
from controller.models import Zone, ManualOverride, Schedule
import random
from datetime import timedelta, time

class Command(BaseCommand):
    help = "Seed the database with initial zones, schedules, and optional manual overrides"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database...")

        # --- Seed Zones ---
        zones_data = [
            ("Living Room", 21.5),
            ("Bedroom", 19.0),
            ("Kitchen", 22.0),
            ("Bathroom", 20.0),
            ("Office", 21.0),
        ]

        for name, current_temp in zones_data:
            zone, created = Zone.objects.get_or_create(
                name=name,
                defaults={
                    'current_temperature': current_temp
                }
            )
            if created:
                self.stdout.write(f"Created zone: {name} (current: {current_temp}°C)")
            else:
                self.stdout.write(f"Zone '{name}' already exists, skipping.")

        # --- Seed sample schedules for each zone ---
        for zone in Zone.objects.all():
            # Create 2 sample schedules per zone: morning and evening
            schedules_data = [
                {"start": time(6, 0), "end": time(9, 0), "target_temp": 21.0},
                {"start": time(18, 0), "end": time(22, 0), "target_temp": 22.0},
            ]
            for day in range(7):  # 0=Monday .. 6=Sunday
                for sched in schedules_data:
                    schedule, created = Schedule.objects.get_or_create(
                        zone=zone,
                        day_of_week=day,
                        start_time=sched["start"],
                        end_time=sched["end"],
                        defaults={"target_temperature": sched["target_temp"]}
                    )
                    if created:
                        self.stdout.write(
                            f"Created schedule for {zone.name} ({day}): {sched['start']} - {sched['end']} ({sched['target_temp']}°C)"
                        )

        # --- Optional: Add one-time manual overrides ---
        now = timezone.now()
        for zone in Zone.objects.all():
            # Check if any active override exists
            active_overrides = ManualOverride.objects.filter(
                zone=zone,
                active_from__lte=now
            ).filter(
                active_until__gte=now
            ) | ManualOverride.objects.filter(
                zone=zone,
                active_from__lte=now,
                active_until__isnull=True
            )

            if not active_overrides.exists() and random.choice([True, False]):
                # Randomly choose +2°C or -2°C
                override_temp = 21.0 + random.choice([-2, 2])
                ManualOverride.objects.create(
                    zone=zone,
                    target_temperature=override_temp,
                    active_from=now,
                    active_until=now + timedelta(hours=2)
                )
                self.stdout.write(
                    f"Created manual override for {zone.name}: {override_temp}°C (2h)"
                )

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))
