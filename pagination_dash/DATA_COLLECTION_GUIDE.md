# Pagination Data Collection Guide (Excel)

This guide explains how to fill in the Excel templates for historical pagination data collection.

## Overview

Each plant will receive **one Excel file** with dropdown validation:
- **`{plant_name}_pagination_data.xlsx`** containing 3 sheets:
  1. **In-House Data** - For your plant's book and pagination data
  2. **Competitor Data** - For competitor newspaper data
  3. **Reference** - Valid values and instructions

## Why Excel with Dropdowns?

- ✅ **Data Quality**: Dropdown validation prevents invalid entries
- ✅ **User-Friendly**: Easy selection from dropdown, no typing errors
- ✅ **Plant-Specific**: Only relevant GNP columns shown for your plant
- ✅ **Visual Cues**: Color-coded headers for required vs optional fields
- ✅ **Built-in Reference**: All valid values documented in the file itself

---

## Quick Start

1. **Open your plant's Excel file** (e.g., `Airoli_pagination_data.xlsx`)
2. **Go to "In-House Data" sheet**
3. **Delete the example rows** (rows 2-4, keep the header row!)
4. **Fill in your historical data** using dropdown arrows for selection
5. **Go to "Competitor Data" sheet** and repeat
6. **Save the file** (keep as .xlsx format)
7. **Validate** using the validation script (optional but recommended)
8. **Return the completed file** for import

---

## Understanding Header Colors

| Color | Meaning | Action Required |
|-------|---------|----------------|
| **Gray** | Pre-filled (locked) | Don't edit - plant_id and plant_name are pre-filled |
| **Dark Blue** | Required field | Must provide a value |
| **Light Blue** | Optional field | Can leave empty |
| **Green** | Dropdown field | Use dropdown arrow to select value |

---

## In-House Data Sheet

### Structure
- **One row per book per date**
- For each day, you'll have 3-7 rows (one for each book: TOI B-1, TOI B-2, TIMS B-1, etc.)
- Report-level fields (remarks, GNP flags) only need to be filled in the FIRST row for each date

### Column Descriptions

| Column | Type | Description | How to Fill |
|--------|------|-------------|-------------|
| `plant_id` | Locked | Your plant's ID | Pre-filled, don't edit |
| `plant_name` | Locked | Your plant name | Pre-filled, don't edit |
| `issue_date` | Required | Issue date | Type in YYYY-MM-DD format (e.g., 2023-01-15) |
| `book_name` | Required, Dropdown | Book type | Use dropdown to select |
| `snp_pages` | Required | Standard News Pages count | Type number (e.g., 24) |
| `gnp_pages_type` | Dropdown | GNP innovation type if any | Use dropdown or leave empty |
| `number_of_gnp_jackets` | Optional | Number of GNP jackets | Type number or leave empty |
| `balloon_printed` | Dropdown | Was balloon printed? (B-2 only) | Use dropdown: Yes/No or leave empty |
| `has_masthead` | Dropdown | Has masthead? (B-2 only) | Use dropdown: Yes/No or leave empty |
| `book_order` | Optional | Display order (0-6) | Type number or leave empty |
| `remarks_toi` | Optional | TOI-specific remarks | Type text or leave empty |
| `remarks_others` | Optional | Other remarks | Type text or leave empty |
| `first_time_execution_info` | Optional | First-time execution notes | Type text or leave empty |
| `gnp_et` | Dropdown | ET had GNP? (if your plant has ET) | Use dropdown: Yes/No or leave empty |
| `gnp_et_b1` | Dropdown | ET B-1 had GNP? | Use dropdown or leave empty |
| `gnp_et_b2` | Dropdown | ET B-2 had GNP? | Use dropdown or leave empty |
| `gnp_et_had_2_books` | Dropdown | ET had 2 books? | Use dropdown or leave empty |
| `gnp_mt` | Dropdown | MT had GNP? (if your plant has MT) | Use dropdown or leave empty |
| `gnp_mirror` | Dropdown | Mirror had GNP? (if your plant has Mirror) | Use dropdown or leave empty |
| `gnp_nbt` | Dropdown | NBT had GNP? (if your plant has NBT) | Use dropdown or leave empty |
| `gnp_tims` | Dropdown | TIMS had GNP? (if your plant has TIMS) | Use dropdown or leave empty |
| `gnp_remarks` | Optional | GNP-specific remarks | Type text or leave empty |

**Note**: Your plant's Excel file will only show GNP columns relevant to your plant's publications.

### Example Data (for one date with 3 books)

