from django import forms
from .models import Schedule, ManualOverride, Zone

# Add Bootstrap classes using widget


class ScheduleForm(forms.ModelForm):
    # Multiple zones
    zones = forms.ModelMultipleChoiceField(
        queryset=Zone.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select select2',
            'required': True,
        })
    )

    # Multiple days
    days_of_week = forms.MultipleChoiceField(
        choices=[
            (0, "Monday"),
            (1, "Tuesday"),
            (2, "Wednesday"),
            (3, "Thursday"),
            (4, "Friday"),
            (5, "Saturday"),
            (6, "Sunday"),
        ],
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select select2',
            'required': True,
        })
    )

    class Meta:
        model = Schedule
        # REMOVE 'zone' and 'day_of_week' here, because we handle them manually
        fields = ['start_time', 'end_time', 'target_temperature', 'priority']
        widgets = {
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'required': True}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'required': True}),
            'target_temperature': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'required': True}),
            'priority': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        initial_zone = kwargs.pop('initial_zone', None)
        initial_days = kwargs.pop('initial_days', None)
        super().__init__(*args, **kwargs)

        # Pre-select zones
        if initial_zone:
            self.fields['zones'].initial = Zone.objects.filter(pk=initial_zone)
        elif self.instance.pk:
            self.fields['zones'].initial = [self.instance.zone]

        # Pre-select days
        if initial_days:
            self.fields['days_of_week'].initial = initial_days
        elif self.instance.pk:
            # When editing, select the existing day
            self.fields['days_of_week'].initial = [
                self.instance.day_of_week]

    def save(self, commit=True):
        zones = self.cleaned_data.pop('zones')
        days = self.cleaned_data.pop('days_of_week')
        instance = super().save(commit=False)

        if commit:
            for zone in zones:
                for day in days:
                    Schedule.objects.create(
                        zone=zone,
                        day_of_week=day,
                        start_time=instance.start_time,
                        end_time=instance.end_time,
                        target_temperature=instance.target_temperature,
                        priority=instance.priority
                    )
        return instance


class ManualOverrideForm(forms.ModelForm):
    class Meta:
        model = ManualOverride
        fields = ['zone', 'target_temperature']
        widgets = {
            'zone': forms.Select(attrs={'class': 'form-select'}),
            'target_temperature': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
            }),
        }


class ZoneForm(forms.ModelForm):
    class Meta:
        model = Zone
        fields = ["name", "pin"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Zone Name"}),
            "pin": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Arduino Pin"}),
        }


class ScheduleBatchForm(forms.ModelForm):
    zones = forms.ModelMultipleChoiceField(
        queryset=Zone.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select select2',
            'required': True,
        })
    )

    days_of_week = forms.MultipleChoiceField(
        choices=[
            (0, "Monday"),
            (1, "Tuesday"),
            (2, "Wednesday"),
            (3, "Thursday"),
            (4, "Friday"),
            (5, "Saturday"),
            (6, "Sunday"),
        ],
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select select2',
            'required': True,
        })
    )

    class Meta:
        model = Schedule
        fields = ['start_time', 'end_time', 'target_temperature', 'priority']
        widgets = {
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'target_temperature': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'priority': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        initial_zones = kwargs.pop('initial_zones', None)
        initial_days = kwargs.pop('initial_days', None)
        super().__init__(*args, **kwargs)

        if initial_zones is not None:
            self.fields['zones'].initial = initial_zones  # IDs are fine

        if initial_days is not None:
            # must be ints, not str
            self.fields['days_of_week'].initial = initial_days
