from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Zone, Schedule, ManualOverride
from .forms import ScheduleForm, ManualOverrideForm, ZoneForm

# Dashboard: simple ListView of zones


class DashboardView(ListView):
    model = Zone
    template_name = "controller/dashboard.html"
    context_object_name = "zones"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get active overrides and make a dict for easy lookup
        overrides = ManualOverride.objects.filter(active=True)
        context['overrides'] = {o.zone.id: o for o in overrides}
        context['page_title'] = "Heating Dashboard"

        return context

# Zones


# List all zones
class ZoneListView(ListView):
    model = Zone
    template_name = "controller/zones.html"
    context_object_name = "zones"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get active manual overrides for easy access in the template if needed
        overrides = ManualOverride.objects.filter(active=True)
        context.update({
            "overrides": {o.zone.id: o for o in overrides},
            "page_title": "Manage Zones",
            "breadcrumbs": [
                {"name": "Dashboard", "url": "/dashboard/"},
                {"name": "Manage Zones", "url": "/zones/"},
            ]
        })
        return context


class ZoneCreateView(CreateView):
    model = Zone
    form_class = ZoneForm
    template_name = "controller/partials/_zone_form.html"
    success_url = reverse_lazy("controller:zone-list")


class ZoneUpdateView(UpdateView):
    model = Zone
    form_class = ZoneForm
    template_name = "controller/partials/_zone_form.html"
    success_url = reverse_lazy("controller:zone-list")


class ZoneDeleteView(DeleteView):
    model = Zone
    template_name = "controller/partials/_zone_confirm_delete.html"
    success_url = reverse_lazy("controller:zone-list")
# Schedules


class ScheduleListView(ListView):
    model = Schedule
    template_name = "controller/schedules.html"
    context_object_name = "schedules"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['zones'] = Zone.objects.all()
        context['page_title'] = "Schedules"
        context['schedule_days'] = Schedule.DAY_CHOICES
        context['form'] = ScheduleForm()
        return context


class ScheduleCreateView(CreateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = "controller/partials/_schedule_form.html"
    success_url = "/schedules/"


class ScheduleUpdateView(UpdateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = "controller/partials/_schedule_form.html"
    success_url = "/schedules/"


class ScheduleDeleteView(DeleteView):
    model = Schedule
    # can be inline in modal
    template_name = "controller/partials/_schedule_delete_confirm.html"
    success_url = reverse_lazy('controller:schedule_list')
# Manual Overrides


class ManualOverrideListView(ListView):
    model = ManualOverride
    template_name = "controller/manual_override.html"
    context_object_name = "overrides"


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
