from django.urls import path, include
from .views import (
    DashboardView, OverrideAdjustView, ScheduleDeleteView, ZoneDeleteView, ZoneListView, ScheduleListView,
    ScheduleCreateView, ScheduleUpdateView,
    ManualOverrideListView, ManualOverrideCreateView,
    ManualOverrideUpdateView, ZoneCreateView, ZoneUpdateView
)

app_name = "controller"

urlpatterns = [
    # Frontend
    path('', DashboardView.as_view(), name='dashboard'),
    path("overrides/adjust/", OverrideAdjustView.as_view(), name="override_adjust"),


    path("zones/", ZoneListView.as_view(), name="zone-list"),
    path("zones/new/", ZoneCreateView.as_view(), name="zone-create"),
    path("zones/edit/<int:pk>/", ZoneUpdateView.as_view(), name="zone-update"),
    path("zones/delete/<int:pk>/", ZoneDeleteView.as_view(), name="zone-delete"),

    path('schedules/', ScheduleListView.as_view(), name='schedule_list'),
    path('schedules/new/', ScheduleCreateView.as_view(), name='schedule_create'),
    path('schedules/edit/<int:pk>/', ScheduleUpdateView.as_view(), name='schedule_update'),
    path('schedules/delete/<int:pk>/', ScheduleDeleteView.as_view(), name='schedule_delete'),
]
