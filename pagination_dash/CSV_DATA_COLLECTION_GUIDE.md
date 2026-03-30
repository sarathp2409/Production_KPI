# Pagination Data Collection Guide

This guide explains how to fill in the CSV templates for historical pagination data collection.

## Overview

Each plant will receive 2 CSV files:
1. **`{plant_name}_inhouse.csv`** - For your plant's book and pagination data
2. **`{plant_name}_competitor.csv`** - For competitor newspaper data

## Quick Start

1. Open your plant's CSV files in Excel or Google Sheets
2. Delete the example rows (keep the header row!)
3. Fill in your historical data following this guide
4. Save as CSV (UTF-8 encoding)
5. Return the completed files for import

---

## In-House Data CSV (`{plant_name}_inhouse.csv`)

### Structure
- **One row per book per date**
- For each day, you'll have 3-7 rows (one for each book: TOI B-1, TOI B-2, TIMS B-1, etc.)
- Report-level fields (remarks, GNP flags) only need to be filled in the FIRST row for each date

### Column Descriptions

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| `plant_id` | Pre-filled | Your plant's ID (don't change) | ODBCAIR30 |
| `plant_name` | Pre-filled | Your plant name (don't change) | Airoli |
| `issue_date` | Yes | Issue date in YYYY-MM-DD format | 2023-01-15 |
| `book_name` | Yes | Book type (see valid values below) | TOI B-1 |
| `snp_pages` | Yes | Standard News Pages count | 24 |
| `gnp_pages_type` | No | GNP innovation type if any | 4 Pg Vantage |
| `number_of_gnp_jackets` | No | Number of GNP jackets | 1 |
| `balloon_printed` | No | Was balloon printed? (B-2 only) | Yes |
| `has_masthead` | No | Has masthead? (B-2 only) | Yes |
| `book_order` | No | Display order (0-6) | 0 |
| `remarks_toi` | No | TOI-specific remarks | |
| `remarks_others` | No | Other remarks | |
| `first_time_execution_info` | No | First-time execution notes | |
| `gnp_et` | No | ET had GNP? | Yes |
| `gnp_et_b1` | No | ET B-1 had GNP? | |
| `gnp_et_b2` | No | ET B-2 had GNP? | |
| `gnp_et_had_2_books` | No | ET had 2 books? | |
| `gnp_mt` | No | MT had GNP? | |
| `gnp_mirror` | No | Mirror had GNP? | |
| `gnp_nbt` | No | NBT had GNP? | |
| `gnp_tims` | No | TIMS had GNP? | |
| `gnp_remarks` | No | GNP-specific remarks | |

### Valid Book Names
- `TOI B-1`
- `TOI B-2`
- `TIMS B-1`
- `TIMS B-2`
- `TOI Supp-1`
- `TOI Supp-2`
- `TOI Supp-3`

### Valid GNP Page Types
- `2 Pg Jkt`
- `4 Pg Jkt - 2 diff clients`
- `4 Pg Vantage`
- `4 Pg Power Jkt`
- `8 Pg Super-pano`
- `6 Pg GNP`
- `8 Pg GNP`

### Example Data (for one date with 3 books)

```csv
plant_id,plant_name,issue_date,book_name,snp_pages,gnp_pages_type,number_of_gnp_jackets,balloon_printed,has_masthead,book_order,remarks_toi,remarks_others,first_time_execution_info,gnp_et,gnp_et_b1,gnp_et_b2,gnp_et_had_2_books,gnp_mt,gnp_mirror,gnp_nbt,gnp_tims,gnp_remarks
ODBCAIR30,Airoli,2023-01-15,TOI B-1,24,4 Pg Vantage,1,,,0,Good execution,,,,,,,,Yes,,,Yes,
ODBCAIR30,Airoli,2023-01-15,TOI B-2,16,,0,Yes,Yes,1,,,,,,,,,,,,,
ODBCAIR30,Airoli,2023-01-15,TIMS B-1,20,,0,,,2,,,,,,,,,,,,,
```

### Important Notes

1. **Date Format**: Always use `YYYY-MM-DD` (e.g., `2023-01-15`)
2. **Boolean Values**: Use `Yes` or `No` (or leave empty for No)
3. **B-2 Fields**: `balloon_printed` and `has_masthead` only apply to `TOI B-2` and `TIMS B-2`
4. **GNP Flags**: Only fill in GNP flags for publications your plant handles
5. **First Row**: Report-level fields (remarks, GNP flags) are read from the first book row of each date

---

## Competitor Data CSV (`{plant_name}_competitor.csv`)

### Structure
- **One row per competitor per date**
- Each row captures both Main book and Supplement book data

### Column Descriptions

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| `plant_id` | Pre-filled | Your plant's ID | ODBCAIR30 |
| `plant_name` | Pre-filled | Your plant name | Airoli |
| `issue_date` | Yes | Issue date in YYYY-MM-DD format | 2023-01-15 |
| `competitor_name` | Yes | Competitor newspaper name | Hindustan Times |
| `main_snp_pages` | No | Main book SNP pages | 24 |
| `main_gnp_pages_type` | No | Main book GNP type | 4 Pg Vantage |
| `main_number_of_gnp_jacket` | No | Main book GNP jackets | 1 |
| `main_number_of_books` | No | Number of main books | 2 |
| `supp_snp_pages` | No | Supplement SNP pages | 8 |
| `supp_gnp_pages_type` | No | Supplement GNP type | |
| `supp_number_of_gnp_jacket` | No | Supplement GNP jackets | 0 |
| `supp_number_of_books` | No | Number of supplements | 1 |
| `innovation_1` | No | First innovation type | Center Panorama |
| `innovation_2` | No | Second innovation type | |
| `innovation_3` | No | Third innovation type | |
| `comment` | No | Additional comments | |

### Valid Innovation Types
- `Center Panorama`
- `Bookmark`
- `Seamless Panorama`
- `Front Vantage`
- `Reverse Flap`
- `Fragrance`
- `French-Window`
- `Power Jacket`
- `Others`

### Example Data

```csv
plant_id,plant_name,issue_date,competitor_name,main_snp_pages,main_gnp_pages_type,main_number_of_gnp_jacket,main_number_of_books,supp_snp_pages,supp_gnp_pages_type,supp_number_of_gnp_jacket,supp_number_of_books,innovation_1,innovation_2,innovation_3,comment
ODBCAIR30,Airoli,2023-01-15,Hindustan Times,24,4 Pg Vantage,1,2,8,,0,1,Center Panorama,,,Good innovation
ODBCAIR30,Airoli,2023-01-15,DNA,20,,0,1,0,,0,0,,,,
```

### Important Notes

1. **Import Order**: In-house data must be imported BEFORE competitor data (competitor data links to the report created by in-house data)
2. **Multiple Competitors**: Add one row for each competitor for each date
3. **Empty Values**: Leave cells empty if no data (don't put 0 for optional fields unless the value is actually 0)

---

## Validation

Before submitting your CSV files, you can validate them using the validation script:

```bash
# Validate in-house CSV
python pagination_dash/validate_csv.py csv_templates/Airoli_inhouse.csv

# Validate competitor CSV
python pagination_dash/validate_csv.py csv_templates/Airoli_competitor.csv
```

The validator will check for:
- Required fields
- Valid date formats
- Valid choice values
- Duplicate entries

---

## Common Errors and Solutions

### 1. Invalid date format
**Error**: `Invalid date format '15-01-2023'. Expected YYYY-MM-DD`
**Solution**: Change date from `15-01-2023` to `2023-01-15`

### 2. Invalid book name
**Error**: `Invalid book_name 'TOI-B1'. Must be one of: TOI B-1, TOI B-2...`
**Solution**: Use exact book name with space: `TOI B-1` not `TOI-B1`

### 3. Duplicate book for same date
**Error**: `Duplicate book 'TOI B-1' for ODBCAIR30 on 2023-01-15`
**Solution**: Check if you've added the same book twice for the same date

### 4. Missing required field
**Error**: `Missing required field 'issue_date'`
**Solution**: Ensure all required fields have values

### 5. Excel date conversion
**Problem**: Excel converts dates to its own format
**Solution**: Format the date column as "Text" before entering dates, or use `2023-01-15` format

---

## Tips for Efficient Data Entry

1. **Copy-paste dates**: For each date, copy the rows and just update the date
2. **Use Excel formulas**: Use formulas to auto-calculate totals (for reference only)
3. **Sort by date**: Keep data sorted by date for easier review
4. **Fill report fields once**: Only fill remarks and GNP flags in the first book row of each date
5. **Leave defaults**: Leave optional fields empty if they're 0 or No

---

## Plant-Specific GNP Publications

Only fill in GNP flags for publications your plant handles:

| Plant | GNP Publications |
|-------|-----------------|
| Airoli | Mirror, MT, TIMS |
| Bhosari | ET, MT, TIMS |
| Bommasandra | ET, TIMS, Mirror |
| Chemmencherry | ET, TIMS |
| Chinhat | ET, NBT, TIMS |
| Kandivali | ET, MT, NBT, Mirror, TIMS |
| Manesar | ET, NBT, TIMS |
| Nacharam | ET, TIMS |
| Sahibabad | ET, NBT, TIMS |
| Saltlake | ET, TIMS |
| Vejalpur | ET, TIMS |
| Baroda | (No GNP) |
| Butibori | (No GNP) |
| Trivandrum | (No GNP) |

---

## Support

If you encounter issues:
1. Check this guide for common errors
2. Run the validation script
3. Contact the system administrator with:
   - Your plant name
   - The error message
   - A screenshot of the problematic row

# /Next Steps

  To generate the CSV templates and start collecting data:

  # 1. Generate all CSV templates
  python pagination_dash/generate_csv_templates.py

  # 2. Templates will be created in: pagination_dash/csv_templates/
  #    - Airoli_inhouse.csv, Airoli_competitor.csv
  #    - Bhosari_inhouse.csv, Bhosari_competitor.csv
  #    - ... (for all 14 plants)

  # 3. Distribute templates to location coordinators

  # 4. Validate returned CSVs
  python pagination_dash/validate_csv.py csv_templates/Airoli_inhouse.csv

  # 5. Import with dry-run first
  python manage.py shell
  >>> from pagination_dash.import_pagination_history import PaginationDataImporter
  >>> importer = PaginationDataImporter('csv_templates/Airoli_inhouse.csv',
  'csv_templates/Airoli_competitor.csv', dry_run=True)
  >>> importer.run()

  # 6. If validation passes, import for real
  >>> importer = PaginationDataImporter('csv_templates/Airoli_inhouse.csv',
  'csv_templates/Airoli_competitor.csv', dry_run=False)
  >>> importer.run()