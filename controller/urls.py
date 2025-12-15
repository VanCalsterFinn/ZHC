from django.urls import path
from .views import (
    DashboardView, OverrideAdjustView, ScheduleDeleteView, ZoneDeleteView, ZoneListView, ScheduleListView,
    ScheduleCreateView, ScheduleUpdateView,
    ZoneCreateView, ZoneUpdateView, ZoneScheduleListView, GroupedScheduleListView, GroupedScheduleBulkEditView, GroupedScheduleDeleteView
)

app_name = "controller"

urlpatterns = [
    # Frontend
    path('', DashboardView.as_view(), name='dashboard'),
    path("overrides/adjust/", OverrideAdjustView.as_view(), name="override_adjust"),


    path("zones/", ZoneListView.as_view(), name="zone-list"),
    path("zones/create/", ZoneCreateView.as_view(), name="zone-create"),
    path("zones/edit/<int:pk>/", ZoneUpdateView.as_view(), name="zone-update"),
    path("zones/delete/<int:pk>/", ZoneDeleteView.as_view(), name="zone-delete"),
    path('zones/<int:zone_id>/schedules/', ZoneScheduleListView.as_view(), name='zone_schedules'),
    
    path('schedules/grouped/', GroupedScheduleListView.as_view(), name='grouped_schedule_list'),
    path(
        "schedules/bulk-edit/<str:schedule_ids>/",
        GroupedScheduleBulkEditView.as_view(),
        name="grouped_schedule_bulk_edit"
    ),
    path('schedules/group-delete/<str:schedule_ids>/', GroupedScheduleDeleteView.as_view(), name='grouped_schedule_delete'),

    path('schedules/', ScheduleListView.as_view(), name='schedule_list'),
    path('schedules/create/', ScheduleCreateView.as_view(), name='schedule_create'),
    path('schedules/edit/<int:pk>/', ScheduleUpdateView.as_view(), name='schedule_update'),
    path('schedules/delete/<int:pk>/', ScheduleDeleteView.as_view(), name='schedule_delete'),
]
