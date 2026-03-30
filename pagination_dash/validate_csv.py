"""
CSV Validation Utility for Pagination Data Import

This script validates CSV files before import to catch errors early.
It checks:
- Required fields are present
- Date formats are correct
- Choice fields contain valid values
- No duplicate entries (same date + book_name for in-house, same date + competitor for competitor)
- Plant IDs are valid

Usage:
    python pagination_dash/validate_csv.py csv_templates/Airoli_inhouse.csv
    python pagination_dash/validate_csv.py csv_templates/Airoli_competitor.csv --type competitor

Or in Django shell:
    from pagination_dash.validate_csv import CSVValidator
    validator = CSVValidator()
    validator.validate_inhouse_csv('path/to/inhouse.csv')
    validator.validate_competitor_csv('path/to/competitor.csv')
"""

import csv
import os
import sys
from datetime import datetime
from collections import defaultdict


class CSVValidator:
    """Validate pagination CSV files before import"""

    # Valid choices
    BOOK_NAME_CHOICES = [
        'TOI B-1',
        'TOI B-2',
        'TIMS B-1',
        'TIMS B-2',
        'TOI Supp-1',
        'TOI Supp-2',
        'TOI Supp-3',
    ]

    GNP_TYPE_CHOICES = [
        '2 Pg Jkt',
        '4 Pg Jkt - 2 diff clients',
        '4 Pg Vantage',
        '4 Pg Power Jkt',
        '8 Pg Super-pano',
        '6 Pg GNP',
        '8 Pg GNP',
    ]

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

    VALID_PLANT_IDS = [
        'ODBCAIR30', 'ACTIVE42', 'ODBCAIR32', 'MAIN34', 'MAIN38',
        'MAIN35', 'MAIN40', 'ODBCAIR28', 'ACTIVE44', 'MAIN36',
        'MAIN41', 'ODBCAIR33', 'ACTIVE43', 'MAIN37'
    ]

    # Required headers for in-house CSV
    INHOUSE_REQUIRED_HEADERS = [
        'plant_id',
        'plant_name',
        'issue_date',
        'book_name',
    ]

    # Required headers for competitor CSV
    COMPETITOR_REQUIRED_HEADERS = [
        'plant_id',
        'plant_name',
        'issue_date',
        'competitor_name',
    ]

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []

    def reset(self):
        """Reset validation state"""
        self.errors = []
        self.warnings = []
        self.info = []

    def parse_date(self, date_str, row_num):
        """Validate and parse date"""
        if not date_str or date_str.strip() == '':
            self.errors.append(f"Row {row_num}: Missing issue_date")
            return None
        try:
            return datetime.strptime(date_str.strip(), '%Y-%m-%d').date()
        except ValueError:
            self.errors.append(f"Row {row_num}: Invalid date format '{date_str}'. Expected YYYY-MM-DD")
            return None

    def validate_choice(self, value, choices, field_name, row_num, required=False):
        """Validate that value is in allowed choices"""
        if not value or value.strip() == '':
            if required:
                self.errors.append(f"Row {row_num}: Missing required field '{field_name}'")
            return None

        value = value.strip()
        if value not in choices:
            self.errors.append(
                f"Row {row_num}: Invalid {field_name} '{value}'. "
                f"Must be one of: {', '.join(choices)}"
            )
            return None
        return value

    def validate_int(self, value, field_name, row_num, allow_negative=False):
        """Validate integer value"""
        if not value or value.strip() == '':
            return 0  # Default to 0 for optional numeric fields

        try:
            int_val = int(value.strip())
            if not allow_negative and int_val < 0:
                self.warnings.append(f"Row {row_num}: Negative value for {field_name}: {int_val}")
            return int_val
        except ValueError:
            self.errors.append(f"Row {row_num}: Invalid integer for {field_name}: '{value}'")
            return None

    def validate_bool(self, value, field_name, row_num):
        """Validate boolean value"""
        if not value or value.strip() == '':
            return False

        value_lower = value.strip().lower()
        valid_true = ['yes', 'true', '1', 'y']
        valid_false = ['no', 'false', '0', 'n', '']

        if value_lower not in valid_true + valid_false:
            self.warnings.append(
                f"Row {row_num}: Unusual boolean value for {field_name}: '{value}'. "
                f"Expected: yes/no, true/false, 1/0"
            )
        return value_lower in valid_true

    def validate_inhouse_csv(self, csv_path):
        """Validate in-house data CSV"""
        self.reset()
        print(f"\n{'='*80}")
        print(f"VALIDATING IN-HOUSE CSV: {csv_path}")
        print(f"{'='*80}\n")

        if not os.path.exists(csv_path):
            self.errors.append(f"File not found: {csv_path}")
            self._print_results()
            return False

        # Track duplicates
        seen_books = defaultdict(set)  # {(plant_id, issue_date): set(book_names)}
        row_count = 0
        unique_dates = set()
        unique_plants = set()

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames

            # Check required headers
            for header in self.INHOUSE_REQUIRED_HEADERS:
                if header not in headers:
                    self.errors.append(f"Missing required header: {header}")

            if self.errors:
                self._print_results()
                return False

            for row_num, row in enumerate(reader, start=2):
                row_count += 1

                # Validate plant_id
                plant_id = row.get('plant_id', '').strip()
                if not plant_id:
                    self.errors.append(f"Row {row_num}: Missing plant_id")
                elif plant_id not in self.VALID_PLANT_IDS:
                    self.errors.append(f"Row {row_num}: Invalid plant_id '{plant_id}'")
                else:
                    unique_plants.add(plant_id)

                # Validate plant_name
                plant_name = row.get('plant_name', '').strip()
                if not plant_name:
                    self.errors.append(f"Row {row_num}: Missing plant_name")

                # Validate issue_date
                issue_date = self.parse_date(row.get('issue_date', ''), row_num)
                if issue_date:
                    unique_dates.add(issue_date)

                # Validate book_name
                book_name = self.validate_choice(
                    row.get('book_name', ''),
                    self.BOOK_NAME_CHOICES,
                    'book_name',
                    row_num,
                    required=True
                )

                # Check for duplicates
                if plant_id and issue_date and book_name:
                    report_key = (plant_id, issue_date)
                    if book_name in seen_books[report_key]:
                        self.errors.append(
                            f"Row {row_num}: Duplicate book '{book_name}' for {plant_id} on {issue_date}"
                        )
                    else:
                        seen_books[report_key].add(book_name)

                # Validate snp_pages
                self.validate_int(row.get('snp_pages', ''), 'snp_pages', row_num)

                # Validate gnp_pages_type
                gnp_type = row.get('gnp_pages_type', '').strip()
                if gnp_type:
                    self.validate_choice(gnp_type, self.GNP_TYPE_CHOICES, 'gnp_pages_type', row_num)

                # Validate number_of_gnp_jackets
                self.validate_int(row.get('number_of_gnp_jackets', ''), 'number_of_gnp_jackets', row_num)

                # Validate B-2 specific fields
                if book_name in ['TOI B-2', 'TIMS B-2']:
                    self.validate_bool(row.get('balloon_printed', ''), 'balloon_printed', row_num)
                    self.validate_bool(row.get('has_masthead', ''), 'has_masthead', row_num)
                else:
                    # Warn if B-2 fields used on non-B-2 books
                    if row.get('balloon_printed', '').strip():
                        balloon = self.validate_bool(row.get('balloon_printed', ''), 'balloon_printed', row_num)
                        if balloon:
                            self.warnings.append(
                                f"Row {row_num}: balloon_printed will be ignored for {book_name} (only for B-2 books)"
                            )
                    if row.get('has_masthead', '').strip():
                        masthead = self.validate_bool(row.get('has_masthead', ''), 'has_masthead', row_num)
                        if masthead:
                            self.warnings.append(
                                f"Row {row_num}: has_masthead will be ignored for {book_name} (only for B-2 books)"
                            )

        # Summary info
        self.info.append(f"Total rows: {row_count}")
        self.info.append(f"Unique dates: {len(unique_dates)}")
        self.info.append(f"Unique plants: {len(unique_plants)}")
        self.info.append(f"Unique reports (plant+date): {len(seen_books)}")

        self._print_results()
        return len(self.errors) == 0

    def validate_competitor_csv(self, csv_path):
        """Validate competitor data CSV"""
        self.reset()
        print(f"\n{'='*80}")
        print(f"VALIDATING COMPETITOR CSV: {csv_path}")
        print(f"{'='*80}\n")

        if not os.path.exists(csv_path):
            self.errors.append(f"File not found: {csv_path}")
            self._print_results()
            return False

        # Track duplicates
        seen_competitors = defaultdict(set)  # {(plant_id, issue_date): set(competitor_names)}
        row_count = 0
        unique_dates = set()
        unique_plants = set()

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames

            # Check required headers
            for header in self.COMPETITOR_REQUIRED_HEADERS:
                if header not in headers:
                    self.errors.append(f"Missing required header: {header}")

            if self.errors:
                self._print_results()
                return False

            for row_num, row in enumerate(reader, start=2):
                row_count += 1

                # Validate plant_id
                plant_id = row.get('plant_id', '').strip()
                if not plant_id:
                    self.errors.append(f"Row {row_num}: Missing plant_id")
                elif plant_id not in self.VALID_PLANT_IDS:
                    self.errors.append(f"Row {row_num}: Invalid plant_id '{plant_id}'")
                else:
                    unique_plants.add(plant_id)

                # Validate plant_name
                plant_name = row.get('plant_name', '').strip()
                if not plant_name:
                    self.errors.append(f"Row {row_num}: Missing plant_name")

                # Validate issue_date
                issue_date = self.parse_date(row.get('issue_date', ''), row_num)
                if issue_date:
                    unique_dates.add(issue_date)

                # Validate competitor_name
                competitor_name = row.get('competitor_name', '').strip()
                if not competitor_name:
                    self.errors.append(f"Row {row_num}: Missing competitor_name")

                # Check for duplicates
                if plant_id and issue_date and competitor_name:
                    report_key = (plant_id, issue_date)
                    if competitor_name in seen_competitors[report_key]:
                        self.errors.append(
                            f"Row {row_num}: Duplicate competitor '{competitor_name}' for {plant_id} on {issue_date}"
                        )
                    else:
                        seen_competitors[report_key].add(competitor_name)

                # Validate Main book fields
                self.validate_int(row.get('main_snp_pages', ''), 'main_snp_pages', row_num)
                main_gnp_type = row.get('main_gnp_pages_type', '').strip()
                if main_gnp_type:
                    self.validate_choice(main_gnp_type, self.GNP_TYPE_CHOICES, 'main_gnp_pages_type', row_num)
                self.validate_int(row.get('main_number_of_gnp_jacket', ''), 'main_number_of_gnp_jacket', row_num)
                self.validate_int(row.get('main_number_of_books', ''), 'main_number_of_books', row_num)

                # Validate Supplement book fields
                self.validate_int(row.get('supp_snp_pages', ''), 'supp_snp_pages', row_num)
                supp_gnp_type = row.get('supp_gnp_pages_type', '').strip()
                if supp_gnp_type:
                    self.validate_choice(supp_gnp_type, self.GNP_TYPE_CHOICES, 'supp_gnp_pages_type', row_num)
                self.validate_int(row.get('supp_number_of_gnp_jacket', ''), 'supp_number_of_gnp_jacket', row_num)
                self.validate_int(row.get('supp_number_of_books', ''), 'supp_number_of_books', row_num)

                # Validate innovation fields
                for i in range(1, 4):
                    innovation = row.get(f'innovation_{i}', '').strip()
                    if innovation:
                        self.validate_choice(innovation, self.INNOVATION_CHOICES, f'innovation_{i}', row_num)

        # Summary info
        self.info.append(f"Total rows: {row_count}")
        self.info.append(f"Unique dates: {len(unique_dates)}")
        self.info.append(f"Unique plants: {len(unique_plants)}")
        self.info.append(f"Unique competitor entries: {sum(len(v) for v in seen_competitors.values())}")

        self._print_results()
        return len(self.errors) == 0

    def _print_results(self):
        """Print validation results"""
        print("\n📊 Summary:")
        for info in self.info:
            print(f"   {info}")

        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings[:20]:
                print(f"   - {warning}")
            if len(self.warnings) > 20:
                print(f"   ... and {len(self.warnings) - 20} more warnings")

        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors[:30]:
                print(f"   - {error}")
            if len(self.errors) > 30:
                print(f"   ... and {len(self.errors) - 30} more errors")
            print(f"\n❌ VALIDATION FAILED - Please fix errors before importing")
        else:
            print(f"\n✅ VALIDATION PASSED - CSV is ready for import")

        print(f"\n{'='*80}\n")


def main():
    """Main entry point for command line usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Validate pagination CSV files')
    parser.add_argument('csv_file', help='Path to CSV file to validate')
    parser.add_argument(
        '--type', '-t',
        choices=['inhouse', 'competitor', 'auto'],
        default='auto',
        help='Type of CSV file (default: auto-detect from filename)'
    )

    args = parser.parse_args()

    validator = CSVValidator()

    # Auto-detect type from filename if not specified
    csv_type = args.type
    if csv_type == 'auto':
        filename = os.path.basename(args.csv_file).lower()
        if 'competitor' in filename:
            csv_type = 'competitor'
        elif 'inhouse' in filename:
            csv_type = 'inhouse'
        else:
            print("Could not auto-detect CSV type from filename.")
            print("Please specify --type inhouse or --type competitor")
            sys.exit(1)

    if csv_type == 'inhouse':
        success = validator.validate_inhouse_csv(args.csv_file)
    else:
        success = validator.validate_competitor_csv(args.csv_file)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
