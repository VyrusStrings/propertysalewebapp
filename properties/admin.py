# properties/admin.py
from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea, NumberInput
from django.utils.html import format_html

from .models import Property

# Optional gallery model (only used if it exists)
try:
    from .models import PropertyImage
except Exception:
    PropertyImage = None


def _detect_feature_field():
    """
    Return the name of the boolean 'featured' field on Property if it exists.
    We auto-support either 'featured' or 'is_featured'. Otherwise return None.
    """
    try:
        names = {f.name for f in Property._meta.get_fields()}
        for candidate in ("featured", "is_featured"):
            if candidate in names:
                return candidate
    except Exception:
        pass
    return None


FEATURE_FIELD = _detect_feature_field()


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ("image", "alt", "order", "preview")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if getattr(obj, "image", None):
            try:
                return format_html(
                    '<img src="{}" style="height:70px;border-radius:6px;"/>', obj.image.url
                )
            except Exception:
                return ""
        return ""


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """
    Modernized Property admin that gracefully handles the presence/absence
    of a 'featured' boolean (supports 'featured' or 'is_featured').
    """
    # Base columns — we'll append the feature field dynamically
    list_display = ("title", "city", "price")
    list_filter = ("city",)
    search_fields = ("title", "city")

    # Nicer widgets
    formfield_overrides = {
        models.CharField:   {"widget": TextInput(attrs={"class": "w100"})},
        models.IntegerField:{"widget": NumberInput(attrs={"class": "w100"})},
        models.DecimalField:{"widget": NumberInput(attrs={"step": "0.01", "class": "w100"})},
        models.TextField:   {"widget": Textarea(attrs={"rows": 4, "class": "w100"})},
    }

    def get_list_display(self, request):
        cols = list(super().get_list_display(request))
        if FEATURE_FIELD and FEATURE_FIELD not in cols:
            cols.append(FEATURE_FIELD)
        return tuple(cols)

    def get_list_filter(self, request):
        filts = list(super().get_list_filter(request))
        if FEATURE_FIELD:
            # Must be a real field to be used as a filter
            filts.insert(0, FEATURE_FIELD)
        return tuple(filts)

    def get_fieldsets(self, request, obj=None):
        # Build Basics in 2-column rows; include feature toggle if present
        rows = [
            ("title", "city"),
            # price + optional feature toggle in same row
            tuple(["price"] + ([FEATURE_FIELD] if FEATURE_FIELD else [])),
            ("bedrooms", "bathrooms"),
            ("size_sqm",),
        ]
        fieldsets = (
            ("Basics", {
                "fields": tuple(rows),
                "classes": ("admin-card", "admin-grid-2"),
            }),
            ("Descriptions", {
                "fields": ("summary", "description"),
                "classes": ("admin-card",),
                "description": "Short teaser shown in cards and list pages.",
            }),
            ("Location", {
                "fields": (("lat", "lng"),),
                "classes": ("admin-card", "admin-grid-2"),
            }),
            ("Media", {
                "fields": ("cover",),
                "classes": ("admin-card",),
            }),
        )
        return fieldsets

    inlines = [PropertyImageInline] if PropertyImage else []

    class Media:
        css = {"all": ("admin/property_admin.css",)}
        js = ("admin/property_admin.js",)
