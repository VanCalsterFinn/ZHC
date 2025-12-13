from django.urls import path
from .views import CustomLoginView, CustomLogoutView, RegisterView, SettingsView, UpdateSettingsView

app_name = 'core'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(next_page='/'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('settings/', SettingsView.as_view(), name='settings'),
    path('settings/update/', UpdateSettingsView.as_view(), name='update_settings'),
]
