from abc import ABC, abstractmethod
from datetime import date, timedelta
import requests
import pandas as pd
import re
import numpy as np
from django.db import models
from .models import ProductionReport, BookWiseDetails, Downtime


def download_from_pi(report_name, plant_id, data_from_date=None, data_to_date=None):
    report_data = {
        "production_report": {
            "url": "Production%20Report%20(Rundate)",
            "report_sheets": ["General", "Book Wise Details", "Down Time", "Web Break", "Reel Consumption"],
            "report_date": date.today() - timedelta(days=1)
        },
        "ctp_report": {
            "url": "CTP%20Report",
            "report_sheets": ["General", "Plate Issues", "Re-Plate Issues"],
            "report_date": date.today()
        }
    }
    report = report_data.get(report_name)
    report_type = report.get("url")
    report_date = report.get("report_date").strftime("%Y-%m-%d")
    if data_from_date and data_to_date:
        url = "http://pi40da.timesgroup.com/api/v1/myFile?fromDate={}&toDate={}&plantId={}&type={}".format(
            data_from_date,
            data_to_date,
            plant_id,
            report_type
        )
    else:
        url = "http://pi40da.timesgroup.com/api/v1/myFile?fromDate={}&toDate={}&plantId={}&type={}".format(
            report_date,
            report_date,
            plant_id,
            report_type
        )
    print(url)
    resonse = requests.get(url)
    if resonse.status_code == 200:
        return resonse
    else:
        print("Error in request")
        return None


def print_missing_columns_df(missing_columns, df_name):
    if missing_columns:
        print(f"Added the following missing columns with NULL values in {df_name}:")
        for col in missing_columns:
            print(f"- {col}")
    else:
        print(f"All model fields were present in the {df_name} DataFrame")


