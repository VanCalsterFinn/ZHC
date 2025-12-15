from django import forms
from django.db import models

class SystemSettings(models.Model):
    MODE_CHOICES = [
        ("auto", "Automatic"),
        ("manual", "Manual"),
    ]

    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default="auto")
    eco_temperature = models.FloatField(default=16.0)  # fallback temperature

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"System Settings ({self.mode})"

    class Meta:
        verbose_name = "System Setting"
        verbose_name_plural = "System Settings"

    def clean(self):
        if not (5 <= self.eco_temperature <= 20):
            raise forms.ValidationError({
                "eco_temperature": "Eco temperature must be between 5°C and 20°C."
            })