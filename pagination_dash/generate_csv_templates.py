"""
Generate CSV Templates for Historical Pagination Data Collection

This script generates per-plant CSV templates for collecting historical pagination data.
Each plant gets 2 CSV files:
1. {plant_name}_inhouse.csv - For books/pagination data
2. {plant_name}_competitor.csv - For competitor data

Usage:
    python manage.py shell < pagination_dash/generate_csv_templates.py

Or run directly:
    python pagination_dash/generate_csv_templates.py
"""

import csv
import os
from datetime import date, timedelta

# Plant configurations
PLANT_DETAILS = [
    {"id": "ODBCAIR30", "name": "Airoli", "display_name": "Airoli"},
    {"id": "ACTIVE42", "name": "Baroda", "display_name": "Baroda"},
    {"id": "ODBCAIR32", "name": "Pune", "display_name": "Bhosari"},
    {"id": "MAIN34", "name": "Bangalore", "display_name": "Bommasandra"},
    {"id": "MAIN38", "name": "Nagpur", "display_name": "Butibori"},
    {"id": "MAIN35", "name": "Chennai", "display_name": "Chemmencherry"},
    {"id": "MAIN40", "name": "Lucknow", "display_name": "Chinhat"},
    {"id": "ODBCAIR28", "name": "Kandivali", "display_name": "Kandivali"},
    {"id": "ACTIVE44", "name": "Manesar", "display_name": "Manesar"},
    {"id": "MAIN36", "name": "Hyderabad", "display_name": "Nacharam"},
    {"id": "MAIN41", "name": "Sahibabad", "display_name": "Sahibabad"},
    {"id": "ODBCAIR33", "name": "Kolkata", "display_name": "Saltlake"},
    {"id": "ACTIVE43", "name": "Trivandrum", "display_name": "Trivandrum"},
    {"id": "MAIN37", "name": "Ahmedabad", "display_name": "Vejalpur"},
]

# GNP publications per plant
PLANT_GNP_PUBLICATIONS = {
    "Airoli": ["Mirror", "MT", "TIMS"],
    "Baroda": [],
    "Bhosari": ["ET", "MT", "TIMS"],
    "Bommasandra": ["ET", "TIMS", "Mirror"],
    "Butibori": [],
    "Chemmencherry": ["ET", "TIMS"],
    "Chinhat": ["ET", "NBT", "TIMS"],
    "Kandivali": ["ET", "MT", "NBT", "Mirror", "TIMS"],
    "Manesar": ["ET", "NBT", "TIMS"],
    "Nacharam": ["ET", "TIMS"],
    "Sahibabad": ["ET", "NBT", "TIMS"],
    "Saltlake": ["ET", "TIMS"],
    "Trivandrum": [],
    "Vejalpur": ["ET", "TIMS"],
}

# Valid book names
BOOK_NAME_CHOICES = [
    'TOI B-1',
    'TOI B-2',
    'TIMS B-1',
    'TIMS B-2',
    'TOI Supp-1',
    'TOI Supp-2',
    'TOI Supp-3',
]

# Valid GNP types
GNP_TYPE_CHOICES = [
    '2 Pg Jkt',
    '4 Pg Jkt - 2 diff clients',
    '4 Pg Vantage',
    '4 Pg Power Jkt',
    '8 Pg Super-pano',
    '6 Pg GNP',
    '8 Pg GNP',
]

# Valid innovation types
INNOVATION_CHOICES = [
    'Center Panorama',
    'Bookmark',
    'Seamless Panorama',
    'Front Vantage',
    'Reverse Flap',
    'Fragrance',
    'French-Window',
    'Power Jacket',
    'Others',
]

# In-house CSV headers
INHOUSE_HEADERS = [
    'plant_id',
    'plant_name',
    'issue_date',
    'book_name',
    'snp_pages',
    'gnp_pages_type',
    'number_of_gnp_jackets',
    'balloon_printed',
    'has_masthead',
    'book_order',
    'remarks_toi',
    'remarks_others',
    'first_time_execution_info',
    'gnp_et',
    'gnp_et_b1',
    'gnp_et_b2',
    'gnp_et_had_2_books',
    'gnp_mt',
    'gnp_mirror',
    'gnp_nbt',
    'gnp_tims',
    'gnp_remarks',
]