class DataHandler(ABC):
    def __init__(self, report_sheet) -> None:
        super().__init__()
        self.report_sheet = report_sheet

    def fetch_data(self, resonse, sheet_name):
        df = pd.read_excel(resonse.content, engine='openpyxl', sheet_name=sheet_name)
        return df

    @abstractmethod
    def rename_columns(self, df):
        """
        Clean and standardize DataFrame column names based on the following rules:
        1. Remove '&' characters, Replace '%' with 'Percentage'
        2. Replace special characters with spaces, Trim extra whitespace
        3.Replace remaining spaces with underscores
        Parameters:
        df (pandas.DataFrame): Input DataFrame
        Returns:
        pandas.DataFrame: DataFrame with cleaned column names
        """
        # Create a copy of the DataFrame to avoid modifying the original
        df_cleaned = df.copy()

        # Function to clean individual column names
        def clean_name(col_name):
            # Convert to string in case of numeric column names
            col_name = str(col_name)

            # Remove '&' characters
            cleaned = col_name.replace('&', '')

            # Replace '%' with 'Percentage'
            cleaned = cleaned.replace('%', 'Percentage')

            # Replace special characters with spaces
            # This keeps alphanumeric characters and replaces everything else with spaces
            cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', cleaned)

            # Trim extra whitespace and replace remaining spaces with underscores
            cleaned = ' '.join(cleaned.split())
            cleaned = cleaned.replace(' ', '_')

            return cleaned

        # Apply the cleaning function to all column names
        df_cleaned.columns = [clean_name(col) for col in df_cleaned.columns]
        df_cleaned.columns = df_cleaned.columns.str.lower()  # Convert all column names to lowercase before uploading

        return df_cleaned

    @abstractmethod
    def clean_data(self, df):
        pass

    def align_dataframe_with_model(self, df, model_class):
        """
        Aligns DataFrame columns with Django model fields.
        Adds missing columns with NULL values if they don't exist in DataFrame.

        Args:
            df: pandas DataFrame
            model_class: Django model class

        Returns:
            pandas DataFrame aligned with model fields
        """
        # Get all field names from the model (excluding Meta and other special attributes)
        model_fields = [
            field.name for field in model_class._meta.get_fields()
            if not field.is_relation  # Exclude relationship fields if any
        ]

        # Convert DataFrame columns to lowercase for consistency
        df.columns = df.columns.str.lower()

        # Initialize a dictionary to store missing fields and their default values
        missing_fields = {}

        # Check each model field
        for field_name in model_fields:
            if field_name not in df.columns and field_name != 'id':
                # Determine appropriate default value based on field type
                field = model_class._meta.get_field(field_name)

                if isinstance(field, models.BooleanField):
                    default_value = False
                elif isinstance(field, models.IntegerField):
                    default_value = None
                elif isinstance(field, models.DecimalField):
                    default_value = None
                elif isinstance(field, (models.DateField, models.TimeField, models.DateTimeField)):
                    default_value = None
                else:
                    default_value = None

                missing_fields[field_name] = default_value

        # Add missing columns to DataFrame
        for field_name, default_value in missing_fields.items():
            df[field_name] = default_value

        # Return the modified DataFrame
        return df, list(missing_fields.keys())

    def convert_decimal_with_nan(self, df, column_name):
        """
        Converts a column to decimal format while properly handling NaN values.

        Args:
            df: pandas DataFrame
            column_name: name of the column to convert

        Returns:
            Series with converted values
        """
        # Create a copy of the column
        converted_series = df[column_name].copy()

        # Replace NaN with None (will become NULL in database)
        converted_series = converted_series.where(pd.notna(converted_series), None)

        # For non-None values, ensure they are proper decimals
        mask = converted_series.notna()
        if mask.any():
            converted_series[mask] = pd.to_numeric(converted_series[mask], errors='coerce')

        return converted_series.fillna(0)

    def convert_dataframe_types(self, df, model_class):
        """
        Converts DataFrame column types to match Django model field types.
        """
        df = df.copy()
        df.columns = df.columns.str.lower()

        # Get field types from model
        model_fields = {
            field.name: field
            for field in model_class._meta.get_fields()
            if not field.is_relation
        }

        type_conversion_errors = []

        for column in df.columns:
            if column in model_fields:
                field = model_fields[column]
                try:
                    if isinstance(field, models.DecimalField):
                        # Use the special conversion for decimal fields
                        df[column] = self.convert_decimal_with_nan(df, column)

                    elif isinstance(field, models.CharField) or isinstance(field, models.TextField):
                        df[column] = df[column].astype(str)
                        df[column] = df[column].replace('nan', None)

                    elif isinstance(field, models.IntegerField):
                        numeric_col = pd.to_numeric(df[column], errors='coerce')
                        if not field.null:
                            # For non-nullable fields, fill NaNs with 0, round, then cast to standard int
                            df[column] = numeric_col.fillna(0).round().astype(int)
                        else:
                            # For nullable fields, round then cast to nullable Int64.
                            # .round() preserves NaNs, which .astype('Int64') handles correctly.
                            df[column] = numeric_col.round().astype('Int64')


                    elif isinstance(field, models.BooleanField):
                        # Convert various truth values to boolean
                        df[column] = df[column].map({
                            True: True, 'True': True, 'true': True, '1': True, 1: True,
                            False: False, 'False': False, 'false': False, '0': False, 0: False,
                            'Yes': True, 'No': False, 'YES': True, 'NO': False,
                            'nan': None, 'null': None, 'NULL': None, np.nan: None
                        })

                except Exception as e:
                    type_conversion_errors.append({
                        'column': column,
                        'error': str(e)
                    })
        return df, type_conversion_errors

    def upload_to_db(self, df, model_class):
        """
        Uploads DataFrame records to the database using update_or_create.
        This method now assumes the primary key is present in the DataFrame.
        """
        model_field_names = {f.name for f in model_class._meta.get_fields()}
        records = df.to_dict('records')
        if self.report_sheet == "Reel Consumption":
            print(records)
        for record in records:
            pk_field = model_class._meta.pk.name
            pk_value = record.get(pk_field)

            if pk_value is None:
                print(f"Skipping record due to missing primary key '{pk_field}': {record}")
                continue

            # Separate pk for lookup and data for update/create
            lookup = {pk_field: pk_value}

            # Filter the record to only include keys that are actual model fields
            defaults = {k: v for k, v in record.items() if k in model_field_names and k != pk_field}

            # Fill NaN with None for database
            for key, value in defaults.items():
                if pd.isna(value):
                    defaults[key] = None

            obj, created = model_class.objects.update_or_create(
                defaults=defaults,
                **lookup
            )

    def execute(self, data_from_pi, db_model):
        response_df = self.fetch_data(data_from_pi, self.report_sheet)
        if response_df.empty:
            return []
        df_renamed = self.rename_columns(response_df)
        df_cleaned = self.clean_data(df_renamed)

        # Drop rows where the foreign key is null before proceeding
        if 'issueid' in df_cleaned.columns:
            df_cleaned.dropna(subset=['issueid'], inplace=True)

        aligned_df, missing_columns = self.align_dataframe_with_model(df_cleaned, db_model)
        # Convert types
        converted_df, conversion_errors = self.convert_dataframe_types(aligned_df, db_model)

        if conversion_errors:
            print("Type conversion errors occurred:")
            for error in conversion_errors:
                print(f"Column: {error['column']}, Error: {error['error']}")

        if not conversion_errors:
            print(f"All data types for {self.report_sheet} converted successfully!")
            self.upload_to_db(converted_df, db_model)

        return missing_columns


