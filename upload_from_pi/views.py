from .data_handler import GeneralProductionHandler, InnovationProductionHandler, download_from_pi, print_missing_columns_df
from .models import ProductionReport, Innovation
from django.http import HttpResponse
import time

# Create your views here.
def upload_reports_db(request):
    data_from_date = "2025-06-01"
    data_to_date = "2025-06-02"
    report_name = "production_report"
    plant_id = "MAIN41"

    report_from_pi4 = download_from_pi(report_name, plant_id, data_from_date, data_to_date)

    # production report general
    production_report_gen = GeneralProductionHandler("General")
    missing_columns_general = production_report_gen.execute(report_from_pi4, ProductionReport)
    print_missing_columns_df(missing_columns_general, "Production_report_general")
    time.sleep(10)

    # Innovation report
    innovation_report = InnovationProductionHandler("Innovations")
    missing_columns_innovation = innovation_report.execute(report_from_pi4, Innovation)
    print_missing_columns_df(missing_columns_innovation, "Innovation")
    
    return HttpResponse("Hello! Am there....")
