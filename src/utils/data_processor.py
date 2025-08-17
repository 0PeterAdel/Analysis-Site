"""
Advanced Data Engineering Module
Handles data cleaning, standardization, and unification for the Safety & Compliance Dashboard
"""

import pandas as pd
import numpy as np
import re
import os
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

# Add parent directories to path for imports
# This ensures that imports like 'config.settings' work correctly
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..')) # Adjust if needed for top-level imports

try:
    from config.settings import ENCODING_OPTIONS, DATA_CONFIG
except ImportError:
    # Fallback if config is not available (for local testing without full project structure)
    ENCODING_OPTIONS = ['utf-8', 'utf-8-sig', 'cp1256', 'iso-8859-1']
    DATA_CONFIG = {
        "excel_files": [
            {
                "filename": "sample-of-data.xlsx",
                "sheets": [
                    {"name": "تدقيق متطلبات SCIS", "unified_type": "inspections", "column_mapping": {"الرقم ": "الرقم", "تاريخ الملاحظة": "التاريخ", "تصنيف النشاط": "النشاط", "الحالة ": "الحالة", "الإدارة المسئولة عن تنفيذ التوصية": "الإدارة"}},
                    {"name": "ملاحظات التفتيش", "unified_type": "inspections", "column_mapping": {"الرقم ": "الرقم", "تاريخ الملاحظة": "التاريخ", "تصنيف النشاط": "النشاط", "الحالة ": "الحالة", "الإدارة المسئولة عن تنفيذ التوصية": "الإدارة", "التصنيف ": "التصنيف"}},
                    {"name": "فحص أنظمة السلامة والإطفاء", "unified_type": "safety_checks", "column_mapping": {"تاريخ الفحص": "التاريخ", "حالة التوصية": "الحالة", "الإدارة المسئولة عن تنفيذ التوصية": "الإدارة", "تصنيف النشاط": "النشاط"}},
                    {"name": "توصيات الفرضيات", "unified_type": "recommendations", "column_mapping": {"تاريخ الفرضية": "التاريخ", "حالة التوصية": "الحالة", "الإدارة المسئولة عن تنفيذ التوصية": "الإدارة", "تصنيف النشاط": "النشاط", "الإجراءات التصحيحية والتوصيات": "التوصية_المقترحة"}},
                    {"name": "توصيات الحوادث", "unified_type": "incidents", "column_mapping": {"تاريخ الحادث": "التاريخ", "حالة التوصية": "الحالة", "الإدارة المسئولة عن تنفيذ التوصية": "الإدارة", "تصنيف النشاط": "النشاط", "وصف مختصر عن الحادث": "الوصف", "تصنيف الحادث": "نوع_الحادث"}},
                    {"name": "توصيات التدقيق على المقاولين", "unified_type": "contractor_audits", "column_mapping": {"تاريخ التدقيق": "التاريخ", "حالة التوصية": "الحالة", "الإدارة المسئولة عن متابعة تنفيذ التوصية": "الإدارة", "تصنيف النشاط": "النشاط", "الفجوات المرصودة": "الوصف"}},
                    {"name": "توصيات تقييم المخاطر", "unified_type": "risk_assessments", "column_mapping": {"تاريخ التقييم": "التاريخ", "حالة التوصية": "الحالة", "الإدارة المسئولة عن تنفيذ التوصية": "الإدارة", "تصنيف النشاط": "النشاط", "نسب المخاطرة": "نسبة_المخاطرة", "الإجراءات التصحيحية والتوصيات": "التوصية_المقترحة"}},
                    {"name": "تقارير تدقيق وفحص المواقع", "unified_type": "inspections", "column_mapping": {"تاريخ الملاحظة": "التاريخ", "الحالة ": "الحالة", "الإدارة المسئولة عن تنفيذ التوصية": "الإدارة", "تصنيف النشاط": "النشاط", "التصنيف ": "التصنيف"}}
                ]
            },
            {
                "filename": "power-bi-copy-v.02.xlsx",
                "sheets": [
                    {"name": "ورقة1", "unified_type": "power_bi_metadata", "column_mapping": {}}
                ]
            }
        ],
        "csv_files": [
            # Removed "المصنف1.xlsx - معرفات.csv" as it is no longer needed
            {"filename": "معرفات.csv", "unified_type": "identifiers_metadata", "column_mapping": {"التصنيف ": "التصنيف", "الحالة": "الحالة", "الإدارات المعنية بالاغلاق": "الإدارة", "مؤشرات التدقيق على المقاولين": "مؤشر_التدقيق", "تصنيف الحادث": "تصنيف_الحادث", "تبعية الحادث": "تبعية_الحادث"}},
            # Add other CSV files from your directory tree if they are meant to be loaded
            {"filename": "Power_BI_Copy_v.02_Sheet1.csv", "unified_type": "power_bi_metadata", "column_mapping": {}},
            {"filename": "أنظمة_السلامة_والإطفاء.csv", "unified_type": "safety_checks", "column_mapping": {"رقم الإجراء / التوصية ": "الرقم", "تاريخ الفحص": "التاريخ", "حالة التوصية": "الحالة", "الإدارة المسئولة عن تنفيذ التوصية": "الإدارة", "تصنيف النشاط": "النشاط"}},
            {"filename": "التفتيش.csv", "unified_type": "inspections", "column_mapping": {"الرقم ": "الرقم", "تاريخ الملاحظة": "التاريخ", "تصنيف النشاط": "النشاط", "الحالة ": "الحالة", "الإدارة المسئولة عن تنفيذ التوصية": "الإدارة", "التصنيف ": "التصنيف"}},
            {"filename": "الحوادث.csv", "unified_type": "incidents", "column_mapping": {"رقم الإجراء / التوصية ": "الرقم", "تاريخ الحادث": "التاريخ", "حالة التوصية": "الحالة", "الإدارة المسئولة عن تنفيذ التوصية": "الإدارة", "تصنيف النشاط": "النشاط", "وصف مختصر عن الحادث": "الوصف", "تصنيف الحادث": "نوع_الحادث"}},
            {"filename": "العلى_المقاولين.csv", "unified_type": "contractor_audits", "column_mapping": {"رقم\nالإجراء / التوصية ": "الرقم", "تاريخ التدقيق": "التاريخ", "حالة التوصية": "الحالة", "الإدارة المسئولة عن متابعة تنفيذ التوصية": "الإدارة", "تصنيف النشاط": "النشاط", "الفجوات المرصودة": "الوصف"}},
            {"filename": "الفرضيات.csv", "unified_type": "recommendations", "column_mapping": {"رقم الإجراء / التوصية ": "الرقم", "تاريخ الفرضية": "التاريخ", "حالة التوصية": "الحالة", "الإدارة المسئولة عن تنفيذ التوصية": "الإدارة", "تصنيف النشاط": "النشاط", "الإجراءات التصحيحية والتوصيات": "التوصية_المقترحة"}},
            {"filename": "تقييم_المخاطر.csv", "unified_type": "risk_assessments", "column_mapping": {"رقم\nالإجراء / التوصية ": "الرقم", "تاريخ التقييم": "التاريخ", "حالة التوصية": "الحالة", "الإدارة المسئولة عن تنفيذ التوصية": "الإدارة", "تصنيف النشاط": "النشاط", "نسب المخاطرة": "نسبة_المخاطرة", "الإجراءات التصحيحية والتوصيات": "التوصية_المقترحة"}},
            {"filename": "متطلبات_SCIS.csv", "unified_type": "inspections", "column_mapping": {"الرقم ": "الرقم", "تاريخ الملاحظة": "التاريخ", "تصنيف النشاط": "النشاط", "الحالة ": "الحالة", "الإدارة المسئولة عن تنفيذ التوصية": "الإدارة"}},
            {"filename": "والمواقع.csv", "unified_type": "inspections", "column_mapping": {"الرقم ": "الرقم", "تاريخ الملاحظة": "التاريخ", "تصنيف النشاط": "النشاط", "الحالة ": "الحالة", "الإدارة المسئولة عن تنفيذ التوصية": "الإدارة", "التصنيف ": "التصنيف"}}
        ]
    }


