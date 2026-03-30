from django.shortcuts import render
from .data_handler import (
    GeneralProductionHandler,
    InnovationProductionHandler,
    BookWiseDetailsHandler,
    DowntimeHandler,
    WebBreakHandler,
    ReelConsumptionHandler,
    download_from_pi,
    print_missing_columns_df,
)
from .models import ProductionReport, Innovation, BookWiseDetails, Downtime, WebBreak, ReelConsumption
from handler_default_data.models import ScheduledTime
from django.http import HttpResponse
import time
from django.db.models import Subquery, OuterRef, Max, Count

# NEW: timezone utilities
from datetime import timedelta, datetime, date
from django.utils import timezone
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


# -----------------------------------------------------------------------------
# Optional data-loader view (unchanged)
# -----------------------------------------------------------------------------
def upload_reports_db(request):
    data_from_date = "2026-03-01"
    data_to_date = "2026-03-28"
    report_name = "production_report"

    plant_ids = [
        "ODBCAIR30", "ACTIVE42", "ODBCAIR32", "MAIN34", "MAIN38",
        "MAIN35", "MAIN40", "ODBCAIR28", "ACTIVE44", "MAIN36",
        "MAIN41", "ODBCAIR33", "ACTIVE43", "MAIN37"
    ]

    # plant_ids = [
    #     "ODBCAIR30", "ACTIVE42", "ODBCAIR32", "MAIN38",
    #     "MAIN35", "MAIN40", "ODBCAIR28", "ACTIVE44", "MAIN36",
    #     "ODBCAIR33", "ACTIVE43", "MAIN37"
    # ]

    for plant_id in plant_ids:
        print(f"Processing reports for plant: {plant_id} from {data_from_date} to {data_to_date}")
        report_from_pi4 = download_from_pi(report_name, plant_id, data_from_date, data_to_date)

        if report_from_pi4:
            production_report_gen = GeneralProductionHandler("General")
            missing_columns_general = production_report_gen.execute(report_from_pi4, ProductionReport)
            print_missing_columns_df(missing_columns_general, f"Production_report_general for {plant_id}")
            time.sleep(5)

            book_wise_handler = BookWiseDetailsHandler("Book Wise Details")
            missing_columns_bookwise = book_wise_handler.execute(report_from_pi4, BookWiseDetails)
            print_missing_columns_df(missing_columns_bookwise, f"BookWiseDetails for {plant_id}")
            time.sleep(5)

            innovation_report = InnovationProductionHandler("Innovations")
            missing_columns_innovation = innovation_report.execute(report_from_pi4, Innovation)
            print_missing_columns_df(missing_columns_innovation, f"Innovation for {plant_id}")
            time.sleep(5)

            downtime_handler = DowntimeHandler("Down Time")
            missing_columns_downtime = downtime_handler.execute(report_from_pi4, Downtime)
            print_missing_columns_df(missing_columns_downtime, f"Downtime for {plant_id}")
            time.sleep(5)

            web_break_handler = WebBreakHandler("Web Break")
            missing_columns_web_break = web_break_handler.execute(report_from_pi4, WebBreak)
            print_missing_columns_df(missing_columns_web_break, f"WebBreak for {plant_id}")
            time.sleep(5)

            reel_consumption_handler = ReelConsumptionHandler("Reel Consumption")
            missing_columns_reel_consumption = reel_consumption_handler.execute(report_from_pi4, ReelConsumption)
            print_missing_columns_df(missing_columns_reel_consumption, f"ReelConsumption for {plant_id}")
            time.sleep(5)
        else:
            print(f"Failed to download report for plant: {plant_id}")

    return HttpResponse("All reports for all plants processed successfully.")