class GeneralProductionHandler(DataHandler):

    def rename_columns(self, df):
        df_renamed = super().rename_columns(df)
        df_renamed.rename(columns={'w_b_s': 'wb_s', 'user': 'user_name'}, inplace=True)
        return df_renamed

    def clean_data(self, df):
        # --- Standard data cleaning ---
        df['folders_count'] = np.where(df['production_type'] == '>', 1, 2)
        df['uv_run'] = df['uv'].map({'Yes': True, 'No': False})
        df['sum_of_pages'] = df['sum_of_pages'].round()
        df["issue_date"] = pd.to_datetime(df["issue_date"], format="%d-%m-%Y")
        df["run_date"] = pd.to_datetime(df["run_date"], format="%d-%m-%Y")
        df["production_start"] = pd.to_datetime(df["production_start_date"].str.cat(df["production_start"], sep=' '),
                                                format="%d/%m/%Y %H:%M")
        df["production_start"] = df["production_start"].dt.tz_localize('Asia/Kolkata')
        df["production_end"] = pd.to_datetime(df["production_end_date"].str.cat(df["production_end"], sep=' '),
                                              format="%d/%m/%Y %H:%M")
        df["production_end"] = df["production_end"].dt.tz_localize('Asia/Kolkata')
        df['production_start_date'] = pd.to_datetime(df["production_start_date"], format="%d/%m/%Y")
        df["production_end_date"] = pd.to_datetime(df["production_end_date"], format="%d/%m/%Y")
        df["entry_time"] = pd.to_datetime(df["entry_time"], format="%d/%m/%Y %I:%M %p")
        df["entry_time"] = df["entry_time"].dt.tz_localize('Asia/Kolkata')

        # --- Logic for the new 'toi_city' field ---
        plant_details = [
            {"id": "ODBCAIR30", "name": "Airoli", "display_name": "Airoli",
             "toi_city": ["TIMES OF INDIA-MUMBAI (CITY-2)", "TOI - Navi Mum", "THE TIMES OF INDIA - THANE CITY"]},
            {"id": "ACTIVE42", "name": "Baroda", "display_name": "Baroda",
             "toi_city": ["TIMES OF INDIA - AHD", "TIMES OF INDIA-AHD"]},
            {"id": "ODBCAIR32", "name": "Pune", "display_name": "Bhosari",
             "toi_city": ["TIMES OF INDIA - PUNE (CITY)"]},
            {"id": "MAIN34", "name": "Bangalore", "display_name": "Bommasandra",
             "toi_city": ["TIMES OF INDIA - BANGALORE (METRO"]},
            {"id": "MAIN38", "name": "Nagpur", "display_name": "Butibori", "toi_city": ["TIMES OF INDIA"]},
            {"id": "MAIN35", "name": "Chennai", "display_name": "Chemmencherry",
             "toi_city": ["TIMES OF INDIA - CHENNAI", "SUNDAY TIMES OF INDIA-CHENNAI"]},
            {"id": "MAIN40", "name": "Lucknow", "display_name": "Chinhat",
             "toi_city": ["TIMES OF INDIA - LUCKNOW (CAPITAL)", "TIMES OF INDIA  - LUCKNOW (CAP"]},
            {"id": "ODBCAIR28", "name": "Kandivali", "display_name": "Kandivali",
             "toi_city": ["TIMES OF INDIA-MUMBAI (CITY-2)"]},
            {"id": "ACTIVE44", "name": "Manesar", "display_name": "Manesar",
             "toi_city": ["TIMES OF INDIA - GURGAON", "Sunday Times- Gurgaon"]},
            {"id": "MAIN36", "name": "Hyderabad", "display_name": "Nacharam",
             "toi_city": ["TIMES OF INDIA - HYDERBAD (CITY)", "SUNDAY TIMES OF INDIA"]},
            {"id": "MAIN41", "name": "Sahibabad", "display_name": "Sahibabad",
             "toi_city": ["TIMES OF INDIA - DELHI (CAP"]},
            {"id": "ODBCAIR33", "name": "Kolkata", "display_name": "Saltlake",
             "toi_city": ["TIMES OF INDIA - KOLKATA (LATE"]},
            {"id": "ACTIVE43", "name": "Trivandrum", "display_name": "Trivandrum", "toi_city": ["TIMES OF INDIA"]},
            {"id": "MAIN37", "name": "Ahmedabad", "display_name": "Vejalpur",
             "toi_city": ["TIMES OF INDIA - AHMEDABAD LATE CITY", "SUNDAY TIMES OF INDIA - AHMEDABAD (CITY"]},
        ]

        # Create a mapping for efficient lookup
        plant_to_city_map = {plant['display_name']: plant['toi_city'] for plant in plant_details}

        def check_toi_city(row):
            plant_name = row['plant_name']
            products = str(row['products']).upper()  # Ensure products is a string and uppercase

            # Get the list of city strings for the plant
            city_list = plant_to_city_map.get(plant_name)

            if city_list:
                # Check if any city string is in the products string
                for city_string in city_list:
                    if city_string.upper() in products:
                        return True
            return False

        # Apply the function to create the new column
        df['toi_city'] = df.apply(check_toi_city, axis=1)

        return df


