# Pagination Data Import Guide

This guide explains how to collect and import historical pagination data into the Production KPI system using CSV/Excel files.

## Table of Contents

1. [Overview](#overview)
2. [CSV Templates](#csv-templates)
3. [Field Specifications](#field-specifications)
4. [Plant-Specific Information](#plant-specific-information)
5. [Data Collection Instructions](#data-collection-instructions)
6. [Import Instructions](#import-instructions)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The pagination_dash app tracks daily pagination data for TOI plants, including:
- **In-house data**: Our books (TOI, TIMS), SNP/GNP pages, jacket counts
- **Competitor data**: Competitor newspapers, their page counts, innovations

Two CSV templates are provided:
1. **inhouse_data_template.csv** - For PaginationReport, GNPInformation, and BookDetails
2. **competitor_data_template.csv** - For CompetitorData and CompetitorBookDetails

---

## CSV Templates

### Template 1: In-House Data

**File**: `inhouse_data_template.csv`

**Structure**: Multi-row format where each row represents ONE BOOK within a report. Report-level data (plant, date, remarks, GNP info) is repeated for all books in the same report.

**Example**:
```csv
plant_id,plant_name,issue_date,remarks_toi,remarks_others,first_time_execution_info,gnp_et,gnp_mt,gnp_mirror,gnp_nbt,gnp_tims,gnp_remarks,book_name,snp_pages,gnp_pages_type,number_of_gnp_jackets,book_order
ODBCAIR30,Airoli,2025-09-15,TOI printed on time,TIMS had slight delay,New jacket type tested,No,Yes,Yes,No,Yes,MT had 4pg jacket,TOI B-1,24,4 Pg Jkt - 2 diff clients,2,1
ODBCAIR30,Airoli,2025-09-15,TOI printed on time,TIMS had slight delay,New jacket type tested,No,Yes,Yes,No,Yes,MT had 4pg jacket,TOI B-2,20,,0,2
ODBCAIR30,Airoli,2025-09-15,TOI printed on time,TIMS had slight delay,New jacket type tested,No,Yes,Yes,No,Yes,MT had 4pg jacket,TIMS B-1,16,2 Pg Jkt,1,3
```

**Key Points**:
- Each row = 1 book
- Same plant_id + issue_date = same report
- Report fields (remarks, GNP flags) must be identical across all rows of the same report
- Minimum 1 book per report, typically 2-4 books

---

### Template 2: Competitor Data

**File**: `competitor_data_template.csv`

**Structure**: Single-row per competitor with Main/Supplement book data in separate columns.

**Example**:
```csv
plant_id,plant_name,issue_date,competitor_name,innovation_1,innovation_2,innovation_3,comment,main_snp_pages,main_gnp_pages_type,main_number_of_gnp_jacket,main_number_of_books,supp_snp_pages,supp_gnp_pages_type,supp_number_of_gnp_jacket,supp_number_of_books
ODBCAIR30,Airoli,2025-09-15,Hindustan Times,Center Panorama,Power Jacket,,Had impressive center panorama,20,2 Pg Jkt,1,1,8,,0,1
ODBCAIR30,Airoli,2025-09-15,Loksatta,,,No special innovations,16,,0,1,4,,0,1
```

**Key Points**:
- Each row = 1 competitor
- Must match existing plant_id + issue_date from in-house data
- Main book = primary edition
- Supplement book = supplement edition (can be all zeros if no supplement)
- Up to 3 innovation types per competitor

---

## Field Specifications

### In-House Data Fields

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| **plant_id** | Text | Yes | Plant ID from system | ODBCAIR30 |
| **plant_name** | Text | Yes | Plant display name | Airoli |
| **issue_date** | Date | Yes | Issue date (YYYY-MM-DD) | 2025-09-15 |
| **remarks_toi** | Text | No | Remarks for TOI publications | TOI printed on time |
| **remarks_others** | Text | No | Remarks for other publications | TIMS had slight delay |
| **first_time_execution_info** | Text | No | First-time execution details | New jacket type tested |
| **gnp_et** | Yes/No | Yes | Economic Times GNP | Yes |
| **gnp_mt** | Yes/No | Yes | Maharashtra Times GNP | No |
| **gnp_mirror** | Yes/No | Yes | Mirror GNP | Yes |
| **gnp_nbt** | Yes/No | Yes | Navbharat Times GNP | No |
| **gnp_tims** | Yes/No | Yes | TIMS GNP | Yes |
| **gnp_remarks** | Text | No | GNP-specific remarks | MT had 4pg jacket |
| **book_name** | Choice | Yes | Book name | TOI B-1 |
| **snp_pages** | Number | Yes | Standard news pages | 24 |
| **gnp_pages_type** | Choice | No | GNP type | 4 Pg Jkt - 2 diff clients |
| **number_of_gnp_jackets** | Number | No | GNP jacket count | 2 |
| **book_order** | Number | Yes | Display order | 1 |

#### Valid Book Names
- TOI B-1
- TOI B-2
- TIMS B-1
- TIMS B-2
- TOI Supp-1
- TOI Supp-2
- TOI Supp-3

#### Valid GNP Page Types
- 2 Pg Jkt
- 4 Pg Jkt - 2 diff clients
- 4 Pg Vantage
- 4 Pg Power Jkt
- 8 Pg Super-pano
- 6 Pg GNP
- 8 Pg GNP

**Note**: `gnp_pages_count` and `total_pages` are auto-calculated by the system. Do NOT include them in CSV.

---

### Competitor Data Fields

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| **plant_id** | Text | Yes | Plant ID (must match in-house) | ODBCAIR30 |
| **plant_name** | Text | Yes | Plant name | Airoli |
| **issue_date** | Date | Yes | Issue date (YYYY-MM-DD) | 2025-09-15 |
| **competitor_name** | Text | Yes | Competitor newspaper name | Hindustan Times |
| **innovation_1** | Choice | No | First innovation type | Center Panorama |
| **innovation_2** | Choice | No | Second innovation type | Power Jacket |
| **innovation_3** | Choice | No | Third innovation type | Bookmark |
| **comment** | Text | No | Comments about competitor | Had impressive execution |
| **main_snp_pages** | Number | No | Main book SNP pages | 20 |
| **main_gnp_pages_type** | Choice | No | Main book GNP type | 2 Pg Jkt |
| **main_number_of_gnp_jacket** | Number | No | Main GNP jacket count | 1 |
| **main_number_of_books** | Number | No | Main book count | 1 |
| **supp_snp_pages** | Number | No | Supplement SNP pages | 8 |
| **supp_gnp_pages_type** | Choice | No | Supplement GNP type | |
| **supp_number_of_gnp_jacket** | Number | No | Supplement GNP jacket count | 0 |
| **supp_number_of_books** | Number | No | Supplement book count | 1 |

#### Valid Innovation Types
- Center Panorama
- Bookmark
- Seamless Panorama
- Front Vantage
- Reverse Flap
- Fragrance
- French-Window
- Power Jacket
- Others

**Note**: Leave innovation fields blank if no innovations were used.

---

## Plant-Specific Information

### Valid Plant IDs and Names

| Plant ID | Plant Name | Display Name |
|----------|------------|--------------|
| ODBCAIR30 | Airoli | Airoli |
| ACTIVE42 | Baroda | Baroda |
| ODBCAIR32 | Pune | Bhosari |
| MAIN34 | Bangalore | Bommasandra |
| MAIN38 | Nagpur | Butibori |
| MAIN35 | Chennai | Chemmencherry |
| MAIN40 | Lucknow | Chinhat |
| ODBCAIR28 | Kandivali | Kandivali |
| ACTIVE44 | Manesar | Manesar |
| MAIN36 | Hyderabad | Nacharam |
| MAIN41 | Sahibabad | Sahibabad |
| ODBCAIR33 | Kolkata | Saltlake |
| ACTIVE43 | Trivandrum | Trivandrum |
| MAIN37 | Ahmedabad | Vejalpur |

---

### GNP Publications by Plant

Only certain plants print specific GNP publications. Use this guide to fill GNP flags correctly:

| Plant | ET | MT | Mirror | NBT | TIMS |
|-------|----|----|--------|-----|------|
| **Airoli** | ❌ | ✅ | ✅ | ❌ | ✅ |
| **Baroda** | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Bhosari** | ✅ | ✅ | ❌ | ❌ | ✅ |
| **Bommasandra** | ✅ | ❌ | ✅ | ❌ | ✅ |
| **Butibori** | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Chemmencherry** | ✅ | ❌ | ❌ | ❌ | ✅ |
| **Chinhat** | ✅ | ❌ | ❌ | ✅ | ✅ |
| **Kandivali** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Manesar** | ✅ | ❌ | ❌ | ✅ | ✅ |
| **Nacharam** | ✅ | ❌ | ❌ | ❌ | ✅ |
| **Sahibabad** | ✅ | ❌ | ❌ | ✅ | ✅ |
| **Saltlake** | ✅ | ❌ | ❌ | ❌ | ✅ |
| **Trivandrum** | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Vejalpur** | ✅ | ❌ | ❌ | ❌ | ✅ |

**Legend**: ✅ = Can have GNP, ❌ = Does not have GNP

**Important**: Only set GNP flags to "Yes" for publications that are actually available at that plant AND were used on that specific date.

---

### Competitor Names by Plant

Each plant has specific competitors to track:

| Plant | Competitors |
|-------|------------|
| **Airoli** | Hindustan Times, Loksatta, Lokmat, Dainik Bhaskar, Mint |
| **Baroda** | Hindustan Times, Nav-Gujarat Samay, Divya Bhaskar, Gujarat Samachar, Sandesh |
| **Bhosari** | Hindustan Times, Sakal, Lokmat, Indian Express |
| **Bommasandra** | The Hindu, Deccan Herald, Indian Express, V K, Prajavani, Vijayawani |
| **Butibori** | Hindustan Times, Sakal, Lokmat |
| **Chemmencherry** | The Hindu, Daily Thanthi, Dinamalar, Hindu Tamil, Indian Express |
| **Chinhat** | Hindustan Times, Dainik Jagran |
| **Kandivali** | Hindustan Times, Loksatta, Lokmat, Dainik Bhaskar, Mint |
| **Manesar** | Hindustan Times, Hindustan, Dainik Bhaskar, Dainik Jagran, Mint |
| **Nacharam** | Deccan Chronicle, The Hindu, Namasthe Telangana, Enadu, Sakshi |
| **Sahibabad** | Hindustan Times, Hindustan, Dainik Bhaskar, Dainik Jagran, Mint |
| **Saltlake** | The Telegraph, Ananda Bazar Patrika |
| **Trivandrum** | The Hindu, Indian Express |
| **Vejalpur** | Hindustan Times, Nav-Gujarat Samay, Divya Bhaskar, Gujarat Samachar, Sandesh |

**Note**: You can track any of these competitors per plant. Not required to track all every day.

---

## Data Collection Instructions

### Step 1: Prepare Excel Files

1. Open the CSV templates in Excel or Google Sheets
2. Save copies with your desired naming (e.g., `pagination_history_sep2024.xlsx`)
3. Keep the column headers exactly as shown in templates

### Step 2: Fill In-House Data

For each day:

1. **Create rows for all books**:
   - Start with TOI B-1, TOI B-2, TIMS B-1 (most common)
   - Add supplement rows if applicable (TOI Supp-1, etc.)

2. **Fill report-level fields** (same for all book rows):
   - plant_id, plant_name, issue_date
   - remarks_toi, remarks_others, first_time_execution_info
   - All GNP flags (gnp_et, gnp_mt, gnp_mirror, gnp_nbt, gnp_tims)
   - gnp_remarks

3. **Fill book-specific fields** (different for each row):
   - book_name
   - snp_pages
   - gnp_pages_type (if GNP jacket was used)
   - number_of_gnp_jackets
   - book_order (1, 2, 3, ...)

### Step 3: Fill Competitor Data

For each competitor on each day:

1. **Create one row per competitor**
2. **Fill competitor info**:
   - plant_id, plant_name, issue_date (must match in-house data)
   - competitor_name (from plant-specific list)
   - innovation_1, innovation_2, innovation_3 (if applicable)
   - comment

3. **Fill Main book data**:
   - main_snp_pages
   - main_gnp_pages_type (if applicable)
   - main_number_of_gnp_jacket
   - main_number_of_books

4. **Fill Supplement book data**:
   - supp_snp_pages
   - supp_gnp_pages_type (if applicable)
   - supp_number_of_gnp_jacket
   - supp_number_of_books

**Tip**: If competitor has no supplement, set all supp_* fields to 0.

### Step 4: Data Validation Checklist

Before importing, verify:

- [ ] All dates in YYYY-MM-DD format
- [ ] All plant_ids are valid (see table above)
- [ ] All book_names match valid choices
- [ ] All gnp_pages_type match valid choices
- [ ] All innovation types match valid choices
- [ ] Boolean fields use Yes/No (not True/False or 1/0)
- [ ] Each competitor row matches an in-house report (same plant_id + issue_date)
- [ ] No duplicate book names within same report
- [ ] No duplicate competitor names within same report
- [ ] Book order is sequential (1, 2, 3, ...)

### Step 5: Save as CSV

1. **For Excel**:
   - File → Save As → CSV (Comma delimited) (*.csv)
   - Save as `inhouse_data.csv` and `competitor_data.csv`

2. **For Google Sheets**:
   - File → Download → Comma-separated values (.csv)

---

## Import Instructions

### Prerequisites

1. Ensure Django environment is set up
2. Database is running (PostgreSQL)
3. CSV files are saved in `pagination_dash/` directory

### Method 1: Command Line (Recommended)

```bash
# Navigate to project directory
cd C:\Users\sarath.pr\Documents\DEV\Production_KPI

# Activate virtual environment (if using one)
.venv\Scripts\activate

# Run import via Django shell
python manage.py shell < pagination_dash/import_pagination_history.py
```

### Method 2: Django Shell

```bash
# Start Django shell
python manage.py shell

# Execute the import script
exec(open('pagination_dash/import_pagination_history.py').read())
```

### Method 3: Custom Paths

If your CSV files are in a different location:

```python
# Start Django shell
python manage.py shell

# Import and run with custom paths
from pagination_dash.import_pagination_history import PaginationDataImporter

importer = PaginationDataImporter(
    inhouse_csv_path='C:/path/to/your/inhouse_data.csv',
    competitor_csv_path='C:/path/to/your/competitor_data.csv',
    created_by_username='your_username'  # Optional, defaults to 'admin'
)

importer.run()
```

### What Happens During Import

The import script will:

1. **Read in-house CSV**
   - Group rows by plant_id + issue_date
   - Validate all fields
   - Create PaginationReport records
   - Create GNPInformation records
   - Create BookDetails records

2. **Read competitor CSV**
   - Find matching reports
   - Validate competitor names and innovations
   - Create CompetitorData records
   - Create CompetitorBookDetails records (Main + Supplement)

3. **Handle errors gracefully**
   - Skip duplicate reports (same plant_id + issue_date)
   - Report validation errors per row
   - Continue processing after errors

4. **Display progress**
   - Show each created/skipped record
   - Display summary statistics
   - List any errors encountered

### Expected Output

```
================================================================================
PAGINATION DATA IMPORT TOOL
================================================================================

Started at: 2025-10-10 14:30:00
Created by user: admin

================================================================================
IMPORTING IN-HOUSE DATA
================================================================================

Processing 10 unique reports...
✅ Created: ODBCAIR30 - 2025-09-15 (3 books)
✅ Created: MAIN34 - 2025-09-16 (3 books)
⏭️  Skipped: ODBCAIR28 - 2025-09-17 (already exists)

================================================================================
IMPORTING COMPETITOR DATA
================================================================================

✅ Created: ODBCAIR30 - 2025-09-15 - Hindustan Times
✅ Created: ODBCAIR30 - 2025-09-15 - Loksatta
⏭️  Skipped: MAIN34 - 2025-09-16 - The Hindu (already exists)

================================================================================
IMPORT SUMMARY
================================================================================

📊 In-House Data:
   - Reports Created: 8
   - Reports Skipped (duplicates): 2
   - Books Created: 24

📊 Competitor Data:
   - Competitors Created: 18
   - Competitor Books Created: 36

✅ No errors!

================================================================================

Completed at: 2025-10-10 14:30:45

✅ Import completed! You can now view the data in the admin panel or application.
```

---

## Troubleshooting

### Common Errors

#### 1. "Invalid plant_id: XYZ"

**Cause**: Plant ID not recognized by system

**Solution**: Use valid plant IDs from the table above (e.g., ODBCAIR30, MAIN34)

---

#### 2. "Invalid date format: 15-09-2025. Expected YYYY-MM-DD"

**Cause**: Date not in correct format

**Solution**: Use YYYY-MM-DD format (e.g., 2025-09-15)

---

#### 3. "Invalid book_name: 'TOI Book 1'. Must be one of: TOI B-1, TOI B-2..."

**Cause**: Book name doesn't match exact choices

**Solution**: Use exact book names: TOI B-1, TOI B-2, TIMS B-1, etc. (note spacing and hyphen)

---

#### 4. "Report not found for ODBCAIR30 - 2025-09-15. Import in-house data first."

**Cause**: Trying to import competitor data before in-house data

**Solution**: Always import in-house data first, then competitor data

---

#### 5. "Duplicate book name detected: 'TOI B-1'"

**Cause**: Same book name appears twice in same report

**Solution**: Each book name can only appear once per report. Check for duplicate rows.

---

#### 6. "A report for Airoli on 2025-09-15 already exists."

**Cause**: Report already imported

**Solution**: This is expected on re-runs. The script will skip duplicates automatically.

---

### Data Quality Tips

1. **Use Excel formulas for repetitive data**:
   - Fill report-level fields for all book rows: `=$A$2`
   - Auto-increment book_order: `=ROW()-1`

2. **Validate before import**:
   - Sort by plant_id and issue_date to group reports
   - Check that GNP flags match plant capabilities
   - Verify competitor names match plant location

3. **Start small**:
   - Import 1-2 weeks of data first
   - Verify in application
   - Then import larger date ranges

4. **Keep backups**:
   - Save Excel files with formulas
   - Export CSV copies before each import
   - Document any data cleaning steps

---

## Support

For issues or questions:

1. Check the error messages in import output
2. Review field specifications in this document
3. Verify CSV format matches templates
4. Contact the development team with specific error messages

---

## Appendix: Auto-Calculated Fields

The following fields are **automatically calculated** by the system and should NOT be included in CSV:

### BookDetails
- `gnp_pages_count` - Calculated from `gnp_pages_type` using mapping:
  - 2 Pg Jkt → 2
  - 4 Pg Jkt - 2 diff clients → 4
  - 4 Pg Vantage → 4
  - 4 Pg Power Jkt → 4
  - 8 Pg Super-pano → 8
  - 6 Pg GNP → 6
  - 8 Pg GNP → 8

- `total_pages` - Calculated as `snp_pages + gnp_pages_count`

### CompetitorBookDetails
- Same calculations as BookDetails apply

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-10 | Initial version |

---

**Document End**
