from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from django.db.models.functions import TruncDate
from leads.models import Lead
from properties.models import Property


def services(request):
    return render(request, "pages/services.html")


def tour(request):
    return render(request, "pages/tour.html")


def contacts(request):
    return render(request, "pages/contacts.html")


def home(request):
    return render(request, "pages/home.html")


def about(request):
    return render(request, "pages/about.html")


def privacy(request):
    return render(request, "pages/privacy.html")


def thank_you(request):
    return render(request, "pages/thank_you.html")


@login_required
def dashboard(request):
    now = timezone.now()
    start_14 = (now - timedelta(days=13)).date()  # inclusive window of 14 days

    # Totals
    total_leads = Lead.objects.count()
    total_properties = Property.objects.count()

    # This week / month
    start_week = (now - timedelta(days=now.weekday())).date()  # Monday
    start_month = now.date().replace(day=1)
    leads_this_week = Lead.objects.filter(created_at__date__gte=start_week).count()
    leads_this_month = Lead.objects.filter(created_at__date__gte=start_month).count()

    # Leads by day (last 14 days)
    by_day_qs = list(
        Lead.objects.filter(created_at__date__gte=start_14)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(c=Count("id"))
        .order_by("day")
    )
    labels, data = [], []
    for i in range(14):
        d = start_14 + timedelta(days=i)
        labels.append(d.strftime("%b %d"))  # e.g., "Aug 19"
        found = next((row["c"] for row in by_day_qs if row["day"] == d), 0)
        data.append(found)

    # Top countries
    countries_qs = list(
        Lead.objects.values("country")
        .annotate(c=Count("id"))
        .order_by("-c")[:10]
    )
    countries_labels = [(row["country"] or "—") for row in countries_qs]
    countries_data = [row["c"] for row in countries_qs]

    # ---- Replaced timeline with status distribution (timeline field doesn't exist) ----
    status_qs = list(
        Lead.objects.values("status")
        .annotate(c=Count("id"))
        .order_by("-c")
    )
    # Keep the same context keys so templates don't need changes:
    timeline_labels = [(row["status"] or "—") for row in status_qs]
    timeline_data = [row["c"] for row in status_qs]

    # Recent leads
    recent_leads = (
        Lead.objects.select_related("property")
        .order_by("-created_at")[:10]
    )

    context = {
        "kpis": {
            "total_leads": total_leads,
            "total_properties": total_properties,
            "leads_this_week": leads_this_week,
            "leads_this_month": leads_this_month,
        },
        "chart": {
            "by_day": {"labels": labels, "data": data},
            "countries": {"labels": countries_labels, "data": countries_data},
            # populated from status distribution to avoid template changes
            "timeline": {"labels": timeline_labels, "data": timeline_data},
        },
        "recent_leads": recent_leads,
    }
    return render(request, "staff/dashboard.html", context)
