from django.core.management.base import BaseCommand
from controller.models import Zone, ManualOverride
import random


class Command(BaseCommand):
    help = "Seed the database with initial zones and manual overrides"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database...")

        # Clear existing data
        Zone.objects.all().delete()
        ManualOverride.objects.all().delete()

        # Default zones (name, current_temperature, target_temperature)
        zones_data = [
            ("Living Room", 21.5, 22.0),
            ("Bedroom", 19.0, 19.0),
            ("Kitchen", 22.0, 21.5),
            ("Bathroom", 20.0, 20.0),
        ]

        zones = []
        for name, current_temp, target_temp in zones_data:
            zone = Zone.objects.create(
                name=name,
                current_temperature=current_temp,
                target_temperature=target_temp
            )
            zones.append(zone)
            self.stdout.write(
                f"Created zone: {name} ({current_temp}°C, target: {target_temp}°C)")

        # Optional: add random manual overrides for testing
        for zone in zones:
            if random.choice([True, False]):  # randomly activate some overrides
                override_temp = zone.target_temperature + \
                    random.choice([-2, 2])
                override = ManualOverride.objects.create(
                    zone=zone, target_temperature=override_temp, active=True
                )
                self.stdout.write(
                    f"Created manual override for {zone.name}: {override_temp}°C"
                )

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))
