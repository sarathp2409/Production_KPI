# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django-based Production KPI system designed to collect, process, and analyze production data from printing plants. The system integrates with PI systems (Process Information systems) to download production reports and provide analytical views of production performance.

## Commands

### Development Commands
- **Run development server**: `python manage.py runserver`
- **Create migrations**: `python manage.py makemigrations`
- **Apply migrations**: `python manage.py migrate`
- **Create superuser**: `python manage.py createsuperuser`
- **Collect static files**: `python manage.py collectstatic`
- **Django shell**: `python manage.py shell`

### Database
- **PostgreSQL database**: `production_kpi`
- **Default user/password**: `postgres/times` (development only)
- **Host**: `localhost:5432`

## Architecture & Key Components

### Django Apps
1. **upload_from_pi**: Core data processing and reporting app
   - Handles data import from PI systems via HTTP API
   - Contains all production-related models and views
   - Provides aggregated reporting functionality

2. **handler_default_data**: Configuration and default data management
   - Contains `ScheduledTime` model for plant scheduling information
   - Manages default data and plant configurations

3. **pagination_dash**: data processing and reporting for pagination
   - Contains all pagination and innovation related models and views
   - Provides functionality to View, Edit and Delete records
   - Provides functionality to aggregate data and send email to a particular recipients list

### Key Models (upload_from_pi/models.py)

**ProductionReport**: Main production data model with comprehensive metrics including:
- Issue tracking, production times, waste metrics
- Machine and folder information
- Performance scores and rankings

**BookWiseDetails**: Detailed book-level production information
- Editorial release times, plate information
- Book-specific production metrics

**Innovation**: Innovation tracking for production improvements
- Links to ProductionReport via foreign key
- Impact measurement and complexity assessment

**Downtime**: Production interruption tracking
- Categorized by department and reason
- Waste tracking by type (cutoff, scum, white, other)

**WebBreak**: Web break incident tracking
- Material and equipment information
- Operator and reason tracking

**ReelConsumption**: Paper/material consumption tracking
- Actual vs captured consumption comparison
- Material specifications and usage metrics

### Data Processing Architecture

The system uses a handler-based architecture for processing different types of production data:

- **Data Handlers** (upload_from_pi/data_handler.py): Abstract base classes and concrete implementations for processing different report types
- **PI Integration**: HTTP API integration with `pi40da.timesgroup.com` for data retrieval
- **Plant IDs**: Multiple plant configurations managed in `plant_ids.py`

### Views & URLs

**Main URLs**:
- `/import_data/` - Data upload/processing endpoint
- `/import_data/production-reports/` - Aggregated production report view

**Key Views**:
- `upload_reports_db`: Processes production data for multiple plants
- `aggregated_production_report_view`: Provides KPI dashboard with delay calculations

### Time Zone Handling

The system uses IST (Asia/Kolkata) timezone with sophisticated delay calculations:
- Production end times compared against 04:00 IST cutoffs
- Editorial release time tracking
- Efficiency calculations based on scheduled vs actual times

### Database Indexes

Models include strategic indexes for performance:
- Date-based indexes (issue_date, edition_date)
- Plant and folder-based indexes
- Composite indexes for common query patterns

## Development Notes

### Data Import Process
1. Data is downloaded from PI systems using plant-specific URLs
2. Multiple report types processed: General, Book Wise Details, Down Time, Web Break, Reel Consumption
3. Missing column detection and reporting for data quality assurance
4. Processing includes 5-second delays between operations

### Performance Considerations
- Database queries use subqueries for complex aggregations
- Timezone-aware datetime handling throughout
- Strategic use of select_related and prefetch_related for query optimization

### Key Business Logic
- TOI City filtering (`toi_city=True`) for specific reporting
- Folder count calculations across distinct folders
- Delay calculations against scheduled print finish times
- Efficiency metrics combining editorial and production timing

## File Structure

```
production_kpi/
├── production_kpi/           # Main Django project
│   ├── settings.py          # Django configuration
│   └── urls.py              # Root URL configuration
├── upload_from_pi/          # Core production data app
│   ├── models.py            # All production models
│   ├── views.py             # Report processing and views
│   ├── data_handler.py      # Data processing handlers
│   ├── urls.py              # App URL routing
│   └── templates/           # HTML templates
├── handler_default_data/    # Configuration app
│   └── models.py            # ScheduledTime and defaults
└── manage.py               # Django management script
```
- Inhouse data\
- In the column H 'balloon_printed' and column I 'has_masthead' please appen 'TOI Book-2' to it to make it 'TOI Book-2 balloon_printed' and 'TOI Book-2 has_masthead'.\
- Is book_order column very important. Can we remove this column to avoid confusion.\
- Can you rename Column k 'remarks_toi' to 'extra_miles_toi' and Column L 'remarks_others' to 'extra_miles_others' \
- Can you rename 'gnp_et_had_2_books' to 'et_had_2_books'. This is not a GNP Specific information, rather to understand if ET carried 2 Books. This column can be moved next to 'first_time_execution_info'\
# Competitor Data\
- 'competitor_name' is different for each locations and is available in @pagination_dash\comp_info.json . Can you add this as a dropdown list for competitor_name