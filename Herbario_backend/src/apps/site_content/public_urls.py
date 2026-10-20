from django.urls import path

from apps.site_content.api.views import PublicAboutPageContentView


urlpatterns = [
    path("about/", PublicAboutPageContentView.as_view(), name="about-content-public"),
]
