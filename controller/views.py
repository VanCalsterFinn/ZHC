from django.shortcuts import redirect, render
from django.views import View
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
        zones = Zone.objects.prefetch_related("manual_override")
        overrides = ManualOverride.objects.filter(active=True)
        context.update({
            "zones": zones,
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

        override, created = ManualOverride.objects.get_or_create(
            zone=zone,
            defaults={"target_temperature": zone.target_temperature, "active": True}
        )

        override.target_temperature += delta
        override.target_temperature = max(5, min(30, override.target_temperature))
        override.active = True
        override.save()

        return redirect("controller:dashboard")    

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
        # Get active manual overrides for easy access in the template if needed
        overrides = ManualOverride.objects.filter(active=True)
        context.update({
            "overrides": {o.zone.id: o for o in overrides},
            "page_title": "Manage Zones",
            "breadcrumbs": [
                {"name": "Home", "url": "/", "active": False},
                {"name": "Zones", "url": "/zones/", "active": False},
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
        # Get active manual overrides for easy access in the template if needed
        overrides = ManualOverride.objects.filter(active=True)
        context.update({
            "overrides": {o.zone.id: o for o in overrides},
            "page_title": "Manage Zones",
            "breadcrumbs": [
                {"name": "Home", "url": "/", "active": False},
                {"name": "Zones", "url": "/zones/", "active": False},
                {"name": "Update", "url": None, "active": True},
            ]
        })
        return context
    
class ZoneDeleteView(DeleteView):
    model = Zone
    template_name = "controller/partials/_zone_confirm_delete.html"
    success_url = reverse_lazy("zone-list")

class ScheduleListView(ListView):
    model = Schedule
    template_name = "controller/schedules.html"
    context_object_name = "schedules"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        zones = Zone.objects.all()
        context.update({
            "page_title": "Schedules",
            "zones": zones,
            "form": ScheduleForm(),
            "breadcrumbs": [
                {"name": "Home", "url": "/", "active": False},
                {"name": "Schedules", "url": "/schedules/", "active": True},
            ]
        })
        return context


class ScheduleCreateView(CreateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = "controller/partials/_schedule_form.html"
    success_url = "/schedules/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get active manual overrides for easy access in the template if needed
        overrides = ManualOverride.objects.filter(active=True)
        context.update({
            "overrides": {o.zone.id: o for o in overrides},
            "page_title": "Manage Zones",
            "breadcrumbs": [
                {"name": "Home", "url": "/", "active": False},
                {"name": "Schedules", "url": "/schedules/", "active": False},
                {"name": "Create", "url": None, "active": True},
            ]
        })
        return context

class ScheduleUpdateView(UpdateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = "controller/partials/_schedule_form.html"
    success_url = "/schedules/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get active manual overrides for easy access in the template if needed
        overrides = ManualOverride.objects.filter(active=True)
        context.update({
            "overrides": {o.zone.id: o for o in overrides},
            "page_title": "Manage Zones",
            "breadcrumbs": [
                {"name": "Home", "url": "/", "active": False},
                {"name": "Schedules", "url": "/schedules/", "active": False},
                {"name": "Update", "url": None, "active": True},
            ]
        })
        return context

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
