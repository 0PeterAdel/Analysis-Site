"""
Utility functions for the Safety & Compliance Analytics Platform
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import streamlit as st
from config import DATA_CONFIG, KPI_THRESHOLDS, COLORS

def clean_text(text):
    """Clean and standardize text values"""
    if pd.isna(text):
        return None
    return str(text).strip()

def standardize_status(status_value):
    """Standardize status values across all datasets"""
    if pd.isna(status_value):
        return None
    
    status_str = str(status_value).strip().lower()
    
    for standard_status, variations in DATA_CONFIG['status_mappings'].items():
        if any(variation in status_str for variation in variations):
            return standard_status.replace('_', ' ').title()
    
    return status_value

def standardize_classification(classification_value):
    """Standardize classification/priority values"""
    if pd.isna(classification_value):
        return None
    
    class_str = str(classification_value).strip().lower()
    
    for standard_class, variations in DATA_CONFIG['classification_mappings'].items():
        if any(variation in class_str for variation in variations):
            return standard_class.title()
    
    return classification_value

def parse_date(date_value):
    """Parse date values using multiple formats"""
    if pd.isna(date_value):
        return None
    
    if isinstance(date_value, datetime):
        return date_value
    
    date_str = str(date_value).strip()
    
    for date_format in DATA_CONFIG['date_formats']:
        try:
            return datetime.strptime(date_str, date_format)
        except ValueError:
            continue
    
    # Try pandas to_datetime as fallback
    try:
        return pd.to_datetime(date_value)
    except:
        return None

def calculate_closure_rate(status_series):
    """Calculate closure rate from status series"""
    if len(status_series) == 0:
        return 0
    
    closed_count = (status_series == 'Closed').sum()
    total_count = len(status_series.dropna())
    
    return (closed_count / total_count * 100) if total_count > 0 else 0

def get_kpi_color(value, kpi_type, reverse=False):
    """Get color based on KPI value and thresholds"""
    if kpi_type not in KPI_THRESHOLDS:
        return COLORS['primary']
    
    thresholds = KPI_THRESHOLDS[kpi_type]
    
    if not reverse:
        if value >= thresholds['excellent']:
            return COLORS['success']
        elif value >= thresholds['good']:
            return COLORS['warning']
        else:
            return COLORS['danger']
    else:
        if value <= thresholds['low']:
            return COLORS['success']
        elif value <= thresholds['medium']:
            return COLORS['warning']
        else:
            return COLORS['danger']

def create_metric_card(title, value, delta=None, help_text=None):
    """Create a styled metric card"""
    delta_html = f"<small style='color: #666;'>{delta}</small>" if delta else ""
    help_html = f"<small style='color: #888;'>{help_text}</small>" if help_text else ""
    
    return f"""
    <div class="metric-card">
        <h3>{title}</h3>
        <h2>{value}</h2>
        {delta_html}
        {help_html}
    </div>
    """

def create_insight_box(message, box_type="info"):
    """Create a styled insight box"""
    icons = {
        "success": "✅",
        "warning": "⚠️",
        "error": "🚨",
        "info": "ℹ️"
    }
    
    icon = icons.get(box_type, "ℹ️")
    css_class = f"{box_type}-box"
    
    return f'<div class="{css_class}">{icon} {message}</div>'

def filter_dataframe(df, filters):
    """Apply multiple filters to a dataframe"""
    filtered_df = df.copy()
    
    for column, values in filters.items():
        if column in filtered_df.columns and values:
            if isinstance(values, list):
                filtered_df = filtered_df[filtered_df[column].isin(values)]
            else:
                filtered_df = filtered_df[filtered_df[column] == values]
    
    return filtered_df

def calculate_trend(series, periods=5):
    """Calculate trend direction and magnitude"""
    if len(series) < periods * 2:
        return 0, "insufficient_data"
    
    recent = series.tail(periods).mean()
    older = series.head(periods).mean()
    
    if older == 0:
        return 0, "no_baseline"
    
    trend_pct = ((recent - older) / older) * 100
    
    if abs(trend_pct) < 5:
        direction = "stable"
    elif trend_pct > 0:
        direction = "increasing"
    else:
        direction = "decreasing"
    
    return trend_pct, direction

def generate_summary_stats(df, numeric_columns=None):
    """Generate comprehensive summary statistics"""
    if numeric_columns is None:
        numeric_columns = df.select_dtypes(include=[np.number]).columns
    
    summary = {}
    
    for col in numeric_columns:
        if col in df.columns:
            series = df[col].dropna()
            if len(series) > 0:
                summary[col] = {
                    'count': len(series),
                    'mean': series.mean(),
                    'median': series.median(),
                    'std': series.std(),
                    'min': series.min(),
                    'max': series.max(),
                    'q25': series.quantile(0.25),
                    'q75': series.quantile(0.75)
                }
    
    return summary

def detect_outliers(series, method='iqr'):
    """Detect outliers in a numeric series"""
    if method == 'iqr':
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = series[(series < lower_bound) | (series > upper_bound)]
        
    elif method == 'zscore':
        z_scores = np.abs((series - series.mean()) / series.std())
        outliers = series[z_scores > 3]
    
    else:
        outliers = pd.Series(dtype=float)
    
    return outliers

def create_comparison_chart(data, x_col, y_col, color_col=None, chart_type='bar'):
    """Create a comparison chart with consistent styling"""
    if chart_type == 'bar':
        fig = px.bar(
            data, 
            x=x_col, 
            y=y_col, 
            color=color_col,
            color_continuous_scale='Blues'
        )
    elif chart_type == 'line':
        fig = px.line(
            data, 
            x=x_col, 
            y=y_col, 
            color=color_col,
            markers=True
        )
    elif chart_type == 'scatter':
        fig = px.scatter(
            data, 
            x=x_col, 
            y=y_col, 
            color=color_col,
            size=y_col
        )
    else:
        fig = px.bar(data, x=x_col, y=y_col, color=color_col)
    
    fig.update_layout(
        height=400,
        template='plotly_white',
        showlegend=True if color_col else False
    )
    
    return fig

def export_data(df, filename, file_format='csv'):
    """Export dataframe to various formats"""
    if file_format == 'csv':
        return df.to_csv(index=False)
    elif file_format == 'excel':
        return df.to_excel(index=False)
    elif file_format == 'json':
        return df.to_json(orient='records', indent=2)
    else:
        return df.to_csv(index=False)

def validate_data_quality(df):
    """Validate data quality and return quality metrics"""
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isnull().sum().sum()
    
    quality_metrics = {
        'completeness': (total_cells - missing_cells) / total_cells * 100,
        'missing_values': missing_cells,
        'total_cells': total_cells,
        'duplicate_rows': df.duplicated().sum(),
        'columns_with_missing': (df.isnull().sum() > 0).sum(),
        'data_types': df.dtypes.value_counts().to_dict()
    }
    
    return quality_metrics

@st.cache_data
def load_csv_with_encoding(filepath):
    """Load CSV file with proper encoding detection"""
    encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            df = pd.read_csv(filepath, encoding=encoding)
            return df
        except UnicodeDecodeError:
            continue
    
    # If all encodings fail, try with error handling
    try:
        df = pd.read_csv(filepath, encoding='utf-8', errors='ignore')
        return df
    except Exception as e:
        st.error(f"Failed to load {filepath}: {str(e)}")
        return pd.DataFrame()

def format_number(number, format_type='auto'):
    """Format numbers for display"""
    if pd.isna(number):
        return "N/A"
    
    if format_type == 'percentage':
        return f"{number:.1f}%"
    elif format_type == 'currency':
        return f"${number:,.2f}"
    elif format_type == 'integer':
        return f"{int(number):,}"
    elif format_type == 'decimal':
        return f"{number:.2f}"
    else:
        # Auto format based on value
        if abs(number) >= 1000000:
            return f"{number/1000000:.1f}M"
        elif abs(number) >= 1000:
            return f"{number/1000:.1f}K"
        elif number == int(number):
            return f"{int(number)}"
        else:
            return f"{number:.2f}"