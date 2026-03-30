from django.urls import path
from .views import upload_reports_db, aggregated_production_report_view

urlpatterns = [
    path("", upload_reports_db, name="upload_reports"),
    path("production-reports/", aggregated_production_report_view, name='production_report_list'
    ),
]
