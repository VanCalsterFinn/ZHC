from django import forms
from .models import Schedule, ManualOverride, Zone

# Add Bootstrap classes using widgets


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['zone', 'day_of_week', 'start_time',
                  'end_time', 'target_temperature']
        widgets = {
            'zone': forms.Select(attrs={'class': 'form-select'}),
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'target_temperature': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        }


class ManualOverrideForm(forms.ModelForm):
    class Meta:
        model = ManualOverride
        fields = ['zone', 'target_temperature', 'active']
        widgets = {
            'zone': forms.Select(attrs={'class': 'form-select'}),
            'target_temperature': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ZoneForm(forms.ModelForm):
    class Meta:
        model = Zone
        fields = ["name", "pin"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Zone Name"}),
            "pin": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Arduino Pin"}),
        }
