from django.urls import path

from apps.site_content.api.views import AboutPageContentAdminView


urlpatterns = [path("about/", AboutPageContentAdminView.as_view(), name="about-content-admin")]
