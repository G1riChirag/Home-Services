
from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["name", "age", "language", "citizenship", "covid_vaccinated", "consent_marketing","consent_healthdata","address"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "age": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "language": forms.TextInput(attrs={"class": "form-control"}),
            "citizenship": forms.TextInput(attrs={"class": "form-control"}),
            "covid_vaccinated": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "consent_marketing": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "consent_healthdata": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

        def save(self, commit=True):
            obj = super().save(commit=False)
            # bump timestamp whenever user changes either consent
            if {"consent_marketing","consent_healthdata"} & set(self.changed_data):
                obj.set_consents(self.cleaned_data["consent_marketing"], self.cleaned_data["consent_healthdata"])
            if commit:
                obj.save()
            return obj