| plant_id | plant_name | issue_date | book_name | snp_pages | gnp_pages_type | number_of_gnp_jackets | balloon_printed | has_masthead | ... |
|----------|------------|------------|-----------|-----------|----------------|---------------------|----------------|--------------|-----|
| ODBCAIR30 | Airoli | 2023-01-15 | TOI B-1 | 24 | 4 Pg Vantage | 1 | | | ... |
| ODBCAIR30 | Airoli | 2023-01-15 | TOI B-2 | 16 | | 0 | Yes | Yes | ... |
| ODBCAIR30 | Airoli | 2023-01-15 | TIMS B-1 | 20 | | 0 | | | ... |

### Important Notes

1. **Date Format**: Always use `YYYY-MM-DD` (e.g., `2023-01-15`)
2. **Dropdowns**: Click the dropdown arrow in cells with green headers to select values
3. **Don't Type Manually**: For dropdown fields, ALWAYS use the dropdown - typing may cause validation errors
4. **B-2 Fields**: `balloon_printed` and `has_masthead` only apply to `TOI B-2` and `TIMS B-2`
5. **GNP Flags**: Only fill in GNP flags for publications your plant handles
6. **First Row**: Report-level fields (remarks, GNP flags) are read from the first book row of each date

---

## Competitor Data Sheet

### Structure
- **One row per competitor per date**
- Each row captures both Main book and Supplement book data

### Column Descriptions

| Column | Type | Description | How to Fill |
|--------|------|-------------|-------------|
| `plant_id` | Locked | Your plant's ID | Pre-filled, don't edit |
| `plant_name` | Locked | Your plant name | Pre-filled, don't edit |
| `issue_date` | Required | Issue date | Type in YYYY-MM-DD format |
| `competitor_name` | Required | Competitor newspaper name | Type the competitor name |
| `main_snp_pages` | Optional | Main book SNP pages | Type number or leave empty |
| `main_gnp_pages_type` | Dropdown | Main book GNP type | Use dropdown or leave empty |
| `main_number_of_gnp_jacket` | Optional | Main book GNP jackets | Type number or leave empty |
| `main_number_of_books` | Optional | Number of main books | Type number or leave empty |
| `supp_snp_pages` | Optional | Supplement SNP pages | Type number or leave empty |
| `supp_gnp_pages_type` | Dropdown | Supplement GNP type | Use dropdown or leave empty |
| `supp_number_of_gnp_jacket` | Optional | Supplement GNP jackets | Type number or leave empty |
| `supp_number_of_books` | Optional | Number of supplements | Type number or leave empty |
| `innovation_1` | Dropdown | First innovation type | Use dropdown or leave empty |
| `innovation_2` | Dropdown | Second innovation type | Use dropdown or leave empty |
| `innovation_3` | Dropdown | Third innovation type | Use dropdown or leave empty |
| `comment` | Optional | Additional comments | Type text or leave empty |

### Example Data

| plant_id | plant_name | issue_date | competitor_name | main_snp_pages | main_gnp_pages_type | ... | innovation_1 | comment |
|----------|------------|------------|----------------|----------------|---------------------|-----|-------------|---------|
| ODBCAIR30 | Airoli | 2023-01-15 | Hindustan Times | 24 | 4 Pg Vantage | ... | Center Panorama | Good innovation |
| ODBCAIR30 | Airoli | 2023-01-15 | DNA | 20 | | ... | | |

### Important Notes

1. **Import Order**: In-house data must be imported BEFORE competitor data
2. **Multiple Competitors**: Add one row for each competitor for each date
3. **Empty Values**: Leave cells empty if no data
4. **Use Dropdowns**: Always use dropdowns for GNP types and innovations

---

## Reference Sheet

The Reference sheet in your Excel file contains:
- All valid values for dropdown fields
- Plant-specific GNP publications
- Detailed instructions
- Color legend for headers

**Always refer to this sheet** if you're unsure about valid values.

---

## Validation

Before submitting your Excel file, you can validate it using the validation script:

```bash
# Validate Excel file (validates both In-House and Competitor sheets)
python pagination_dash/validate_data.py xlsx_templates/Airoli_pagination_data.xlsx

# Or for CSV files (if using CSV instead)
python pagination_dash/validate_data.py csv_templates/Airoli_inhouse.csv
```

The validator will check for:
- Required fields
- Valid date formats
- Valid choice values (matches dropdowns)
- Duplicate entries
- Data consistency

---

## Common Errors and Solutions

### 1. Invalid date format
**Error**: `Invalid date format '15-01-2023'. Expected YYYY-MM-DD`
**Solution**: Change date from `15-01-2023` to `2023-01-15`

### 2. Typed value not in dropdown list
**Error**: `Invalid book_name 'TOI-B1'. Must be one of: TOI B-1, TOI B-2...`
**Solution**: Use the dropdown arrow to select the value instead of typing

### 3. Duplicate book for same date
**Error**: `Duplicate book 'TOI B-1' for ODBCAIR30 on 2023-01-15`
**Solution**: Check if you've added the same book twice for the same date

### 4. Missing required field
**Error**: `Missing required field 'issue_date'`
**Solution**: Ensure all required fields (dark blue headers) have values

