from django import forms
from .models import Booking, Review

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            "type", "preferred_date", "duration_hours",
            "package", "service", "address", "notes",
            "quoted_price_cents",
        ]
        widgets = {
            "type": forms.Select(attrs={"class": "form-select"}),
            "preferred_date": forms.DateInput(attrs={"type":"date","class":"form-control"}),
            "duration_hours": forms.NumberInput(attrs={"class":"form-control","min":"0","step":"0.5"}),
            "package": forms.Select(attrs={"class":"form-select"}),
            "service": forms.Select(attrs={"class":"form-select"}),
            "address": forms.TextInput(attrs={"class":"form-control","placeholder":"123 Example St, Suburb"}),
            "notes": forms.Textarea(attrs={"class":"form-control","rows":3}),
            "quoted_price_cents": forms.NumberInput(attrs={"class":"form-control","min":"0","step":"50"}),
        }

    def clean(self):
        cleaned = super().clean()

        # If user didn’t provide a quote, auto-fill from package or service:
        q = cleaned.get("quoted_price_cents")
        pkg = cleaned.get("package")
        svc = cleaned.get("service")

        if not q:
            if pkg and getattr(pkg, "price_cents", None):
                cleaned["quoted_price_cents"] = pkg.price_cents
            elif svc and getattr(svc, "base_price_cents", None):
                cleaned["quoted_price_cents"] = svc.base_price_cents

        return cleaned
    
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(choices=[(i, i) for i in range(1, 6)], attrs={"class": "form-select"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
