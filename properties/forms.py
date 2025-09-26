from django import forms
from .models import Property

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            "title", "city", "price", "bedrooms", "bathrooms",
            "size_sqm", "summary", "description", "cover", "lat", "lng", "is_featured"
        ]
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 3}),
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault("style", "width:100%;padding:10px;border:1px solid #e6e9f0;border-radius:8px;")