class SafetyDataProcessor:
    """Comprehensive data processor for safety and compliance data"""
    
    def __init__(self):
        self.data_sources = {}
        self.unified_data = {}
        self.metadata = {}
        
        # Set up database path
        self.base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        self.database_dir = os.path.join(self.base_dir, 'database')
        
    def get_database_path(self, filename):
        """Get full path for database file"""
        return os.path.join(self.database_dir, filename)
    
    def load_all_data(self):
        """
        Load all data from database directory based on DATA_CONFIG.
        Applies cleaning and initial column renaming during loading.
        """
        all_raw_data = {}
        
        # Load Excel files from DATA_CONFIG
        for excel_entry in DATA_CONFIG.get("excel_files", []):
            filename = excel_entry["filename"]
            file_path = self.get_database_path(filename)
            if os.path.exists(file_path):
                excel_data = self.load_excel_data(file_path, excel_entry["sheets"])
                all_raw_data[filename] = excel_data
            else:
                print(f"File not found: {file_path}")
        
        # Load CSV files from DATA_CONFIG
        for csv_entry in DATA_CONFIG.get("csv_files", []):
            filename = csv_entry["filename"]
            file_path = self.get_database_path(filename)
            if os.path.exists(file_path):
                csv_data = self.load_csv_data(file_path, csv_entry["column_mapping"], csv_entry["unified_type"])
                if csv_data is not None and not csv_data.empty:
                    # For CSVs, store as filename -> DataFrame directly
                    all_raw_data[filename] = csv_data
            else:
                print(f"File not found: {file_path}")
                
        self.data_sources = all_raw_data
        return all_raw_data
        
    def load_excel_data(self, file_path, sheets_config):
        """Load and process Excel data with multiple sheets based on config"""
        try:
            excel_file = pd.ExcelFile(file_path)
            data = {}
            
            for sheet_info in sheets_config:
                sheet_name = sheet_info["name"]
                column_mapping = sheet_info.get("column_mapping", {})
                unified_type = sheet_info.get("unified_type", "misc")

                if sheet_name in excel_file.sheet_names:
                    try:
                        df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
                        df = self._clean_dataframe(df, sheet_name, column_mapping)
                        if not df.empty:
                            df['original_source_file'] = os.path.basename(file_path)
                            df['original_sheet_name'] = sheet_name
                            df['unified_type'] = unified_type # Tag with unified type
                            data[sheet_name] = df
                    except Exception as sheet_error:
                        print(f"Error loading sheet '{sheet_name}' from '{file_path}': {str(sheet_error)}")
                        continue
                else:
                    print(f"Sheet '{sheet_name}' not found in Excel file '{file_path}'. Skipping.")
                
            return data
        except Exception as e:
            print(f"Error loading Excel file '{file_path}': {str(e)}")
            return {}
    
    def load_csv_data(self, file_path, column_mapping=None, unified_type="misc"):
        """Load and process CSV data with robust encoding detection and column renaming"""
        if column_mapping is None:
            column_mapping = {}

        df = None
        for encoding in ENCODING_OPTIONS:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"Error reading CSV with encoding {encoding}: {e}")
                continue
        
        if df is None:
            print(f"Failed to load CSV file '{file_path}' with all tried encodings.")
            return pd.DataFrame() # Return empty DataFrame if all attempts fail

        filename = os.path.basename(file_path).replace('.csv', '')
        df = self._clean_dataframe(df, filename, column_mapping)
        if not df.empty:
            df['original_source_file'] = os.path.basename(file_path)
            df['unified_type'] = unified_type # Tag with unified type
        return df
    
    def _clean_dataframe(self, df, source_name, column_mapping=None):
        """Clean and standardize dataframe with specific column renaming"""
        if df.empty:
            return df
            
        # Remove completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Clean column names initially
        df.columns = self._clean_column_names(df.columns)
        
        # Handle duplicate columns after initial cleaning
        df = self._handle_duplicate_columns(df)
        
        # Handle header rows (first row often contains actual column names)
        # Re-evaluate based on cleaned columns
        if len(df) > 0 and self._is_potential_header_row(df.iloc[0]):
             # If the first row seems like a header, promote it
            new_columns = [str(col).strip() if pd.notna(col) else f"col_{i}" 
                           for i, col in enumerate(df.iloc[0])]
            df = df.iloc[1:].copy()
            df.columns = self._clean_column_names(new_columns) # Re-clean new column names
            df = self._handle_duplicate_columns(df) # Handle duplicates again
        
        # Apply specific column renaming from config
        if column_mapping:
            df = self._rename_columns(df, column_mapping)
            
        # Standardize data types
        df = self._standardize_data_types(df)
        
        # Clean text data
        df = self._clean_text_data(df)
        
        # Standardize status values
        df = self._standardize_status_values(df)
        
        return df
    
    def _handle_duplicate_columns(self, df):
        """Handle duplicate column names by appending a suffix"""
        cols = df.columns.tolist()
        seen = {}
        new_cols = []
        for col in cols:
            original_col = col # Keep original for initial check
            if original_col in seen:
                seen[original_col] += 1
                new_cols.append(f"{original_col}_{seen[original_col]}")
            else:
                seen[original_col] = 0
                new_cols.append(original_col)
        df.columns = new_cols
        return df

    def _clean_column_names(self, columns):
        """Clean and standardize column names (remove newlines, extra spaces, special chars, standardize case)"""
        cleaned_columns = []
        for idx, col in enumerate(columns):
            if pd.isna(col) or str(col).startswith('Unnamed'):
                cleaned_columns.append(f"col_{idx}")
            else:
                clean_col = str(col)
                if isinstance(col, tuple): # Handle MultiIndex columns if any
                    clean_col = '_'.join([str(x) for x in col if pd.notna(x)])
                
                clean_col = clean_col.strip()
                clean_col = re.sub(r'\n+', '_', clean_col) # Replace newlines with underscore
                clean_col = re.sub(r'\s+', '_', clean_col) # Replace spaces with underscore
                clean_col = re.sub(r'[^\w_]', '', clean_col) # Remove non-alphanumeric characters except underscore
                clean_col = re.sub(r'_+', '_', clean_col).strip('_') # Remove repeated/trailing underscores
                
                # Check for empty string after cleaning (e.g. if column was just symbols)
                if not clean_col:
                    clean_col = f"col_{idx}"

                cleaned_columns.append(clean_col)
        return cleaned_columns

    def _rename_columns(self, df, column_mapping):
        """Apply specific column renaming based on a provided mapping."""
        # Create a reverse mapping for case-insensitive and cleaned matches
        reverse_mapping = {self._clean_name_for_matching(k): v for k, v in column_mapping.items()}
        
        new_cols = []
        for col in df.columns:
            cleaned_col = self._clean_name_for_matching(col)
            if cleaned_col in reverse_mapping:
                new_cols.append(reverse_mapping[cleaned_col])
            else:
                new_cols.append(col) # Keep original if no match
        df.columns = new_cols
        return df

    def _clean_name_for_matching(self, name):
        """Helper to clean names for matching against column_mapping keys."""
        if pd.isna(name):
            return ""
        clean_name = str(name).strip().lower()
        clean_name = re.sub(r'\n+', '_', clean_name)
        clean_name = re.sub(r'\s+', '_', clean_name)
        clean_name = re.sub(r'_+', '_', clean_name).strip('_')
        return clean_name

    def _is_potential_header_row(self, row):
        """Check if the first row is likely a header. Improved logic."""
        # A header row often has more non-null string values that look like labels
        # and fewer purely numeric/boolean values compared to data rows.
        
        # Count non-nulls that are strings and not simple numbers
        string_like_count = sum(1 for x in row if pd.notna(x) and isinstance(x, str) and not x.strip().replace('.', '', 1).isdigit())
        
        # Heuristic: if more than 50% of non-null values are string-like, it's a header
        if row.notna().sum() > 0 and string_like_count / row.notna().sum() > 0.5:
            return True
        
        # Also, if many columns are 'Unnamed' after initial load, and the first row has good names
        if any(col.startswith('Unnamed') for col in row.index) and string_like_count > len(row) * 0.3:
            return True
            
        return False
    
    def _standardize_data_types(self, df):
        """Standardize data types across the dataframe"""
        for col in df.columns:
            # Try to convert date columns
            if any(keyword in col.lower() for keyword in ['تاريخ', 'date']):
                df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Try to convert numeric columns
            # Use 'col.lower()' to be case-insensitive, and avoid issues with original column names
            elif any(keyword in col.lower() for keyword in ['عدد', 'نسبة', 'رقم', 'number', 'count', 'percentage']):
                # Ensure values are suitable for numeric conversion
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def _clean_text_data(self, df):
        """Clean and standardize text data"""
        try:
            if df.empty:
                return df
                
            # Iterate through columns of object type (potential strings)
            for col in df.select_dtypes(include=['object']).columns:
                # Ensure the column exists after potential renaming
                if col in df.columns: 
                    # Convert to string and clean common issues
                    series = df[col].astype(str).str.strip()
                    series = series.replace('nan', np.nan) # Replace string 'nan' with actual NaN
                    series = series.replace('', np.nan)    # Replace empty strings with NaN
                    df[col] = series
            
            return df
        except Exception as e:
            print(f"Error cleaning text data: {str(e)}")
            return df
    
    def _standardize_status_values(self, df):
        """Standardize status values across all datasets for consistency"""
        status_mappings = {
            'مفتوح - Open': 'مفتوح',
            'مغلق - Close': 'مغلق',
            'مغلق - Closed': 'مغلق',
            'Closed - Close': 'مغلق',
            'Open': 'مفتوح',
            'Close': 'مغلق',
            'Closed': 'مغلق',
            'مكتمل': 'مغلق', # Consider "مكتمل" as "مغلق"
            'complete': 'مغلق',
            'completed': 'مغلق',
            'قيد المراجعة': 'مفتوح', # Consider "قيد المراجعة" as "مفتوح" for simplicity
            'in review': 'مفتوح',
            'pending': 'مفتوح'
        }
        
        # Apply status standardization to relevant columns
        for col in df.columns:
            # Check for column names that indicate status, case-insensitive
            if any(keyword in col.lower() for keyword in ['حالة', 'status', 'state']):
                # Apply mapping to non-null values only
                df[col] = df[col].apply(lambda x: status_mappings.get(x, x) if pd.notna(x) else x)
        
        return df
    
    def create_unified_dataset(self, data_sources):
        """
        Unifies and categorizes all loaded DataFrames into a single dictionary
        based on their 'unified_type'.
        """
        unified_data_categorized = {}
        
        for file_name, file_content in data_sources.items():
            if isinstance(file_content, dict): # This is an Excel file with sheets
                for sheet_name, df in file_content.items():
                    if not df.empty and 'unified_type' in df.columns:
                        data_type = df['unified_type'].iloc[0] # Get unified_type from the DataFrame itself
                        if data_type not in unified_data_categorized:
                            unified_data_categorized[data_type] = []
                        unified_data_categorized[data_type].append(df.drop(columns=['unified_type', 'original_source_file', 'original_sheet_name'], errors='ignore'))
            elif isinstance(file_content, pd.DataFrame): # This is a CSV file
                if not file_content.empty and 'unified_type' in file_content.columns:
                    data_type = file_content['unified_type'].iloc[0]
                    if data_type not in unified_data_categorized:
                        unified_data_categorized[data_type] = []
                    unified_data_categorized[data_type].append(file_content.drop(columns=['unified_type', 'original_source_file'], errors='ignore'))
        
        # Now, merge similar datasets within each category
        final_unified_data = {}
        for data_type, list_of_dfs in unified_data_categorized.items():
            if list_of_dfs:
                # Use _merge_similar_datasets to concatenate all DataFrames of the same type
                final_unified_data[data_type] = self._merge_similar_datasets(list_of_dfs)
                # Ensure the 'التاريخ' column is datetime after merging
                if 'التاريخ' in final_unified_data[data_type].columns:
                    final_unified_data[data_type]['التاريخ'] = pd.to_datetime(final_unified_data[data_type]['التاريخ'], errors='coerce')

        self.unified_data = final_unified_data
        return final_unified_data
    
    def _merge_similar_datasets(self, datasets):
        """
        Merges a list of DataFrames by concatenating them, handling missing columns
        by filling with NaN and ensuring common data types where possible.
        """
        if not datasets:
            return pd.DataFrame()
        
        # Collect all unique columns across all datasets
        all_columns = set()
        for df in datasets:
            all_columns.update(df.columns)
            
        # Reindex all dataframes to have the same columns and then concatenate
        standardized_datasets = []
        for df in datasets:
            df_reindexed = df.reindex(columns=list(all_columns))
            standardized_datasets.append(df_reindexed)
            
        result = pd.concat(standardized_datasets, ignore_index=True, sort=False)
        return result
    
    def generate_kpi_data(self, unified_data):
        """Generate KPI data for dashboard from unified data"""
        kpis = {}
        
        for data_type, df in unified_data.items():
            if df.empty:
                continue
                
            kpis[data_type] = {
                'total_records': len(df),
                'date_range': self._get_date_range(df),
                'status_distribution': self._get_status_distribution(df),
                'department_distribution': self._get_department_distribution(df),
                'activity_distribution': self._get_activity_distribution(df)
            }
        
        return kpis
    
    def _get_date_range(self, df):
        """Get date range from dataframe using standardized 'التاريخ' column"""
        if 'التاريخ' in df.columns and pd.api.types.is_datetime64_any_dtype(df['التاريخ']):
            valid_dates = df['التاريخ'].dropna()
            if not valid_dates.empty:
                return {
                    'min_date': valid_dates.min(),
                    'max_date': valid_dates.max()
                }
        return None
    
    def _get_status_distribution(self, df):
        """Get status distribution from dataframe using standardized 'الحالة' column"""
        if 'الحالة' in df.columns:
            return df['الحالة'].value_counts().to_dict()
        return {}
    
    def _get_department_distribution(self, df):
        """Get department distribution from dataframe using standardized 'الإدارة' or similar column"""
        # Prioritize 'الإدارة' then 'القطاع'
        if 'الإدارة' in df.columns:
            return df['الإدارة'].value_counts().to_dict()
        elif 'القطاع' in df.columns:
            return df['القطاع'].value_counts().to_dict()
        return {}
    
    def _get_activity_distribution(self, df):
        """Get activity distribution from dataframe using standardized 'النشاط' or similar column"""
        if 'النشاط' in df.columns:
            return df['النشاط'].value_counts().to_dict()
        return {}
    
    def export_cleaned_data(self, unified_data, output_path="cleaned_unified_data.xlsx"):
        """Export cleaned and unified data to an Excel file with multiple sheets."""
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for sheet_name, df in unified_data.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"Cleaned data exported to {output_path}")
        except Exception as e:
            print(f"Error exporting data: {str(e)}")
    
    def get_data_quality_report(self, unified_data):
        """Generate data quality report for each unified dataset"""
        report = {}
        
        for data_type, df in unified_data.items():
            if df.empty:
                continue
                
            total_cells = len(df) * len(df.columns)
            missing_values_count = df.isnull().sum().sum()
            
            report[data_type] = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'missing_values_count': missing_values_count,
                'missing_data_percentage': (missing_values_count / total_cells * 100) if total_cells > 0 else 0,
                'duplicate_rows': df.duplicated().sum(),
                'data_types': {col: str(df[col].dtype) for col in df.columns},
                'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024) # in MB
            }
        
        return report
    
    def generate_kpis(self, unified_data):
        """Generate KPIs - alias for generate_kpi_data"""
        return self.generate_kpi_data(unified_data)
    
    def generate_quality_report(self, unified_data):
        """Generate quality report - alias for get_data_quality_report"""
        return self.get_data_quality_report(unified_data)

