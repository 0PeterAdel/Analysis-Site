"""
Helper utilities for the Safety & Compliance Dashboard
"""

import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import re

def generate_unique_key(base_key: str, suffix: str = "") -> str:
    """Generate a unique key for Streamlit widgets"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"{base_key}_{suffix}_{timestamp}" if suffix else f"{base_key}_{timestamp}"

def safe_convert_to_numeric(series: pd.Series) -> pd.Series:
    """Safely convert a pandas series to numeric, handling Arabic numerals"""
    # Replace Arabic numerals with English numerals
    arabic_to_english = {
        '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
        '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
    }
    
    def convert_arabic_numerals(text):
        if pd.isna(text):
            return text
        text = str(text)
        for arabic, english in arabic_to_english.items():
            text = text.replace(arabic, english)
        return text
    
    converted_series = series.apply(convert_arabic_numerals)
    return pd.to_numeric(converted_series, errors='coerce')

def clean_arabic_text(text: str) -> str:
    """Clean and normalize Arabic text"""
    if pd.isna(text) or not isinstance(text, str):
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Normalize Arabic characters
    text = text.replace('ي', 'ی').replace('ك', 'ک')
    
    return text

def format_percentage(value: float, decimals: int = 1) -> str:
    """Format a number as percentage"""
    if pd.isna(value):
        return "0.0%"
    return f"{value:.{decimals}f}%"

def format_number(value: float, thousands_sep: str = ",") -> str:
    """Format a number with thousands separator"""
    if pd.isna(value):
        return "0"
    return f"{int(value):,}".replace(",", thousands_sep)

def get_status_color(status: str) -> str:
    """Get color based on status"""
    status = str(status).lower()
    
    if any(word in status for word in ['مغلق', 'مكتمل', 'closed', 'completed']):
        return '#00cc88'  # Green
    elif any(word in status for word in ['مفتوح', 'قيد', 'open', 'pending']):
        return '#ffa500'  # Orange
    elif any(word in status for word in ['عاجل', 'urgent', 'high']):
        return '#ff4b4b'  # Red
    else:
        return '#1f77b4'  # Blue

def get_risk_color(risk_level: str) -> str:
    """Get color based on risk level"""
    risk_level = str(risk_level).lower()
    
    if any(word in risk_level for word in ['عالي', 'مرتفع', 'high']):
        return '#ff4b4b'  # Red
    elif any(word in risk_level for word in ['متوسط', 'medium']):
        return '#ffa500'  # Orange
    elif any(word in risk_level for word in ['منخفض', 'low']):
        return '#00cc88'  # Green
    else:
        return '#1f77b4'  # Blue

def create_metric_card(title: str, value: str, delta: Optional[str] = None, 
                      color: str = '#1f77b4') -> str:
    """Create a styled metric card HTML"""
    delta_html = f"<p style='color: #666; margin: 0.25rem 0 0 0; font-size: 0.8rem;'>{delta}</p>" if delta else ""
    
    return f"""
    <div style='background: linear-gradient(135deg, {color}15 0%, {color}25 100%); 
                padding: 1.5rem; border-radius: 12px; border-left: 4px solid {color};
                box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 1rem;'>
        <h3 style='color: {color}; margin: 0; font-size: 2rem; font-weight: bold;'>{value}</h3>
        <p style='color: #666; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>{title}</p>
        {delta_html}
    </div>
    """

def filter_dataframe_by_date(df: pd.DataFrame, date_column: str, 
                           start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """Filter dataframe by date range"""
    if date_column not in df.columns:
        return df
    
    try:
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        mask = (df[date_column] >= pd.Timestamp(start_date)) & \
               (df[date_column] <= pd.Timestamp(end_date))
        return df[mask]
    except Exception:
        return df

def filter_dataframe_by_text(df: pd.DataFrame, column: str, 
                           search_terms: List[str], case_sensitive: bool = False) -> pd.DataFrame:
    """Filter dataframe by text search"""
    if column not in df.columns or not search_terms:
        return df
    
    mask = pd.Series([False] * len(df))
    
    for term in search_terms:
        if case_sensitive:
            mask |= df[column].str.contains(term, na=False)
        else:
            mask |= df[column].str.contains(term, case=False, na=False)
    
    return df[mask]

def calculate_compliance_rate(df: pd.DataFrame, status_column: str) -> float:
    """Calculate compliance rate based on status"""
    if status_column not in df.columns or df.empty:
        return 0.0
    
    total_records = len(df)
    completed_records = len(df[df[status_column].str.contains('مغلق|مكتمل|closed|completed', 
                                                            case=False, na=False)])
    
    return (completed_records / total_records * 100) if total_records > 0 else 0.0

def get_data_quality_score(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate data quality score for a dataframe"""
    if df.empty:
        return {
            'score': 0,
            'missing_percentage': 100,
            'duplicate_percentage': 0,
            'completeness': 0
        }
    
    total_cells = df.size
    missing_cells = df.isnull().sum().sum()
    duplicate_rows = df.duplicated().sum()
    
    missing_percentage = (missing_cells / total_cells * 100) if total_cells > 0 else 0
    duplicate_percentage = (duplicate_rows / len(df) * 100) if len(df) > 0 else 0
    completeness = 100 - missing_percentage
    
    # Calculate overall quality score
    score = max(0, completeness - duplicate_percentage)
    
    return {
        'score': round(score, 1),
        'missing_percentage': round(missing_percentage, 1),
        'duplicate_percentage': round(duplicate_percentage, 1),
        'completeness': round(completeness, 1),
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_cells': missing_cells,
        'duplicate_rows': duplicate_rows
    }

