from django.core.management.base import BaseCommand
from controller.models import Zone, ManualOverride, DayOfWeek
import random


class Command(BaseCommand):
    help = "Seed the database with initial zones, days of week, and optional manual overrides"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database...")

        # --- Seed Days of the Week ---
        days = [
            0, 1, 2, 3, 4, 5, 6  # Monday = 0 ... Sunday = 6
        ]

        for day_value in days:
            day_obj, created = DayOfWeek.objects.get_or_create(day=day_value)
            if created:
                print(f"Created day of week: {day_obj.get_day_display()}")
            else:
                print(f"Day '{day_obj.get_day_display()}' already exists, skipping.")


        # --- Seed Zones ---
        zones_data = [
            ("Living Room", 21.5, 22.0),
            ("Bedroom", 19.0, 19.0),
            ("Kitchen", 22.0, 21.5),
            ("Bathroom", 20.0, 20.0),
        ]

        for name, current_temp, target_temp in zones_data:
            zone, created = Zone.objects.get_or_create(
                name=name,
                defaults={
                    'current_temperature': current_temp,
                    'target_temperature': target_temp
                }
            )
            if created:
                self.stdout.write(
                    f"Created zone: {name} ({current_temp}°C, target: {target_temp}°C)"
                )
            else:
                self.stdout.write(f"Zone '{name}' already exists, skipping.")

        # --- Optional: Add one-time manual overrides ---
        for zone in Zone.objects.all():
            if not ManualOverride.objects.filter(zone=zone, active=True).exists():
                if random.choice([True, False]):  # randomly activate some overrides
                    override_temp = zone.target_temperature + random.choice([-2, 2])
                    ManualOverride.objects.create(
                        zone=zone,
                        target_temperature=override_temp,
                        active=True
                    )
                    self.stdout.write(
                        f"Created manual override for {zone.name}: {override_temp}°C"
                    )

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))
