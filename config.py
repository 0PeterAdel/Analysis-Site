"""
Configuration file for the Safety & Compliance Analytics Platform
"""

import streamlit as st

# Application Configuration
APP_CONFIG = {
    'title': 'Safety & Compliance Analytics Platform',
    'icon': '🛡️',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Color Schemes
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'warning': '#ff7f0e',
    'danger': '#d62728',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

# Chart Configuration
CHART_CONFIG = {
    'height': 400,
    'template': 'plotly_white',
    'color_sequences': {
        'qualitative': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'],
        'sequential': 'Blues',
        'diverging': 'RdBu'
    }
}

# Data Processing Configuration
DATA_CONFIG = {
    'date_formats': ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S'],
    'status_mappings': {
        'open': ['open', 'مفتوح', 'pending', 'active'],
        'closed': ['close', 'مغلق', 'closed', 'completed'],
        'in_progress': ['progress', 'ongoing', 'جاري']
    },
    'classification_mappings': {
        'high': ['high', 'عالي', 'critical', 'urgent'],
        'medium': ['medium', 'متوسط', 'moderate'],
        'low': ['low', 'منخفض', 'minor']
    }
}

# KPI Thresholds
KPI_THRESHOLDS = {
    'closure_rate': {
        'excellent': 80,
        'good': 60,
        'poor': 40
    },
    'risk_score': {
        'high': 0.7,
        'medium': 0.4,
        'low': 0.2
    },
    'compliance_score': {
        'excellent': 90,
        'good': 70,
        'poor': 50
    }
}

# File Mappings
FILE_MAPPINGS = {
    'identifiers': 'معرفات.csv',
    'site_audits': 'والمواقع.csv',
    'risk_assessment': 'تقييم_المخاطر.csv',
    'contractor_audits': 'العلى_المقاولين.csv',
    'incidents': 'الحوادث.csv',
    'hypotheses': 'الفرضيات.csv',
    'fire_safety': 'أنظمة_السلامة_والإطفاء.csv',
    'inspection_notes': 'التفتيش.csv',
    'scis_audit': 'متطلبات_SCIS.csv',
    'power_bi_sheet': 'Power_BI_Copy_v.02_Sheet1.csv'
}

# Custom CSS
CUSTOM_CSS = """
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 1rem 0;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .kpi-container {
        display: flex;
        justify-content: space-around;
        margin: 2rem 0;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    .stSelectbox > div > div {
        background-color: #f8f9fa;
    }
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .insight-box {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .warning-box {
        background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .success-box {
        background: linear-gradient(135deg, #55efc4 0%, #00b894 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .error-box {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
"""