# Competitor CSV headers
COMPETITOR_HEADERS = [
    'plant_id',
    'plant_name',
    'issue_date',
    'competitor_name',
    'main_snp_pages',
    'main_gnp_pages_type',
    'main_number_of_gnp_jacket',
    'main_number_of_books',
    'supp_snp_pages',
    'supp_gnp_pages_type',
    'supp_number_of_gnp_jacket',
    'supp_number_of_books',
    'innovation_1',
    'innovation_2',
    'innovation_3',
    'comment',
]


def get_example_date():
    """Get a sample date string"""
    return "2023-01-01"


def generate_inhouse_example_rows(plant_id, plant_name, plant_display_name):
    """Generate example rows for in-house CSV"""
    example_date = get_example_date()
    gnp_pubs = PLANT_GNP_PUBLICATIONS.get(plant_display_name, [])
    has_et = 'ET' in gnp_pubs
    has_mt = 'MT' in gnp_pubs
    has_mirror = 'Mirror' in gnp_pubs
    has_nbt = 'NBT' in gnp_pubs
    has_tims = 'TIMS' in gnp_pubs

    # Create example rows for standard books
    rows = []

    # TOI B-1 example
    rows.append({
        'plant_id': plant_id,
        'plant_name': plant_display_name,
        'issue_date': example_date,
        'book_name': 'TOI B-1',
        'snp_pages': '24',
        'gnp_pages_type': '4 Pg Vantage',
        'number_of_gnp_jackets': '1',
        'balloon_printed': '',
        'has_masthead': '',
        'book_order': '0',
        'remarks_toi': 'Example remark for TOI',
        'remarks_others': 'Example remark for others',
        'first_time_execution_info': '',
        'gnp_et': 'Yes' if has_et else '',
        'gnp_et_b1': '',
        'gnp_et_b2': '',
        'gnp_et_had_2_books': '',
        'gnp_mt': 'Yes' if has_mt else '',
        'gnp_mirror': '' if not has_mirror else '',
        'gnp_nbt': '' if not has_nbt else '',
        'gnp_tims': 'Yes' if has_tims else '',
        'gnp_remarks': '',
    })

    # TOI B-2 example (with B-2 specific fields)
    rows.append({
        'plant_id': plant_id,
        'plant_name': plant_display_name,
        'issue_date': example_date,
        'book_name': 'TOI B-2',
        'snp_pages': '16',
        'gnp_pages_type': '',
        'number_of_gnp_jackets': '0',
        'balloon_printed': 'Yes',
        'has_masthead': 'Yes',
        'book_order': '1',
        'remarks_toi': '',
        'remarks_others': '',
        'first_time_execution_info': '',
        'gnp_et': '',
        'gnp_et_b1': '',
        'gnp_et_b2': '',
        'gnp_et_had_2_books': '',
        'gnp_mt': '',
        'gnp_mirror': '',
        'gnp_nbt': '',
        'gnp_tims': '',
        'gnp_remarks': '',
    })

    # TIMS B-1 example
    rows.append({
        'plant_id': plant_id,
        'plant_name': plant_display_name,
        'issue_date': example_date,
        'book_name': 'TIMS B-1',
        'snp_pages': '20',
        'gnp_pages_type': '',
        'number_of_gnp_jackets': '0',
        'balloon_printed': '',
        'has_masthead': '',
        'book_order': '2',
        'remarks_toi': '',
        'remarks_others': '',
        'first_time_execution_info': '',
        'gnp_et': '',
        'gnp_et_b1': '',
        'gnp_et_b2': '',
        'gnp_et_had_2_books': '',
        'gnp_mt': '',
        'gnp_mirror': '',
        'gnp_nbt': '',
        'gnp_tims': '',
        'gnp_remarks': '',
    })

    return rows


def generate_competitor_example_rows(plant_id, plant_name, plant_display_name):
    """Generate example rows for competitor CSV"""
    example_date = get_example_date()

    rows = []

    # Example competitor row
    rows.append({
        'plant_id': plant_id,
        'plant_name': plant_display_name,
        'issue_date': example_date,
        'competitor_name': 'Sample Competitor',
        'main_snp_pages': '24',
        'main_gnp_pages_type': '4 Pg Vantage',
        'main_number_of_gnp_jacket': '1',
        'main_number_of_books': '2',
        'supp_snp_pages': '8',
        'supp_gnp_pages_type': '',
        'supp_number_of_gnp_jacket': '0',
        'supp_number_of_books': '1',
        'innovation_1': 'Center Panorama',
        'innovation_2': '',
        'innovation_3': '',
        'comment': 'Example comment',
    })

    return rows


