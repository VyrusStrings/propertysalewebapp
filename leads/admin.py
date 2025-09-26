from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "created_at", "full_name", "phone", "country",
        "budget_min", "budget_max",
        "remote_purchase", "visit_date",   # replaced timeline
        "status", "property",
    )
    list_filter = (
        "status", "remote_purchase", "country", "created_at"  # replaced timeline
    )
    search_fields = ("full_name", "phone", "email", "country", "message")

    actions = ["export_as_csv"]

    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="leads.csv"'
        writer = csv.writer(response)
        writer.writerow([
            "created_at", "full_name", "phone", "email", "country",
            "budget_min", "budget_max",
            "remote_purchase", "visit_date",   # replaced timeline
            "status", "property",
        ])
        for l in queryset:
            writer.writerow([
                l.created_at.strftime("%Y-%m-%d %H:%M") if l.created_at else "",
                l.full_name,
                l.phone,
                l.email,
                l.country,
                l.budget_min,
                l.budget_max,
                "Yes" if l.remote_purchase is True else ("No" if l.remote_purchase is False else ""),
                l.visit_date.strftime("%Y-%m-%d") if l.visit_date else "",
                l.status,
                getattr(l.property, "title", ""),
            ])
        return response

    export_as_csv.short_description = "Export selected leads as CSV"