# Example usage (for testing this module independently)
def main():
    processor = SafetyDataProcessor()
    
    # Load all raw data
    raw_data_sources = processor.load_all_data()
    print("\n--- Raw Data Loaded ---")
    for file_name, content in raw_data_sources.items():
        if isinstance(content, dict):
            print(f"File: {file_name}, Sheets: {list(content.keys())}")
        else:
            print(f"File: {file_name}, Rows: {len(content)}, Cols: {len(content.columns)}")
            
    # Create unified dataset
    unified_data = processor.create_unified_dataset(raw_data_sources)
    
    print("\n--- Unified Datasets ---")
    for data_type, df in unified_data.items():
        print(f"Unified Type: '{data_type}', Rows: {len(df)}, Cols: {len(df.columns)}, Columns: {list(df.columns)}")
    
    # Generate KPIs
    kpis = processor.generate_kpi_data(unified_data)
    print("\n--- KPIs ---")
    for data_type, kpi_info in kpis.items():
        print(f"KPIs for '{data_type}':")
        for key, value in kpi_info.items():
            print(f"  {key}: {value}")
            
    # Generate quality report
    quality_report = processor.get_data_quality_report(unified_data)
    print("\n--- Quality Report ---")
    for data_type, report_info in quality_report.items():
        print(f"Quality Report for '{data_type}': {report_info}")
    
    # Example export (optional)
    # processor.export_cleaned_data(unified_data, "exported_unified_data.xlsx")

if __name__ == "__main__":
    main()

