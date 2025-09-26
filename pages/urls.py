from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("privacy/", views.privacy, name="privacy"),
    path("thank-you/", views.thank_you, name="thank_you"),
    path("services/", views.services, name="services"),
    path("tour/", views.tour, name="tour"),
    path("contacts/", views.contacts, name="contacts"),
]
