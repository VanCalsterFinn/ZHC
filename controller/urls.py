from django.urls import path, include
from .views import (
    DashboardView, ScheduleDeleteView, ZoneDeleteView, ZoneListView, ScheduleListView,
    ScheduleCreateView, ScheduleUpdateView,
    ManualOverrideListView, ManualOverrideCreateView,
    ManualOverrideUpdateView, ZoneCreateView, ZoneUpdateView
)

app_name = "controller"

urlpatterns = [
    # Frontend
    path('', DashboardView.as_view(), name='dashboard'),

    path("zones/", ZoneListView.as_view(), name="zone-list"),
    path("zones/add/", ZoneCreateView.as_view(), name="zone-add"),
    path("zones/<int:pk>/edit/", ZoneUpdateView.as_view(), name="zone-edit"),
    path("zones/<int:pk>/delete/", ZoneDeleteView.as_view(), name="zone-delete"),

    path('schedules/', ScheduleListView.as_view(), name='schedule_list'),
    path('schedules/new/', ScheduleCreateView.as_view(), name='schedule_create'),
    path('schedules/edit/<int:pk>/',
         ScheduleUpdateView.as_view(), name='schedule_update'),
    path('schedules/delete/<int:pk>/',
         ScheduleDeleteView.as_view(), name='schedule_delete'),


    path('manual_override/', ManualOverrideListView.as_view(),
         name='manual_override'),
    path('manual_override/new/', ManualOverrideCreateView.as_view(),
         name='manual_override_create'),
    path('manual_override/edit/<int:pk>/',
         ManualOverrideUpdateView.as_view(), name='manual_override_update'),
]