def create_download_link(df: pd.DataFrame, filename: str, 
                        file_format: str = 'csv') -> str:
    """Create a download link for dataframe"""
    if file_format.lower() == 'csv':
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        return st.download_button(
            label=f"تحميل {filename}.csv",
            data=csv,
            file_name=f"{filename}.csv",
            mime="text/csv"
        )
    elif file_format.lower() == 'excel':
        # This would require additional implementation for Excel export
        pass

def validate_data_types(df: pd.DataFrame) -> Dict[str, List[str]]:
    """Validate data types and return suggestions"""
    suggestions = {
        'numeric_candidates': [],
        'date_candidates': [],
        'categorical_candidates': []
    }
    
    for column in df.columns:
        # Check for numeric candidates
        if df[column].dtype == 'object':
            # Try to convert to numeric
            numeric_series = safe_convert_to_numeric(df[column])
            if not numeric_series.isnull().all():
                suggestions['numeric_candidates'].append(column)
        
        # Check for date candidates
        if df[column].dtype == 'object':
            sample_values = df[column].dropna().head(10)
            date_patterns = [
                r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
                r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY
                r'\d{1,2}-\d{1,2}-\d{4}'  # D-M-YYYY
            ]
            
            for value in sample_values:
                if any(re.match(pattern, str(value)) for pattern in date_patterns):
                    suggestions['date_candidates'].append(column)
                    break
        
        # Check for categorical candidates
        if df[column].dtype == 'object':
            unique_ratio = df[column].nunique() / len(df)
            if unique_ratio < 0.1:  # Less than 10% unique values
                suggestions['categorical_candidates'].append(column)
    
    return suggestions

def create_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Create summary statistics for dataframe"""
    if df.empty:
        return pd.DataFrame()
    
    summary_data = []
    
    for column in df.columns:
        col_info = {
            'العمود': column,
            'النوع': str(df[column].dtype),
            'عدد القيم': len(df[column]),
            'القيم المفقودة': df[column].isnull().sum(),
            'نسبة المفقود': f"{df[column].isnull().sum() / len(df) * 100:.1f}%",
            'القيم الفريدة': df[column].nunique()
        }
        
        if df[column].dtype in ['int64', 'float64']:
            col_info.update({
                'المتوسط': f"{df[column].mean():.2f}" if not df[column].isnull().all() else "N/A",
                'الوسيط': f"{df[column].median():.2f}" if not df[column].isnull().all() else "N/A",
                'الحد الأدنى': f"{df[column].min():.2f}" if not df[column].isnull().all() else "N/A",
                'الحد الأقصى': f"{df[column].max():.2f}" if not df[column].isnull().all() else "N/A"
            })
        
        summary_data.append(col_info)
    
    return pd.DataFrame(summary_data)