from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from pages import views as page_views
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("rosetta/", include("rosetta.urls")),
]

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("staff/login/",  auth_views.LoginView.as_view(template_name="staff/login.html"), name="staff_login"),
    path("staff/logout/", auth_views.LogoutView.as_view(next_page="/"), name="staff_logout"),
    path("dashboard/", page_views.dashboard, name="dashboard"),
    path("", include(("pages.urls","pages"), namespace="pages")),
    path("properties/", include(("properties.urls","properties"), namespace="properties")),
    path("leads/", include(("leads.urls","leads"), namespace="leads")),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
