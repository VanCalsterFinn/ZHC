from django.urls import path
from .views import CustomLoginView, CustomLogoutView, RegisterView

app_name = 'core'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(next_page='/'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
]
