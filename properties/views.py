from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Property
from .forms import PropertyForm
from leads.forms import LeadForm


def property_list(request):
    qs = Property.objects.all().order_by("-created_at")
    city = request.GET.get("city")
    minp = request.GET.get("min")
    maxp = request.GET.get("max")
    beds = request.GET.get("beds")
    if city:
        qs = qs.filter(city__iexact=city)
    if minp:
        qs = qs.filter(price__gte=minp)
    if maxp:
        qs = qs.filter(price__lte=maxp)
    if beds:
        qs = qs.filter(bedrooms__gte=beds)
    return render(request, "properties/list.html", {"properties": qs})


def _collect_property_images(prop):
    """
    Return an ordered list of image URLs for a property:
    - cover first (if available)
    - then related images from common reverse managers (images/photos/gallery)
    - skips duplicates and missing files gracefully
    - respects common ordering fields if present: position/order/sort
    """
    urls = []
    seen = set()

    # 1) Cover first
    cover_url = None
    try:
        if getattr(prop, "cover", None) and prop.cover and prop.cover.url:
            cover_url = prop.cover.url
    except Exception:
        cover_url = None

    if cover_url:
        urls.append(cover_url)
        seen.add(cover_url)

    # 2) Find a related manager
    related_mgr = None
    for rel_name in ("images", "photos", "gallery"):
        mgr = getattr(prop, rel_name, None)
        if hasattr(mgr, "all"):
            related_mgr = mgr
            break

    if not related_mgr:
        return urls

    # 3) Respect natural ordering if the related model exposes a typical order field
    qs = related_mgr.all()
    # Try common ordering fields; fall back to natural model order
    for order_field in ("position", "order", "sort"):
        # Only apply if the field exists on the related model
        model_cls = qs.model
        if hasattr(model_cls, order_field):
            qs = qs.order_by(order_field)
            break

    # 4) Extract file field from each related object
    for obj in qs:
        file_url = None
        for f_name in ("image", "photo", "file"):
            f = getattr(obj, f_name, None)
            if f:
                try:
                    if f.url:
                        file_url = f.url
                        break
                except Exception:
                    pass
        if file_url and file_url not in seen:
            seen.add(file_url)
            urls.append(file_url)

    return urls


def property_detail(request, slug):
    prop = get_object_or_404(Property, slug=slug)
    images = _collect_property_images(prop)

    ctx = {
        "property": prop,
        "form": LeadForm(),
        "images": images,
    }
    return render(request, "properties/detail.html", ctx)


@login_required
def staff_property_add(request):
    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("properties:staff_manage")
    else:
        form = PropertyForm()
    return render(request, "properties/staff_add.html", {"form": form})


@login_required
def staff_property_manage(request):
    qs = Property.objects.all().order_by("-created_at")
    return render(request, "properties/staff_manage.html", {"properties": qs})


@login_required
def staff_property_delete(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    if request.method == "POST":
        prop.delete()
        return redirect("properties:staff_manage")
    return redirect("properties:staff_manage")


@login_required
def staff_property_edit(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES, instance=prop)
        if form.is_valid():
            form.save()
            return redirect("properties:staff_manage")
    else:
        form = PropertyForm(instance=prop)
    return render(
        request,
        "properties/staff_add.html",
        {"form": form, "edit": True, "prop": prop},
    )