# -----------------------------------------------------------------------------
# Helper: correct delay vs 04:00 IST (handles aware/naive datetimes)
# -----------------------------------------------------------------------------
def delay_vs_4am_ist(latest_end):
    """Return a tuple (delay_minutes, 'HH:MM') where delay is computed as
    max(0, latest_end_IST - 04:00 on the SAME IST calendar day).

    Notes:
    - If `latest_end` is naive, we assume it is in UTC and make it aware as UTC.
      If your DB actually stores naive IST, swap the make_aware line accordingly.
    - Requires Django's USE_TZ=True for best results.
    """
    if latest_end is None:
        return 0, "00:00"

    # Make aware if needed
    if timezone.is_naive(latest_end):
        # If DB stores naive UTC:
        latest_end = timezone.make_aware(latest_end, timezone=timezone.utc)
        # If instead DB stores naive IST, use:
        # latest_end = timezone.make_aware(latest_end, timezone=IST)

    # Convert to IST for correct calendar-day anchoring
    local_end = latest_end.astimezone(IST)

    # Build cutoff at 04:00 on SAME IST calendar day
    cutoff = local_end.replace(hour=4, minute=0, second=0, microsecond=0)

    if local_end <= cutoff:
        delta = timedelta(0)
    else:
        delta = local_end - cutoff

    minutes = int(delta.total_seconds() // 60)
    hh = minutes // 60
    mm = minutes % 60
    return minutes, f"{hh:02d}:{mm:02d}"


# -----------------------------------------------------------------------------
# Aggregated view (updated delay logic)
# -----------------------------------------------------------------------------
def aggregated_production_report_view(request):
    """
    Creates a single row per (plant_name, issue_date) with:
      - scheduled_lprs / scheduled_print_finish / planned_folders from ScheduledTime
      - latest_editorial_release from BookWiseDetails
      - latest_production_end (max)
      - actual_folders_run (sum of distinct folders' folders_count)
      - additional_folders_run (actual - planned)
      - uv_runs_count (count of unique desk values where UV='Yes')
      - delay vs 04:00 IST (this function FIXED)
    """

    # Subqueries for scheduled times
    scheduled_lprs_subquery = ScheduledTime.objects.filter(
        plant_name__iexact=OuterRef('plant_name'),
        is_active=True
    ).values('scheduled_lprs')[:1]

    scheduled_print_finish_subquery = ScheduledTime.objects.filter(
        plant_name__iexact=OuterRef('plant_name'),
        is_active=True
    ).values('scheduled_print_finish')[:1]

    planned_folders_subquery = ScheduledTime.objects.filter(
        plant_name__iexact=OuterRef('plant_name'),
        is_active=True
    ).values('planned_folders')[:1]

    # Latest editorial release for this plant/date (TOI city only)
    latest_editorial_release_subquery = BookWiseDetails.objects.filter(
        issueid__plant_name=OuterRef('plant_name'),
        issueid__issue_date=OuterRef('issue_date'),
        issueid__toi_city=True,
        editorial_release__isnull=False,
        reflong='No'
    ).order_by('-editorial_release').values('editorial_release')[:1]

    # UV runs count for this plant/date (TOI city only, specific desk values, UV='Yes')
    # Note: We'll calculate this in the loop since subqueries can't handle distinct counts easily

    # Aggregate base rows
    aggregated_reports = (
        ProductionReport.objects
        .filter(issue_date__month=7, toi_city=True)
        .values('plant_name', 'issue_date')
        .annotate(
            latest_production_end=Max('production_end'),
            scheduled_lprs=Subquery(scheduled_lprs_subquery),
            scheduled_print_finish=Subquery(scheduled_print_finish_subquery),
            planned_folders=Subquery(planned_folders_subquery),
            latest_editorial_release=Subquery(latest_editorial_release_subquery),
            total_reports_count=Count('issueid'),
        )
        .order_by('issue_date', 'plant_name')
    )

    # Build final list and compute additional_folders_run + delay
    final_reports = []
    for report in aggregated_reports:
        actual_folders_run = ProductionReportAggregationService.calculate_folder_count(
            report['plant_name'], report['issue_date']
        )

        # Calculate additional folders run beyond planned
        planned_folders = report['planned_folders'] or 0
        additional_folders_run = max(0, actual_folders_run - planned_folders)

        # Calculate UV runs count for this plant/date with desk normalization
        valid_desk_values = ['ET-MAIN', 'TOI', 'NBT', 'TOI-MAIN', 'ET', 'Mirror_MMCL', 'MT', 'TOI Sec-2']

        # Define desk normalization mapping (TOI-MAIN → TOI, ET-MAIN → ET)
        desk_mapping = {
            'TOI-MAIN': 'TOI',
            'ET-MAIN': 'ET'
        }

        # Get distinct desk values for UV='Yes' records
        uv_desk_values = BookWiseDetails.objects.filter(
            issueid__plant_name=report['plant_name'],
            issueid__issue_date=report['issue_date'],
            uv='Yes',
            desk__in=valid_desk_values
        ).values_list('desk', flat=True).distinct()

        # Normalize desk values and count unique ones
        normalized_desks = {desk_mapping.get(desk, desk) for desk in uv_desk_values}
        uv_runs_count = len(normalized_desks)

        # Calculate delay: production_end_ist - scheduled_print_finish_dt
        delay_minutes = 0
        
        if (report['scheduled_print_finish'] is not None and 
            report['latest_production_end'] is not None):
            
            # Convert datetime objects to IST for consistent comparison
            production_end_ist = report['latest_production_end'].astimezone(IST)
            
            # Convert time object to datetime object using the issue_date
            issue_date = report['issue_date']
            scheduled_print_finish_dt = datetime.combine(issue_date, report['scheduled_print_finish'])
            scheduled_print_finish_dt = timezone.make_aware(scheduled_print_finish_dt, timezone=IST)
            
            # Calculate delay in minutes (rounded to 1 decimal place)
            calculated_delay = round((production_end_ist - scheduled_print_finish_dt).total_seconds() / 60, 1)
            delay_minutes = max(0, calculated_delay)

        # Calculate efficiency: (latest_editorial_release - scheduled_lprs) + (scheduled_print_finish - latest_production_end)
        efficiency_minutes = 0
        
        if (report['latest_editorial_release'] is not None and 
            report['scheduled_lprs'] is not None and 
            report['scheduled_print_finish'] is not None and 
            report['latest_production_end'] is not None):
            
            # Convert datetime objects to IST for consistent comparison
            editorial_release_ist = report['latest_editorial_release'].astimezone(IST)
            production_end_ist = report['latest_production_end'].astimezone(IST)
            
            # Convert time objects to datetime objects using the issue_date
            issue_date = report['issue_date']
            scheduled_lprs_dt = datetime.combine(issue_date, report['scheduled_lprs'])
            scheduled_lprs_dt = timezone.make_aware(scheduled_lprs_dt, timezone=IST)
            
            scheduled_print_finish_dt = datetime.combine(issue_date, report['scheduled_print_finish'])
            scheduled_print_finish_dt = timezone.make_aware(scheduled_print_finish_dt, timezone=IST)
            
            # Calculate first part: (latest_editorial_release - scheduled_lprs)
            editorial_to_lprs = (editorial_release_ist - scheduled_lprs_dt).total_seconds() / 60
            
            # Calculate second part: (scheduled_print_finish - latest_production_end)
            print_finish_to_production = (scheduled_print_finish_dt - production_end_ist).total_seconds() / 60
            
            # Total efficiency in minutes (rounded to 1 decimal place)
            efficiency_minutes = round(editorial_to_lprs + print_finish_to_production, 1)

        final_reports.append({
            'plant_name': report['plant_name'],
            'issue_date': report['issue_date'],
            'scheduled_lprs': report['scheduled_lprs'],
            'scheduled_print_finish': report['scheduled_print_finish'],
            'latest_editorial_release': report['latest_editorial_release'],
            'production_end': report['latest_production_end'],
            'planned_folders': planned_folders,
            'actual_folders_run': actual_folders_run,
            'additional_folders_run': additional_folders_run,
            'uv_runs_count': uv_runs_count,
            'total_reports_count': report['total_reports_count'],
            'delay_minutes': delay_minutes,
            'efficiency_minutes': efficiency_minutes,
        })

    context = {
        'aggregated_reports': final_reports,
        'total_combinations': len(final_reports),
    }

    return render(request, 'upload_from_pi/production_report_list.html', context)


# -----------------------------------------------------------------------------
# Service class (unchanged except for style/comments)
# -----------------------------------------------------------------------------
class ProductionReportAggregationService:
    @staticmethod
    def calculate_folder_count(plant_name, issue_date):
        distinct_folders = (
            ProductionReport.objects
            .filter(plant_name=plant_name, issue_date=issue_date, toi_city=True)
            .values('folder', 'folders_count')
            .distinct()
        )
        return sum(f['folders_count'] for f in distinct_folders)

    @staticmethod
    def get_aggregated_reports_by_month(year, month):
        scheduled_lprs_subquery = ScheduledTime.objects.filter(
            plant_name__iexact=OuterRef('plant_name'), is_active=True
        ).values('scheduled_lprs')[:1]

        scheduled_print_finish_subquery = ScheduledTime.objects.filter(
            plant_name__iexact=OuterRef('plant_name'), is_active=True
        ).values('scheduled_print_finish')[:1]

        latest_editorial_release_subquery = BookWiseDetails.objects.filter(
            issueid__plant_name=OuterRef('plant_name'),
            issueid__issue_date=OuterRef('issue_date'),
            issueid__toi_city=True,
            editorial_release__isnull=False,
        ).order_by('-editorial_release').values('editorial_release')[:1]

        base_reports = (
            ProductionReport.objects
            .filter(issue_date__year=year, issue_date__month=month, toi_city=True)
            .values('plant_name', 'issue_date')
            .annotate(
                latest_production_end=Max('production_end'),
                scheduled_lprs=Subquery(scheduled_lprs_subquery),
                scheduled_print_finish=Subquery(scheduled_print_finish_subquery),
                latest_editorial_release=Subquery(latest_editorial_release_subquery),
                total_reports_count=Count('issueid'),
            )
            .order_by('issue_date', 'plant_name')
        )

        final_reports = []
        for report in base_reports:
            folder_count = ProductionReportAggregationService.calculate_folder_count(
                report['plant_name'], report['issue_date']
            )
            final_report = dict(report)
            final_report['folder_count'] = folder_count
            final_reports.append(final_report)

        return final_reports

    @staticmethod
    def validate_data_completeness(aggregated_data):
        total_records = len(aggregated_data)
        complete_records, partial_records, missing_records = 0, 0, 0

        for record in aggregated_data:
            has_scheduled_lprs = record.get('scheduled_lprs') is not None
            has_scheduled_print_finish = record.get('scheduled_print_finish') is not None
            has_editorial_release = record.get('latest_editorial_release') is not None
            has_production_end = record.get('latest_production_end') is not None
            has_folder_count = record.get('folder_count') not in (None, 0)

            if all([has_scheduled_lprs, has_scheduled_print_finish, has_editorial_release, has_production_end, has_folder_count]):
                complete_records += 1
            elif has_production_end and has_folder_count:
                partial_records += 1
            else:
                missing_records += 1

        return {
            'total_records': total_records,
            'complete_records': complete_records,
            'partial_records': partial_records,
            'missing_records': missing_records,
            'completeness_percentage': (complete_records / total_records * 100) if total_records else 0,
        }