class InnovationProductionHandler(DataHandler):
    parent_class = ProductionReport

    def rename_columns(self, df):
        return super().rename_columns(df)

    def clean_data(self, df):
        df["issue_date"] = pd.to_datetime(df["issue_date"], format="%Y-%m-%d")

        # Map issueid to ProductionReport instances
        issue_ids = df['issueid'].dropna().unique()
        production_reports = self.parent_class.objects.filter(issueid__in=issue_ids)
        report_mapping = {str(report.issueid): report for report in production_reports}

        df['issueid_fk'] = df['issueid'].map(report_mapping)
        df.dropna(subset=['issueid_fk'], inplace=True)

        # Generate the composite primary key using the original issueid and a row index
        df.reset_index(inplace=True)
        df['innovation_id'] = df.apply(
            lambda row: f"{row['issueid']}_{row['index']}",
            axis=1
        )

        # Rename the foreign key column to 'issueid' for the model
        df = df.rename(columns={'issueid_fk': 'issueid'})

        return df


class BookWiseDetailsHandler(DataHandler):
    parent_class = ProductionReport

    def rename_columns(self, df):
        df_renamed = super().rename_columns(df)
        df_renamed.rename(columns={'issue_id': 'issueid'}, inplace=True)
        return df_renamed

    def clean_data(self, df):
        # Date and time conversions
        df['issue_date'] = pd.to_datetime(df['issue_date'], format='%d-%m-%Y')
        df['run_date'] = pd.to_datetime(df['run_date'], format='%d-%m-%Y')

        # Combine date and time columns and then convert to datetime
        df['start_datetime'] = pd.to_datetime(df['start_date'] + ' ' + df['start_time'], format='%Y-%m-%d %H:%M',
                                              errors='coerce')
        df['start_datetime'] = df['start_datetime'].dt.tz_localize('Asia/Kolkata')
        df['end_datetime'] = pd.to_datetime(df['end_date'] + ' ' + df['end_time'], format='%Y-%m-%d %H:%M',
                                            errors='coerce')
        df['end_datetime'] = df['end_datetime'].dt.tz_localize('Asia/Kolkata')

        # Convert other datetime fields
        df['editorial_release'] = pd.to_datetime(df['editorial_release'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
        df['editorial_release'] = df['editorial_release'].dt.tz_localize('Asia/Kolkata')
        df['first_tiff'] = pd.to_datetime(df['first_tiff'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
        df['first_tiff'] = df['first_tiff'].dt.tz_localize('Asia/Kolkata')
        df['last_tiff'] = pd.to_datetime(df['last_tiff'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
        df['last_tiff'] = df['last_tiff'].dt.tz_localize('Asia/Kolkata')
        df['last_plate'] = pd.to_datetime(df['last_plate'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
        df['last_plate'] = df['last_plate'].dt.tz_localize('Asia/Kolkata')
        df['entry_time'] = pd.to_datetime(df['entry_time'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
        df['entry_time'] = df['entry_time'].dt.tz_localize('Asia/Kolkata')

        # Map issueid to ProductionReport instances
        issue_ids = df['issueid'].dropna().unique()
        production_reports = self.parent_class.objects.filter(issueid__in=issue_ids)
        report_mapping = {str(report.issueid): report for report in production_reports}

        df['issueid'] = df['issueid'].map(report_mapping)

        # Drop the original columns that have been combined
        df.drop(columns=['start_date', 'start_time', 'end_date', 'end_time'], inplace=True, errors='ignore')

        return df


class DowntimeHandler(DataHandler):
    parent_class = ProductionReport

    def rename_columns(self, df):
        df_renamed = super().rename_columns(df)
        return df_renamed

    def clean_data(self, df):
        # Date and time conversions
        df['edition_date'] = pd.to_datetime(df['edition_date'], format='%Y-%m-%d', errors='coerce')
        df['run_date'] = pd.to_datetime(df['run_date'], format='%d-%m-%Y', errors='coerce')

        # Convert time columns, handling potential errors
        df['start_time'] = pd.to_datetime(df['start_time'], format='%H:%M', errors='coerce').dt.time
        df['end_time'] = pd.to_datetime(df['end_time'], format='%H:%M', errors='coerce').dt.time

        # This line correctly handles nulls from the source data.
        # The errors='coerce' argument turns any unparseable values into NaT (Not a Time),
        # which Django correctly interprets as NULL for a nullable database column.
        df['follow_up_date'] = pd.to_datetime(df['follow_up_date'], errors='coerce')

        # Map issueid to ProductionReport instances
        issue_ids = df['issueid'].dropna().unique()
        production_reports = self.parent_class.objects.filter(issueid__in=issue_ids)
        report_mapping = {str(report.issueid): report for report in production_reports}

        df['issueid_fk'] = df['issueid'].map(report_mapping)
        df.dropna(subset=['issueid_fk'], inplace=True)

        # Generate the composite primary key using the original issueid and a row index
        df.reset_index(inplace=True)
        df['downtime_id'] = df.apply(
            lambda row: f"{row['issueid']}_{row['index']}",
            axis=1
        )

        # Rename the foreign key column to 'issueid' for the model
        df = df.rename(columns={'issueid_fk': 'issueid'})

        return df


class WebBreakHandler(DataHandler):
    parent_class = ProductionReport

    def rename_columns(self, df):
        df_renamed = super().rename_columns(df)
        return df_renamed

    def clean_data(self, df):
        # Date and time conversions
        df['edition_date'] = pd.to_datetime(df['edition_date'], format='%Y-%m-%d', errors='coerce')
        df['run_date'] = pd.to_datetime(df['run_date'], format='%d-%m-%Y', errors='coerce')

        # Map issueid to ProductionReport instances
        issue_ids = df['issueid'].dropna().unique()
        production_reports = self.parent_class.objects.filter(issueid__in=issue_ids)
        report_mapping = {str(report.issueid): report for report in production_reports}

        df['issueid_fk'] = df['issueid'].map(report_mapping)
        df.dropna(subset=['issueid_fk'], inplace=True)

        # Generate the composite primary key using the original issueid and a row index
        df.reset_index(inplace=True)
        df['web_break_id'] = df.apply(
            lambda row: f"{row['issueid']}_{row['index']}",
            axis=1
        )

        # Rename the foreign key column to 'issueid' for the model
        df = df.rename(columns={'issueid_fk': 'issueid'})

        return df


class ReelConsumptionHandler(DataHandler):
    parent_class = ProductionReport

    def rename_columns(self, df):
        df_renamed = super().rename_columns(df)
        df_renamed.rename(columns={'production_type': 'production_type_folder'}, inplace=True)
        return df_renamed

    def clean_data(self, df):
        # Date and time conversions
        df['edition_date'] = pd.to_datetime(df['edition_date'], format='%Y-%m-%d', errors='coerce')

        # Map issueid to ProductionReport instances
        issue_ids = df['issueid'].dropna().unique()
        production_reports = self.parent_class.objects.filter(issueid__in=issue_ids)
        report_mapping = {str(report.issueid): report for report in production_reports}

        df['issueid_fk'] = df['issueid'].map(report_mapping)
        df.dropna(subset=['issueid_fk'], inplace=True)

        # Generate the composite primary key using the original issueid and a row index
        df.reset_index(inplace=True)
        df['reel_consumption_id'] = df.apply(
            lambda row: f"{row['issueid']}_{row['index']}",
            axis=1
        )

        # Rename the foreign key column to 'issueid' for the model
        df = df.rename(columns={'issueid_fk': 'issueid'})
        return df
