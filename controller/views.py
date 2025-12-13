from collections import defaultdict
from django.http import Http404
from django.shortcuts import get_list_or_404, redirect, render
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, FormView
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Zone, Schedule, ManualOverride
from .forms import ScheduleBatchForm, ScheduleForm, ManualOverrideForm, ZoneForm
from django.db.models import Q



def get_active_overrides():
    now = timezone.now()
    return list(
        ManualOverride.objects.filter(active_from__lte=now).filter(
            Q(active_until__gte=now) | Q(active_until__isnull=True)
        )
    )

class DashboardView(ListView):
    model = Zone
    template_name = "controller/dashboard.html"
    context_object_name = "zones"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        zones = Zone.objects.all()
        now = timezone.localtime()

        # Active manual overrides
        overrides = get_active_overrides()
        active_overrides = {o.zone.id: o for o in overrides}

        # Next event per zone (manual or schedule)
        next_events = {}
        for zone in zones:
            # Next manual override
            next_manual = ManualOverride.objects.filter(zone=zone, active_from__gt=now).order_by('active_from').first()

            # Next schedule for today or next days
            today = now.weekday()
            next_schedule = Schedule.objects.filter(
                zone=zone
            ).filter(
                Q(day_of_week=today, start_time__gt=now.time()) |
                Q(day_of_week__gt=today)
            ).order_by('day_of_week', 'start_time').first()

            # Pick whichever comes first
            next_dt = None
            if next_manual and next_schedule:
                manual_dt = next_manual.active_from
                schedule_dt = timezone.make_aware(timezone.datetime.combine(
                    timezone.localdate() + timezone.timedelta(days=(next_schedule.day_of_week - today) % 7),
                    next_schedule.start_time
                ))
                next_dt = min(manual_dt, schedule_dt)
            elif next_manual:
                next_dt = next_manual.active_from
            elif next_schedule:
                next_dt = timezone.make_aware(timezone.datetime.combine(
                    timezone.localdate() + timezone.timedelta(days=(next_schedule.day_of_week - today) % 7),
                    next_schedule.start_time
                ))

            next_events[zone.id] = next_dt

        context.update({
            "zones": zones,
            "active_overrides": active_overrides,
            "next_events": next_events,
            "page_title": "Heating Dashboard",
            "breadcrumbs": [
                {"name": "Home", "url": "/", "active": True},
            ]
        })
        return context

class OverrideAdjustView(View):
    def post(self, request):
        zone_id = request.POST["zone"]
        delta = int(request.POST["delta"])

        zone = Zone.objects.get(id=zone_id)

        # Create or update manual override
        override, created = ManualOverride.objects.get_or_create(
            zone=zone,
            defaults={"target_temperature": zone.get_active_target, "active_from": timezone.now()}
        )

        override.target_temperature += delta
        override.target_temperature = max(5, min(30, override.target_temperature))
        override.active_from = timezone.now()
        override.active_until = None  # reset end time
        override.save()

        return redirect("controller:dashboard")



# Zone views
class ZoneListView(ListView):
    model = Zone
    template_name = "controller/zones.html"
    context_object_name = "zones"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        overrides = get_active_overrides()
        context.update({
            "overrides": {o.zone.id: o for o in overrides},
            "page_title": "Manage Zones",
            "breadcrumbs": [
                {"name": "Home", "url": "/", "active": False},
                {"name": "Zones", "url": None, "active": True},
            ]
        })
        return context


