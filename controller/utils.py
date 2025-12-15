# views.py
from django.http import JsonResponse
from controller.models import Zone, Schedule
from core.models import SystemSettings

def zone_schedule_api(request, zone_id):
    zone = Zone.objects.get(id=zone_id)
    system_settings = SystemSettings.objects.first()
    eco_temp = system_settings.eco_temperature if system_settings else 20

    schedule_data = {}
    for day in range(7):
        day_name = Schedule._meta.get_field('day_of_week').choices[day][1]
        day_scheds = Schedule.objects.filter(zone=zone, day_of_week=day).order_by('start_time')
        schedule_data[day_name] = [
            {
                'start_time': s.start_time.strftime("%H:%M"),
                'end_time': s.end_time.strftime("%H:%M"),
                'target_temperature': s.target_temperature
            } for s in day_scheds
        ]

    return JsonResponse({
        'zone': zone.name,
        'eco_temperature': eco_temp,
        'schedule': schedule_data
    })
