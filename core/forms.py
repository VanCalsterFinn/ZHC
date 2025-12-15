from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import SystemSettings


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'class': 'form-control'}))
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class SystemSettingsForm(forms.ModelForm):
    class Meta:
        model = SystemSettings
        fields = ["mode", "eco_temperature"]
        widgets = {
            "mode": forms.RadioSelect,
            'eco_temperature': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '5', 'max': '20'}),
        }
        
    def clean_eco_temperature(self):
        value = self.cleaned_data["eco_temperature"]
        if not (5 <= value <= 20):
            raise forms.ValidationError("Eco temperature must be between 5°C and 20°C.")
        return value