class ZoneCreateView(CreateView):
    model = Zone
    form_class = ZoneForm
    template_name = "controller/partials/_zone_form.html"
    success_url = reverse_lazy("zone-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        overrides = get_active_overrides()
        context.update({
            "overrides": {o.zone.id: o for o in overrides},
            "page_title": "Create Zone",
            "breadcrumbs": [
                {"name": "Home", "url": "/", "active": False},
                {"name": "Zones", "url": reverse_lazy("zone-list"), "active": False},
                {"name": "Create", "url": None, "active": True},
            ]
        })
        return context


class ZoneUpdateView(UpdateView):
    model = Zone
    form_class = ZoneForm
    template_name = "controller/partials/_zone_form.html"
    success_url = reverse_lazy("zone-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        overrides = get_active_overrides()
        context.update({
            "overrides": {o.zone.id: o for o in overrides},
            "page_title": "Update Zone",
            "breadcrumbs": [
                {"name": "Home", "url": "/", "active": False},
                {"name": "Zones", "url": reverse_lazy("zone-list"), "active": False},
                {"name": "Update", "url": None, "active": True},
            ]
        })
        return context


class ZoneDeleteView(DeleteView):
    model = Zone
    template_name = "controller/partials/_zone_confirm_delete.html"
    success_url = reverse_lazy("zone-list")

class ZoneScheduleListView(ListView):
    model = Schedule
    template_name = "controller/zone_schedules/zone_schedules_list.html"
    context_object_name = "schedules"

    def get_queryset(self):
        zone_id = self.kwargs['zone_id']
        return Schedule.objects.filter(zone_id=zone_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        zone_id = self.kwargs['zone_id']
        zone = Zone.objects.get(id=zone_id)
        context.update({
            "zone": zone,
            "form": ScheduleForm(),
            "page_title": "Zone Schedules",
            "breadcrumbs": [
                {"name": "Home", "url": "/", "active": False},
                {"name": f"{zone.name} Schedules", "url": None, "active": True},
            ]
        })
        return context
    
# Schedule views
class ScheduleListView(ListView):
    model = Schedule
    template_name = "controller/schedules.html"
    context_object_name = "schedules"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        zones = Zone.objects.all()
        context.update({
            "zones": zones,
            "form": ScheduleForm(),
            "page_title": "Schedules",
            "breadcrumbs": [
                {"name": "Home", "url": "/", "active": False},
                {"name": "Schedules", "url": None, "active": True},
            ]
        })
        return context


class ScheduleCreateView(CreateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = "controller/partials/_schedule_form.html"
    success_url = reverse_lazy('controller:schedule_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        overrides = get_active_overrides()
        context.update({
            "overrides": {o.zone.id: o for o in overrides},
            "page_title": "Create Schedule",
            "breadcrumbs": [
                {"name": "Home", "url": "/", "active": False},
                {"name": "Schedules", "url": reverse_lazy('controller:schedule_list'), "active": False},
                {"name": "Create", "url": None, "active": True},
            ]
        })
        return context

    def get_form_kwargs(self):
        """Pass the initial_zone to the form if ?zone=<id> is in the URL"""
        kwargs = super().get_form_kwargs()
        zone_id = self.request.GET.get('zone')
        if zone_id:
            kwargs['initial_zone'] = int(zone_id)
        return kwargs


class ScheduleUpdateView(UpdateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = "controller/partials/_schedule_form.html"
    success_url = reverse_lazy('controller:schedule_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        overrides = get_active_overrides()
        context.update({
            "overrides": {o.zone.id: o for o in overrides},
            "page_title": "Update Schedule",
            "breadcrumbs": [
                {"name": "Home", "url": "/", "active": False},
                {"name": "Schedules", "url": reverse_lazy('controller:schedule_list'), "active": False},
                {"name": "Update", "url": None, "active": True},
            ]
        })
        return context
    
    def get_form_kwargs(self):
        """Pass the initial_zone to the form if ?zone=<id> is in the URL"""
        kwargs = super().get_form_kwargs()
        zone_id = self.request.GET.get('zone')
        if zone_id:
            kwargs['initial_zone'] = int(zone_id)
        return kwargs

class ScheduleDeleteView(DeleteView):
    model = Schedule
    template_name = "controller/partials/_schedule_confirm_delete.html"
    success_url = reverse_lazy('controller:schedule_list')


# Manual Override views
class ManualOverrideListView(ListView):
    model = ManualOverride
    template_name = "controller/manual_override.html"
    context_object_name = "overrides"

    def get_queryset(self):
        return get_active_overrides()


class ManualOverrideCreateView(CreateView):
    model = ManualOverride
    form_class = ManualOverrideForm
    template_name = "controller/manual_override_form.html"
    success_url = reverse_lazy('manual_override')


class ManualOverrideUpdateView(UpdateView):
    model = ManualOverride
    form_class = ManualOverrideForm
    template_name = "controller/manual_override_form.html"
    success_url = reverse_lazy('manual_override')

class GroupedScheduleListView(TemplateView):
    template_name = "controller/grouped_schedule_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Fetch all schedules
        schedules = Schedule.objects.select_related('zone').all().order_by(
            'start_time', 'end_time', 'target_temperature', 'priority'
        )

        # Group schedules by identical settings
        grouped = defaultdict(lambda: {'zones': set(), 'days': set(), 'schedules': []})
        for sched in schedules:
            key = (sched.start_time, sched.end_time, sched.target_temperature, sched.priority)
            grouped[key]['zones'].add(sched.zone)         # set method
            grouped[key]['days'].add(sched.day_of_week)  # set method
            grouped[key]['schedules'].append(sched)

        # Convert to list for template
        grouped_schedules = []
        for key, value in grouped.items():
            start_time, end_time, temp, priority = key
            grouped_schedules.append({
                'zones': sorted(value['zones'], key=lambda z: z.name),
                'days': sorted(value['days']),
                'day_names': [dict(Schedule._meta.get_field('day_of_week').choices)[d] for d in sorted(value['days'])],
                'schedules': value['schedules'],
                'start_time': start_time,
                'end_time': end_time,
                'target_temperature': temp,
                'priority': priority,
            })

        context.update({
            "grouped_schedules": grouped_schedules,
            "page_title": "Grouped Schedules",
            "breadcrumbs": [
                {"name": "Home", "url": "/", "active": False},
                {"name": "Schedules", "url": reverse_lazy('controller:schedule_list'), "active": False},
                {"name": "Grouped Schedules", "url": None, "active": True},
            ]
        })
        return context

    
class GroupedScheduleUpdateView(FormView):
    template_name = "controller/partials/_grouped_schedules_form.html"
    form_class = ScheduleBatchForm

    def dispatch(self, request, *args, **kwargs):
        self.schedule_ids = self.kwargs['schedule_ids'].split(',')
        self.schedules = Schedule.objects.filter(id__in=self.schedule_ids)

        if not self.schedules.exists():
            raise Http404

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        first = self.schedules.first()

        kwargs['initial'] = {
            'start_time': first.start_time,
            'end_time': first.end_time,
            'target_temperature': first.target_temperature,
            'priority': first.priority,
        }

        # Pre-select zones (works)
        kwargs['initial_zones'] = list(
            self.schedules.values_list('zone_id', flat=True).distinct()
        )

        # Pre-select days (must be strings for MultipleChoiceField)
        kwargs['initial_days'] = [
            str(d) for d in self.schedules.values_list('day_of_week', flat=True).distinct()
        ]

        return kwargs


    def form_valid(self, form):
        cleaned = form.cleaned_data

        for sched in self.schedules:
            sched.start_time = cleaned['start_time']
            sched.end_time = cleaned['end_time']
            sched.target_temperature = cleaned['target_temperature']
            sched.priority = cleaned['priority']
            sched.save()

        return redirect('controller:grouped_schedule_list')

class GroupedScheduleDeleteView(View):
    def post(self, request, schedule_ids, *args, **kwargs):
        ids = schedule_ids.split(',')
        schedules = get_list_or_404(Schedule, id__in=ids)
        for sched in schedules:
            sched.delete()
        return redirect('controller:grouped_schedule_list')