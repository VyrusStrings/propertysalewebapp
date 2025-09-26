from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from .forms import LeadForm
from .models import Lead
from properties.models import Property
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
import csv

def staff_required(user): return user.is_staff

def lead_create(request):
    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("leads:thank_you")
    else:
        initial = {}
        name = request.GET.get("name")
        phone = request.GET.get("phone")
        if name:  initial["full_name"] = name
        if phone: initial["phone"] = phone
        form = LeadForm(initial=initial)

    return render(request, "leads/lead_form.html", {"form": form})


def lead_create_for_property(request, slug):
    """
    Inline sidebar form on the property detail page.
    """
    prop = get_object_or_404(Property, slug=slug)
    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.save()
            return redirect("pages:thank_you")
    else:
        form = LeadForm()
    return render(request, "properties/detail.html", {"property": prop, "form": form})


def thank_you(request):
    return redirect("pages:thank_you")


def _notify_sales(lead):
    send_mail(
        subject=f"New Lead: {lead.full_name} ({lead.phone})",
        message=f"Email: {lead.email}\nCountry: {lead.country}\nBudget: {lead.budget_min}-{lead.budget_max}\nTimeline: {lead.timeline}\nMessage:\n{lead.message}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.SALES_INBOX],
    )

@login_required
def staff_leads(request):
    qs = Lead.objects.select_related("property").all()
    return render(request, "leads/staff_list.html", {"leads": qs})

@login_required
def staff_leads_export_csv(request):
    qs = Lead.objects.select_related("property").all()
    resp = HttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = 'attachment; filename="leads.csv"'
    w = csv.writer(resp)
    w.writerow(["created_at","full_name","phone","email","country","budget_min","budget_max","timeline","status","property","utm_source","utm_campaign","source_url"])
    for l in qs:
        w.writerow([
            l.created_at, l.full_name, l.phone, l.email, l.country,
            l.budget_min, l.budget_max, l.timeline, l.status,
            getattr(l.property, "title", ""),
            getattr(l, "utm_source", ""), getattr(l, "utm_campaign", ""), getattr(l, "source_url", "")
        ])
    return resp


@login_required
@user_passes_test(staff_required)
def lead_set_status(request, pk):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    lead = get_object_or_404(Lead, pk=pk)
    status = (request.POST.get("status") or "").lower()
    if status not in ("new", "contacted"):
        return HttpResponseBadRequest("Invalid status")
    lead.status = status
    lead.save(update_fields=["status"])
    return redirect(request.META.get("HTTP_REFERER") or "dashboard")

@login_required
@user_passes_test(staff_required)
def lead_delete(request, pk):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    lead = get_object_or_404(Lead, pk=pk)
    lead.delete()
    return redirect(request.META.get("HTTP_REFERER") or "dashboard")