from django.urls import path
from .views import upload_reports_db

urlpatterns = [
    path("", upload_reports_db, name="upload_reports")
]