### 5. Excel auto-formatting dates
**Problem**: Excel converts dates to different formats
**Solution**:
- Format the date column as "Text" before entering dates
- Or use Find & Replace to ensure dates are in `YYYY-MM-DD` format

### 6. Can't see dropdown arrow
**Problem**: Dropdown arrow not visible
**Solution**: Click on the cell - the dropdown arrow appears on the right side of the cell

---

## Tips for Efficient Data Entry

1. **Copy-paste rows**: For similar data, copy the row and just update the changing fields
2. **Use Excel's fill-down**: Drag the fill handle to copy values down (e.g., dates)
3. **Sort by date**: Keep data sorted by date for easier review
4. **Fill report fields once**: Only fill remarks and GNP flags in the first book row of each date
5. **Save frequently**: Save your work often to avoid losing data
6. **Check Reference sheet**: When in doubt about valid values, check the Reference sheet
7. **Use validation script**: Run the validation script before submitting to catch errors early

---

## Plant-Specific GNP Publications

Your Excel file only shows GNP columns for publications your plant handles:

| Plant | GNP Publications |
|-------|-----------------|
| Airoli | Mirror, MT, TIMS |
| Bhosari | ET, MT, TIMS |
| Bommasandra | ET, TIMS, Mirror |
| Chemmencherry | ET, TIMS |
| Chinhat | ET, NBT, TIMS |
| Kandivali | ET, MT, NBT, Mirror, TIMS (ALL) |
| Manesar | ET, NBT, TIMS |
| Nacharam | ET, TIMS |
| Sahibabad | ET, NBT, TIMS |
| Saltlake | ET, TIMS |
| Vejalpur | ET, TIMS |
| Baroda | (No GNP columns) |
| Butibori | (No GNP columns) |
| Trivandrum | (No GNP columns) |

---

## Import Process (For Administrators)

### 1. Generate Excel Templates

```bash
# Generate all plant Excel templates
python pagination_dash/generate_xlsx_templates.py

# Templates will be created in: pagination_dash/xlsx_templates/
# - Airoli_pagination_data.xlsx
# - Bhosari_pagination_data.xlsx
# - ... (for all 14 plants)
```

### 2. Distribute Templates

Send each plant their specific Excel file via email or shared drive.

### 3. Validate Returned Files

```bash
# Validate each returned file
python pagination_dash/validate_data.py xlsx_templates/Airoli_pagination_data.xlsx
```

### 4. Import with Dry-Run First

```python
python manage.py shell

# Import from Excel file
from pagination_dash.import_pagination_history import PaginationDataImporter

# Dry run first (validates without importing)
importer = PaginationDataImporter.from_xlsx(
    xlsx_path='xlsx_templates/Airoli_pagination_data.xlsx',
    created_by_username='admin',
    dry_run=True
)
importer.run()

# If validation passes, import for real
importer = PaginationDataImporter.from_xlsx(
    xlsx_path='xlsx_templates/Airoli_pagination_data.xlsx',
    created_by_username='admin',
    dry_run=False
)
importer.run()
```

### 5. Alternative: Import from CSV files

```python
# If using CSV files instead of Excel
from pagination_dash.import_pagination_history import PaginationDataImporter

# Dry run
importer = PaginationDataImporter(
    inhouse_path='csv_templates/Airoli_inhouse.csv',
    competitor_path='csv_templates/Airoli_competitor.csv',
    created_by_username='admin',
    dry_run=True
)
importer.run()

# Actual import
importer = PaginationDataImporter(
    inhouse_path='csv_templates/Airoli_inhouse.csv',
    competitor_path='csv_templates/Airoli_competitor.csv',
    created_by_username='admin',
    dry_run=False
)
importer.run()
```

---

## Support

If you encounter issues:
1. **Check the Reference sheet** in your Excel file
2. **Check this guide** for common errors
3. **Run the validation script** to identify specific issues
4. **Contact the system administrator** with:
   - Your plant name
   - The error message from validation
   - A screenshot of the problematic row

---

## Summary Checklist

Before submitting your Excel file:

- [ ] Deleted example rows (kept only header)
- [ ] Filled all required fields (dark blue headers)
- [ ] Used dropdown arrows for all green header columns
- [ ] Date format is YYYY-MM-DD
- [ ] No duplicate books for the same date
- [ ] Report-level fields (remarks, GNP flags) filled in first row of each date
- [ ] Saved file as .xlsx (not .csv)
- [ ] Ran validation script (optional but recommended)
- [ ] File name matches your plant

---

## Dependencies

For administrators running the scripts:

```bash
# Install required Python package
pip install openpyxl

# This is needed for:
# - generate_xlsx_templates.py (create Excel files)
# - import_pagination_history.py (import from Excel)
# - validate_data.py (validate Excel files)
```
