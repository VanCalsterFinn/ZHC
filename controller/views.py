from collections import defaultdict
from django.http import Http404
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, FormView
from django.urls import reverse_lazy
from django.utils import timezone

from core.models import SystemSettings
from .models import Zone, Schedule, ManualOverride
from .forms import ScheduleBatchForm, ScheduleForm, ManualOverrideForm, ZoneForm
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from django.db import transaction
from django.http import Http404

MAX_TEMP = 30.0
MIN_TEMP = 5.0   # optional, but recommended


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
            next_manual = ManualOverride.objects.filter(
                zone=zone, active_from__gt=now).order_by('active_from').first()

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


@method_decorator(csrf_exempt, name='dispatch')
class OverrideAdjustView(View):
    """
    Handles AJAX adjustment of zone manual override temperatures (+/-).
    """

    def post(self, request, *args, **kwargs):
        zone_id = request.POST.get("zone")

        try:
            delta = float(request.POST.get("delta", 0))
        except (TypeError, ValueError):
            return JsonResponse({"success": False, "error": "Invalid delta"})

        try:
            zone = Zone.objects.get(id=zone_id)
        except Zone.DoesNotExist:
            return JsonResponse({"success": False, "error": "Zone not found"})

        now = timezone.now()

        # Get active override if exists
        override = ManualOverride.objects.filter(
            zone=zone,
            active_from__lte=now
        ).filter(
            Q(active_until__gte=now) | Q(active_until__isnull=True)
        ).first()

        if override:
            new_target = override.target_temperature + delta
        else:
            new_target = zone.get_active_target + delta

        # Clamp temperature
        new_target = max(MIN_TEMP, min(MAX_TEMP, new_target))

        if override:
            override.target_temperature = new_target
            override.active_from = now
            override.save()
        else:
            override = ManualOverride.objects.create(
                zone=zone,
                target_temperature=new_target,
                active_from=now
            )

        return JsonResponse({
            "success": True,
            "new_target": round(new_target, 1),
            "zone": zone.id,
            "clamped": new_target in (MIN_TEMP, MAX_TEMP)
        })


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
                {"name": "Zones", "url": reverse_lazy(
                    "zone-list"), "active": False},
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
                {"name": "Zones", "url": reverse_lazy(
                    "zone-list"), "active": False},
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
        return Schedule.objects.filter(zone_id=zone_id).order_by('day_of_week', 'start_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        zone_id = self.kwargs['zone_id']
        zone = Zone.objects.get(id=zone_id)
        system_settings = SystemSettings.objects.first()
        context.update({
            "zone": zone,
            "eco_temperature": system_settings.eco_temperature if system_settings else 20,
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

    def get_queryset(self):
        # Sort all schedules by day_of_week first, then start_time
        return Schedule.objects.all().order_by('day_of_week', 'start_time')

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
                {"name": "Schedules", "url": reverse_lazy(
                    'controller:schedule_list'), "active": False},
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
                {"name": "Schedules", "url": reverse_lazy(
                    'controller:schedule_list'), "active": False},
                {"name": "Update", "url": None, "active": True},
            ]
        })
        return context

    def get_form_kwargs(self):
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
        grouped = defaultdict(
            lambda: {'zones': set(), 'days': set(), 'schedules': []})
        for sched in schedules:
            key = (sched.start_time, sched.end_time,
                   sched.target_temperature, sched.priority)
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
                {"name": "Schedules", "url": reverse_lazy(
                    'controller:schedule_list'), "active": False},
                {"name": "Grouped Schedules", "url": None, "active": True},
            ]
        })
        return context


class GroupedScheduleBulkEditView(FormView):
    template_name = "controller/partials/_grouped_schedules_form.html"
    form_class = ScheduleBatchForm

    def dispatch(self, request, *args, **kwargs):
        self.schedule_ids = self.kwargs.get("schedule_ids", "").split(",")
        self.schedules = Schedule.objects.filter(id__in=self.schedule_ids)

        if not self.schedules.exists():
            raise Http404("No schedules found.")

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        first = self.schedules.first()

        kwargs["initial"] = {
            "start_time": first.start_time,
            "end_time": first.end_time,
            "target_temperature": first.target_temperature,
            "priority": first.priority,
        }

        # Pre-select zones
        kwargs["initial_zones"] = list(
            self.schedules.values_list("zone_id", flat=True).distinct()
        )

        # Pre-select days as strings
        kwargs["initial_days"] = list(
            self.schedules.values_list("day_of_week", flat=True).distinct()
        )

        return kwargs

    @transaction.atomic
    def form_valid(self, form):
        cleaned = form.cleaned_data
        selected_zones = cleaned["zones"]
        selected_days = [int(d) for d in cleaned["days_of_week"]]
        start_time = cleaned["start_time"]
        end_time = cleaned["end_time"]
        target_temperature = cleaned["target_temperature"]
        priority = cleaned["priority"]

        # Build sets for comparison
        original_keys = {
            (s.zone_id, s.day_of_week): s
            for s in self.schedules
        }
        submitted_keys = {
            (zone.id, day) for zone in selected_zones for day in selected_days
        }

        # 1. Update existing schedules that are still selected
        for key in submitted_keys & original_keys.keys():
            sched = original_keys[key]
            sched.start_time = start_time
            sched.end_time = end_time
            sched.target_temperature = target_temperature
            sched.priority = priority
            sched.save()

        # 2. Delete schedules that were removed
        for key in original_keys.keys() - submitted_keys:
            original_keys[key].delete()

        # 3. Create new schedules for newly added zone/day combos
        for key in submitted_keys - original_keys.keys():
            zone_id, day = key
            Schedule.objects.create(
                zone_id=zone_id,
                day_of_week=day,
                start_time=start_time,
                end_time=end_time,
                target_temperature=target_temperature,
                priority=priority
            )

        return redirect("controller:grouped_schedule_list")


class GroupedScheduleDeleteView(View):
    def post(self, request, schedule_ids, *args, **kwargs):
        ids = schedule_ids.split(',')
        schedules = get_list_or_404(Schedule, id__in=ids)
        for sched in schedules:
            sched.delete()
        return redirect('controller:grouped_schedule_list')


class ZoneScheduleGraphView(TemplateView):
    template_name = "controller/zone_schedules/zone_schedules_graph.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        zone_id = kwargs.get('zone_id')
        zone = get_object_or_404(Zone, id=zone_id)
        context['zone'] = zone
        # optional: eco temperature
        context['eco_temperature'] = 18
        return context
