from django.core.management.base import BaseCommand
from controller.models import Zone, Schedule, ManualOverride, TemperatureLog
from datetime import datetime, time
import time as t


class Command(BaseCommand):
    help = "Apply schedules and manual overrides to zones"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting schedule loop...")
        try:
            while True:
                now = datetime.now()
                weekday = now.weekday()  # 0 = Monday
                current_time = now.time()

                zones = Zone.objects.all()

                for zone in zones:
                    # Check manual override
                    override = ManualOverride.objects.filter(
                        zone=zone, active=True).first()
                    if override:
                        zone.current_temperature = override.target_temperature
                        source = "manual"
                    else:
                        # Find latest schedule for this time
                        schedules = Schedule.objects.filter(
                            zone=zone, day_of_week=weekday, time__lte=current_time).order_by('-time')
                        if schedules.exists():
                            zone.current_temperature = schedules.first().target_temperature
                            source = "schedule"
                        else:
                            # Keep current temperature if no schedule
                            source = "none"

                    zone.save()

                    # Optional: log temperature
                    if source != "none":
                        TemperatureLog.objects.create(
                            zone=zone, temperature=zone.current_temperature, source=source)

                    self.stdout.write(
                        f"{zone.name} -> {zone.current_temperature}°C ({source})")

                # Sleep before next check (e.g., 10 seconds)
                t.sleep(10)

        except KeyboardInterrupt:
            self.stdout.write("Schedule loop stopped.")
