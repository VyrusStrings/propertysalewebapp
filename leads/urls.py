from django.urls import path
from . import views

app_name = "leads"

urlpatterns = [
    # public lead endpoints:
    path("contact/", views.lead_create, name="contact"),
    path("contact/<slug:slug>/", views.lead_create_for_property, name="create_for_property"),

    # staff:
    path("staff/", views.staff_leads, name="staff_list"),
    path("staff/export/csv/", views.staff_leads_export_csv, name="staff_export_csv"),
    path("<int:pk>/set-status/", views.lead_set_status, name="set_status"),
    path("<int:pk>/delete/", views.lead_delete, name="delete"),
]
