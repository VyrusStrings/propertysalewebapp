from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "properties"

urlpatterns = [
    # public
    path("", views.property_list, name="list"),

    # alias BEFORE the slug route:
    path("add/", RedirectView.as_view(pattern_name="properties:staff_add", permanent=False)),

    # staff (keep these before the slug route)
    path("staff/add/", views.staff_property_add, name="staff_add"),
    path("staff/manage/", views.staff_property_manage, name="staff_manage"),
    path("staff/<int:pk>/edit/", views.staff_property_edit, name="staff_edit"),
    path("staff/<int:pk>/delete/", views.staff_property_delete, name="staff_delete"),

    # slug catch-all LAST
    path("<slug:slug>/", views.property_detail, name="detail"),
]
