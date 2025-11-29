from django.contrib import admin
from .models import Zone, Schedule, ManualOverride, TemperatureLog

admin.site.register(Zone)
admin.site.register(Schedule)
admin.site.register(ManualOverride)
admin.site.register(TemperatureLog)
