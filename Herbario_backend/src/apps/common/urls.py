from django.urls import path

from apps.common.api.views import HealthCheckView, PublicFilterOptionsView
from apps.common.api.views.stats_view import HerbariumStatsView

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("stats/", HerbariumStatsView.as_view(), name="herbarium-stats"),
    path("filter-options/", PublicFilterOptionsView.as_view(), name="public-filter-options"),
]