def generate_reference_sheet(output_dir):
    """Generate a reference sheet with all valid values"""
    ref_file = os.path.join(output_dir, '_REFERENCE_VALID_VALUES.txt')

    with open(ref_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("PAGINATION DATA COLLECTION - VALID VALUES REFERENCE\n")
        f.write("=" * 80 + "\n\n")

        f.write("BOOK NAMES (book_name column):\n")
        f.write("-" * 40 + "\n")
        for name in BOOK_NAME_CHOICES:
            f.write(f"  - {name}\n")
        f.write("\n")

        f.write("GNP PAGE TYPES (gnp_pages_type columns):\n")
        f.write("-" * 40 + "\n")
        for gnp_type in GNP_TYPE_CHOICES:
            f.write(f"  - {gnp_type}\n")
        f.write("\n")

        f.write("INNOVATION TYPES (innovation_1/2/3 columns):\n")
        f.write("-" * 40 + "\n")
        for innovation in INNOVATION_CHOICES:
            f.write(f"  - {innovation}\n")
        f.write("\n")

        f.write("BOOLEAN VALUES (balloon_printed, has_masthead, gnp_* columns):\n")
        f.write("-" * 40 + "\n")
        f.write("  - Yes or TRUE or 1 = True\n")
        f.write("  - No or FALSE or 0 or empty = False\n")
        f.write("\n")

        f.write("DATE FORMAT (issue_date column):\n")
        f.write("-" * 40 + "\n")
        f.write("  - YYYY-MM-DD (e.g., 2023-01-15)\n")
        f.write("\n")

        f.write("PLANT GNP PUBLICATIONS:\n")
        f.write("-" * 40 + "\n")
        for plant, pubs in PLANT_GNP_PUBLICATIONS.items():
            if pubs:
                f.write(f"  {plant}: {', '.join(pubs)}\n")
            else:
                f.write(f"  {plant}: (No GNP publications)\n")
        f.write("\n")

        f.write("=" * 80 + "\n")
        f.write("NOTES:\n")
        f.write("=" * 80 + "\n")
        f.write("1. balloon_printed and has_masthead are only applicable for TOI B-2 and TIMS B-2\n")
        f.write("2. gnp_et_b1, gnp_et_b2, gnp_et_had_2_books are only for plants with ET publication\n")
        f.write("3. Report-level fields (remarks, GNP flags) only need to be filled in the first\n")
        f.write("   book row for each date - they will be ignored in subsequent rows\n")
        f.write("4. Competitor data must be imported AFTER in-house data for the same dates\n")
        f.write("\n")

    print(f"  Created: {ref_file}")


def generate_plant_templates(output_dir):
    """Generate CSV templates for all plants"""
    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "=" * 80)
    print("GENERATING CSV TEMPLATES")
    print("=" * 80 + "\n")

    for plant in PLANT_DETAILS:
        plant_id = plant['id']
        plant_name = plant['name']
        plant_display_name = plant['display_name']

        # Generate in-house CSV
        inhouse_file = os.path.join(output_dir, f"{plant_display_name}_inhouse.csv")
        with open(inhouse_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=INHOUSE_HEADERS)
            writer.writeheader()

            # Write example rows
            example_rows = generate_inhouse_example_rows(plant_id, plant_name, plant_display_name)
            for row in example_rows:
                writer.writerow(row)

        print(f"  Created: {inhouse_file}")

        # Generate competitor CSV
        competitor_file = os.path.join(output_dir, f"{plant_display_name}_competitor.csv")
        with open(competitor_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=COMPETITOR_HEADERS)
            writer.writeheader()

            # Write example rows
            example_rows = generate_competitor_example_rows(plant_id, plant_name, plant_display_name)
            for row in example_rows:
                writer.writerow(row)

        print(f"  Created: {competitor_file}")

    # Generate reference sheet
    generate_reference_sheet(output_dir)

    print("\n" + "=" * 80)
    print(f"COMPLETED: Generated {len(PLANT_DETAILS) * 2} CSV files + 1 reference file")
    print(f"Output directory: {output_dir}")
    print("=" * 80 + "\n")


def main():
    """Main entry point"""
    # Determine output directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, 'csv_templates')

    generate_plant_templates(output_dir)

    print("Instructions for users:")
    print("-" * 40)
    print("1. Open your plant's _inhouse.csv file")
    print("2. Delete the example rows (keep the header)")
    print("3. Add your historical data (one row per book per date)")
    print("4. Save the file")
    print("5. Repeat for the _competitor.csv file")
    print("6. Return the completed files for import")
    print()


if __name__ == '__main__':
    main()
