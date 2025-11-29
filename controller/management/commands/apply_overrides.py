from django.core.management.base import BaseCommand
from controller.models import Zone, ManualOverride
import time


class Command(BaseCommand):
    help = "Apply manual overrides to zones"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting manual override loop...")
        try:
            while True:
                # Get all active manual overrides
                overrides = ManualOverride.objects.filter(active=True)

                for override in overrides:
                    zone = override.zone
                    zone.current_temperature = override.target_temperature
                    zone.save()
                    self.stdout.write(
                        f"Applied override: {zone.name} -> {zone.current_temperature}°C")

                # Sleep for 10 seconds (adjust as needed)
                time.sleep(10)

        except KeyboardInterrupt:
            self.stdout.write("Manual override loop stopped.")
