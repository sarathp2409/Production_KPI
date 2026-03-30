from abc import ABC, abstractmethod
from datetime import date, timedelta
import requests
import pandas as pd
import re
import numpy as np
from django.db import models
from .models import ProductionReport


def download_from_pi(report_name, plant_id, data_from_date=None, data_to_date=None):
    report_data = {
        "production_report" : {
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
        url =  "http://pi40da.timesgroup.com/api/v1/myFile?fromDate={}&toDate={}&plantId={}&type={}".format(
            data_from_date, 
            data_to_date, 
            plant_id, 
            report_type
        )
    else:
        url =  "http://pi40da.timesgroup.com/api/v1/myFile?fromDate={}&toDate={}&plantId={}&type={}".format(
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
    def clean_data(self):
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
                        df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int64')
                    
                    
                    elif isinstance(field, models.BooleanField):
                        # Convert various truth values to boolean
                        df[column] = df[column].map({
                            True: True, 'True': True, 'true': True, '1': True, 1: True,
                            False: False, 'False': False, 'false': False, '0': False, 0: False,
                            'Yes': True, 'No': False, 'YES': True, 'NO': False,
                            'nan': None, 'null': None, 'NULL': None, np.nan: None
                        })
                    
                    # elif isinstance(field, models.DateField):
                    #     # Convert to datetime first, then extract date
                    #     df[column] = pd.to_datetime(df[column], format="%d/%m/%Y", errors='coerce').dt.date
                        
                    # elif isinstance(field, models.TimeField):
                    #     # Convert to datetime first, then extract time
                    #     df[column] = pd.to_datetime(df[column], errors='coerce').dt.time
                        
                    # elif isinstance(field, models.DateTimeField):
                    #     df[column] = pd.to_datetime(df[column], format="%d/%m/%Y %I:%M %p", errors='coerce')
                    
                except Exception as e:
                    type_conversion_errors.append({
                        'column': column,
                        'error': str(e)
                    })
        
        return df, type_conversion_errors

    def validate_data_types(self, df, model_class):
        """
        Validates that all data types in the DataFrame match the model field types.
        """
        validation_errors = []
        
        for field in model_class._meta.get_fields():
            if not field.is_relation and field.name in df.columns:
                column = df[field.name]
                
                # Check for required fields with null values
                if not field.null and column.isnull().any():
                    validation_errors.append(
                        f"Column '{field.name}' contains NULL values but is required"
                    )
                
                # Check character field lengths
                if isinstance(field, models.CharField):
                    max_length = field.max_length
                    if column.str.len().max() > max_length:
                        validation_errors.append(
                            f"Column '{field.name}' contains values exceeding max_length of {max_length}"
                        )
        
        return validation_errors

    def upload_to_db(self, df, model_class):
        records = df.to_dict('records')
        # Use update_or_create to avoid duplicates based on primary key
        for record in records:
            pk_field = model_class._meta.pk.name
            pk_value = record.get(pk_field)
            if pk_value is None:
                continue  # Or handle error

            # Separate pk for lookup and data for update/create
            lookup = {pk_field: pk_value}
            defaults = {k: v for k, v in record.items() if k != pk_field}

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
        df_renamed = self.rename_columns(response_df)
        df_cleaned = self.clean_data(df_renamed)
        aligned_df, missing_columns = self.align_dataframe_with_model(df_cleaned, db_model)  
        # Convert types
        converted_df, conversion_errors = self.convert_dataframe_types(aligned_df, db_model)
        
        if conversion_errors:
            print("Type conversion errors occurred:")
            for error in conversion_errors:
                print(f"Column: {error['column']}, Error: {error['error']}")
        
        # # Validate data
        # validation_errors = self.validate_data_types(converted_df, db_model)
        
        # if validation_errors:
        #     print("\nValidation errors found:")
        #     for error in validation_errors:
        #         print(error)
        
        if not conversion_errors:
            print("All data types converted successfully!")
            self.upload_to_db(converted_df, db_model)
        
        return missing_columns


class GeneralProductionHandler(DataHandler):

    def rename_columns(self, df):
        df_renamed = super().rename_columns(df)
        df_renamed.rename(columns={'w_b_s' : 'wb_s', 'user': 'user_name'}, inplace=True)
        return df_renamed
    
    def clean_data(self, df):
        super().clean_data()
        df['folders_count'] = np.where(df['production_type'] == '>', 1, 2)
        df['uv_run'] = df['uv'].map({'Yes': True, 'No': False})
        df['sum_of_pages'] = df['sum_of_pages'].round()
        df["issue_date"] = pd.to_datetime(df["issue_date"], format="%d-%m-%Y")
        df["run_date"] = pd.to_datetime(df["run_date"], format="%d-%m-%Y")
        df["production_start"] = pd.to_datetime(df["production_start_date"].str.cat(df["production_start"], sep=' '), format="%d/%m/%Y %H:%M")
        df["production_start"] = df["production_start"].dt.tz_localize('Asia/Kolkata')
        df["production_end"] = pd.to_datetime(df["production_end_date"].str.cat(df["production_end"], sep=' '), format="%d/%m/%Y %H:%M")
        df["production_end"] = df["production_end"].dt.tz_localize('Asia/Kolkata')
        df['production_start_date'] = pd.to_datetime(df["production_start_date"], format="%d/%m/%Y")
        df["production_end_date"] = pd.to_datetime(df["production_end_date"], format="%d/%m/%Y")
        df["entry_time"] = pd.to_datetime(df["entry_time"], format="%d/%m/%Y %I:%M %p")
        df["entry_time"] = df["entry_time"].dt.tz_localize('Asia/Kolkata')
        return df


class InnovationProductionHandler(DataHandler):
    parent_class = ProductionReport
    
    def rename_columns(self, df):
        return super().rename_columns(df)

    def clean_data(self, df):
        super().clean_data()
        df["issue_date"] = pd.to_datetime(df["issue_date"], format="%Y-%m-%d")
        """
        Prepare innovation dataframe by mapping issueid to ProductionReport instances
        and restructuring the dataframe for Django ORM usage.
        
        Args:
            df (pd.DataFrame): Input dataframe with issueid column
            
        Returns:
            pd.DataFrame: Processed dataframe ready for Django ORM
        """, 
        # Create a dictionary mapping issueid strings to ProductionReport instances
        issue_ids = df['issueid'].unique()
        production_reports = self.parent_class.objects.filter(issueid__in=issue_ids)
        report_mapping = {str(report.issueid): report for report in production_reports}
        
        # Create a new column with ProductionReport instances
        df['production_report'] = df['issueid'].map(report_mapping)
        
        # Drop the original issueid column and rename production_report to issueid
        df = df.drop('issueid', axis=1)
        df = df.rename(columns={'production_report': 'issueid'})
        return df
