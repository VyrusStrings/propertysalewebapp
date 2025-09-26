from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from django_countries import countries
from .models import Lead

EXTRA_COUNTRIES = [("TRNC", "Turkish Republic of Northern Cyprus")]

class LeadForm(ModelForm):
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput)

    REMOTE_CHOICES = (("yes", _("Yes")), ("no", _("No")))
    remote_choice = forms.TypedChoiceField(
        label=_("Do you want to buy it remotely?"),
        choices=REMOTE_CHOICES,
        coerce=lambda v: True if v == "yes" else False,
        widget=forms.RadioSelect,
        required=True,
    )

    visit_date = forms.DateField(
        label=_("Choose the date that you are planning to come to Cyprus"),
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    country = forms.ChoiceField(
        choices=[("", "Select country")] + EXTRA_COUNTRIES + list(countries),
        widget=forms.Select(attrs={
            "id": "id_country",
            "class": "django-countries-select",
        }),
        required=False,
    )

    class Meta:
        model = Lead
        fields = [
            "full_name", "phone", "email", "country",
            "budget_min", "budget_max",
            "message", "consent", "property",
            "remote_purchase", "visit_date",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "John Doe"}),
            "phone": forms.TextInput(attrs={"placeholder": "+90 5xx xxx xx xx (WhatsApp)"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "budget_min": forms.NumberInput(attrs={"placeholder": "e.g., 50,000"}),
            "budget_max": forms.NumberInput(attrs={"placeholder": "e.g., 250,000"}),
            "message": forms.Textarea(attrs={"placeholder": "Anything specific you’re looking for?"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_class = "input"
        placeholders = {
            "full_name": "John Doe",
            "phone": "+90 5xx xxx xx xx",
            "email": "name@example.com",
            "country": "Select your country",
            "budget_min": "e.g., 90000",
            "budget_max": "e.g., 250000",
            "message": "Tell us what you’re looking for (location, bedrooms, sea view, etc.)",
        }
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", base_class)
            if name in placeholders:
                field.widget.attrs.setdefault("placeholder", placeholders[name])

    def clean(self):
        cleaned = super().clean()
        remote = cleaned.get("remote_choice")
        date = cleaned.get("visit_date")
        if remote is False and not date:
            self.add_error("visit_date", _("Please choose a date if you are not buying remotely."))
            
        cleaned["remote_purchase"] = remote
        return cleaned
