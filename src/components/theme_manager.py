"""
Theme Manager for Safety & Compliance Dashboard
Handles dark/light theme switching and UI customization
"""

import streamlit as st
import json
from datetime import datetime

class ThemeManager:
    """Advanced theme management system"""
    
    def __init__(self):
        """Initialize theme manager with light and dark themes"""
        self.themes = {
            'light': {
                'name': 'Light Theme',
                'icon': '☀️',
                'primary_color': "#1489dd",
                'secondary_color': '#ff7f0e',
                'success_color': '#2ca02c',
                'warning_color': '#d62728',
                'info_color': '#9467bd',
                'background_color': '#ffffff',
                'surface_color': '#f8f9fa',
                'text_color': '#000000',
                'text_secondary': '#1a1a1a',
                'text_on_primary': '#ffffff',
                'text_on_secondary': '#000000',
                'text_on_success': '#000000',
                'text_on_warning': '#000000',
                'text_on_info': '#000000',
                'text_on_light': '#000000',
                'text_on_dark': '#ffffff',
                'chart_text': '#000000',
                'metric_text': '#000000',
                'border_color': '#dee2e6',
                'shadow': '0 4px 6px rgba(0,0,0,0.1)',
                'gradient_primary': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                'gradient_secondary': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                'gradient_success': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                'card_bg': 'linear-gradient(135deg, #f0f2f6 0%, #e8ecf0 100%)',
                'sidebar_bg': '#000000'
            },
            'dark': {
                'name': 'Dark Theme',
                'icon': '🌙',
                'primary_color': "#137dd3",
                'secondary_color': '#ffa726',
                'success_color': '#66bb6a',
                'warning_color': '#ef5350',
                'info_color': '#ab47bc',
                'background_color': '#121212',
                'surface_color': '#1e1e1e',
                'text_color': '#ffffff',
                'text_secondary': '#b0b0b0',
                'text_on_primary': '#ffffff',
                'text_on_secondary': '#000000',
                'text_on_success': '#000000',
                'text_on_warning': '#000000',
                'text_on_info': '#ffffff',
                'text_on_light': '#212529',
                'text_on_dark': '#ffffff',
                'chart_text': '#ffffff',
                'metric_text': '#ffffff',
                'border_color': '#333333',
                'shadow': '0 4px 6px rgba(0,0,0,0.3)',
                'gradient_primary': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                'gradient_secondary': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                'gradient_success': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                'card_bg': 'linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%)',
                'sidebar_bg': '#000000'
            }
        }
        
        # Initialize theme in session state
        if 'current_theme' not in st.session_state:
            st.session_state.current_theme = 'light'
    
    def get_current_theme(self):
        """Get current theme configuration"""
        return self.themes[st.session_state.current_theme]
    
    def set_theme(self, theme_name):
        """Set current theme"""
        if theme_name in self.themes:
            st.session_state.current_theme = theme_name
            st.rerun()
    
    def create_theme_selector(self):
        """Create theme selector widget"""
        st.sidebar.markdown("### 🎨 اختيار المظهر")
        
        current_theme = st.session_state.current_theme
        theme_options = {name: f"{config['icon']} {config['name']}"
                        for name, config in self.themes.items()}
        
        # Add custom styles to ensure text visibility
        st.markdown("""
            <style>
                div[data-testid="stSelectbox"] label {
                    color: #ffffff !important;
                }
                div[data-testid="stSelectbox"] div[data-baseweb="select"] {
                    color: #ffffff !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        selected_theme = st.sidebar.selectbox(
            "اختر المظهر",
            options=list(theme_options.keys()),
            format_func=lambda x: theme_options[x],
            index=list(theme_options.keys()).index(current_theme),
            key="theme_selector"
        )
        
        if selected_theme != current_theme:
            self.set_theme(selected_theme)
        
        # Theme preview
        theme_config = self.get_current_theme()
        st.sidebar.markdown(f"""
        <div style="
            background: {theme_config['card_bg']};
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid {theme_config['border_color']};
            margin: 1rem 0;
        ">
            <h4 style="color: {theme_config['primary_color']}; margin: 0;">
                {theme_config['icon']} {theme_config['name']}
            </h4>
            <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">
                <div style="width: 20px; height: 20px; background: {theme_config['primary_color']}; border-radius: 50%;"></div>
                <div style="width: 20px; height: 20px; background: {theme_config['secondary_color']}; border-radius: 50%;"></div>
                <div style="width: 20px; height: 20px; background: {theme_config['success_color']}; border-radius: 50%;"></div>
                <div style="width: 20px; height: 20px; background: {theme_config['warning_color']}; border-radius: 50%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def apply_theme_css(self):
        """Apply current theme CSS"""
        theme = self.get_current_theme()
        
        css = f"""
        <style>
            /* Global Theme Variables */
            :root {{
                --primary-color: {theme['primary_color']};
                --secondary-color: {theme['secondary_color']};
                --success-color: {theme['success_color']};
                --warning-color: {theme['warning_color']};
                --info-color: {theme['info_color']};
                --background-color: {theme['background_color']};
                --surface-color: {theme['surface_color']};
                --text-color: {theme['text_color']};
                --text-secondary: {theme['text_secondary']};
                --text-on-primary: {theme['text_on_primary']};
                --text-on-secondary: {theme['text_on_secondary']};
                --text-on-success: {theme['text_on_success']};
                --text-on-warning: {theme['text_on_warning']};
                --text-on-info: {theme['text_on_info']};
                --text-on-light: {theme['text_on_light']};
                --text-on-dark: {theme['text_on_dark']};
                --chart-text: {theme['chart_text']};
                --metric-text: {theme['metric_text']};
                --border-color: {theme['border_color']};
                --shadow: {theme['shadow']};
                --gradient-primary: {theme['gradient_primary']};
                --gradient-secondary: {theme['gradient_secondary']};
                --gradient-success: {theme['gradient_success']};
                --card-bg: {theme['card_bg']};
                --sidebar-bg: {theme['sidebar_bg']};
            }}

            /* Ensure dark text in light theme for all streamlit elements */
            .light-theme .stMarkdown,
            .light-theme .stText,
            .light-theme .stMetric,
            .light-theme .stDataFrame,
            .light-theme .stTable,
            .light-theme .stTabs,
            .light-theme .stTab,
            .light-theme .stSelectbox,
            .light-theme .stMultiSelect,
            .light-theme .stRadio,
            .light-theme .stCheckbox,
            .light-theme .stTextInput,
            .light-theme .stTextArea,
            .light-theme .stDateInput,
            .light-theme .stTimeInput,
            .light-theme .stNumberInput,
            .light-theme .stFileUploader,
            .light-theme .stProgress,
            .light-theme .stAlert,
            .light-theme .stError,
            .light-theme .stWarning,
            .light-theme .stInfo,
            .light-theme .stSuccess {{
                color: {theme['text_color']} !important;
            }}

            /* Light theme specific enhancements for text visibility */
            .stApp.light {{
                --text-color-normal: {theme['text_color']};
                --text-color-muted: {theme['text_secondary']};
            }}

            /* Enhanced visibility for alerts and messages */
            .element-container .stAlert {{
                color: {theme['text_color']} !important;
                font-weight: 500 !important;
            }}

            /* Make text in charts and visualizations more visible */
            .st-emotion-cache-1inwz65 .plot-container text {{
                fill: {theme['chart_text']} !important;
                font-weight: 600 !important;
                color: {theme['chart_text']} !important;
            }}

            /* Ensure visibility of error messages */
            .stException,
            .stError {{
                color: {theme['warning_color']} !important;
                font-weight: 500 !important;
            }}

            /* Enhance visibility of info messages */
            .stInfo {{
                color: {theme['info_color']} !important;
                font-weight: 500 !important;
            }}

            /* DataFrames and tables text visibility */
            .dataframe td,
            .dataframe th {{
                color: {theme['text_color']} !important;
            }}

            /* Better visibility for tabs and navigation */
            .stTabs [role="tab"][aria-selected="true"] {{
                color: {theme['primary_color']} !important;
                font-weight: 600 !important;
            }}

            /* Section headers and titles */
            h1, h2, h3, h4, h5, h6 {{
                color: {theme['text_color']} !important;
                font-weight: 600 !important;
            }}

            /* Enhanced text contrast for buttons */
            .stButton button {{
                color: {theme['text_color']} !important;
                font-weight: 500 !important;
            }}
            
            /* Main App Background */
            .stApp {{
                background-color: var(--background-color);
                color: var(--text-color);
            }}
            
            /* Sidebar Styling */
            .css-1d391kg,
            .css-1544g2n,
            .css-1avcm0n,
            .css-14xtw13,
            .css-1nm2qww,
            .css-zt5igj,
            .css-1vq4p4l,
            .css-1oe5cao,
            [data-testid="stSidebar"],
            [data-testid="stSidebarNav"] {{
                background-color: #000000 !important;
            }}

            /* Force white text in sidebar for all modes */
            [data-testid="stSidebar"],
            [data-testid="stSidebar"] *,
            [data-testid="stSidebar"] .element-container,
            [data-testid="stSidebar"] .streamlit-expanderHeader,
            [data-testid="stSidebar"] .streamlit-expanderContent,
            [data-testid="stSidebar"] .stMarkdown,
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] .stSelectbox,
            [data-testid="stSidebar"] .stMultiSelect,
            [data-testid="stSidebar"] p,
            [data-testid="stSidebar"] span,
            [data-testid="stSidebar"] div,
            [data-testid="stSidebar"] h1,
            [data-testid="stSidebar"] h2,
            [data-testid="stSidebar"] h3,
            [data-testid="stSidebar"] h4,
            [data-testid="stSidebar"] h5,
            [data-testid="stSidebar"] h6,
            [data-testid="stSidebar"] button,
            [data-testid="stSidebar"] input,
            [data-testid="stSidebar"] select,
            [data-testid="stSidebar"] .stTextInput > div > div > input {{
                color: #ffffff !important;
            }}

            /* Additional sidebar text color overrides */
            .sidebar .stMarkdown,
            .sidebar .stText,
            .sidebar label,
            .sidebar-content,
            [data-testid="stSidebarNav"],
            [data-testid="baseButton-headerNoPadding"] {{
                color: #ffffff !important;
            }}
            
            /* Main Header */
            .main-header {{
                font-size: 3rem;
                font-weight: bold;
                text-align: center;
                margin-bottom: 2rem;
                background: var(--gradient-primary);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
                animation: headerGlow 3s ease-in-out infinite alternate;
            }}

            /* Enhanced metric text visibility */
            .stMetric {{
                color: var(--text-color) !important;
            }}
            
            .stMetric [data-testid="stMetricValue"] {{
                color: var(--text-color) !important;
                font-weight: 600 !important;
            }}
            
            .stMetric [data-testid="stMetricDelta"] {{
                color: var(--text-color) !important;
                font-weight: 500 !important;
            }}
            
            /* Plot title and text enhancements */
            .js-plotly-plot .plotly .gtitle,
            .js-plotly-plot .plotly .xtitle,
            .js-plotly-plot .plotly .ytitle,
            .js-plotly-plot .plotly .legendtext {{
                fill: var(--text-color) !important;
                color: var(--text-color) !important;
                font-weight: 600 !important;
            }}
            
            .plot-container .main-svg text {{
                fill: var(--text-color) !important;
                color: var(--text-color) !important;
            }}
            
            @keyframes headerGlow {{
                from {{ filter: brightness(1); }}
                to {{ filter: brightness(1.2); }}
            }}
            
            /* Enhanced Metric Cards */
            .metric-card {{
                background: var(--card-bg);
                padding: 2rem;
                border-radius: 1rem;
                border: 1px solid var(--border-color);
                box-shadow: var(--shadow);
                margin-bottom: 1.5rem;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }}
            
            /* Ensure text visibility in sector cards */
            .sector-card,
            .activity-card {{
                color: var(--text-color) !important;
                text-shadow: 0 0 1px rgba(0,0,0,0.1) !important;
            }}
            
            /* Enhance text visibility in visualization sections */
            .visualization-section h3,
            .visualization-section h4,
            .visualization-section p {{
                color: var(--text-color) !important;
                text-shadow: 0 0 1px rgba(0,0,0,0.1) !important;
            }}
            
            /* Ensure visibility of info and warning messages */
            div[data-testid="stText"],
            div[data-testid="stMarkdownContainer"] {{
                color: var(--text-color) !important;
                font-weight: 500 !important;
            }}
            
            /* Enhanced metric text */
            .metric-value,
            .metric-label {{
                color: var(--metric-text) !important;
                text-shadow: 0 0 1px rgba(0,0,0,0.1) !important;
                font-weight: 600 !important;
            }}
            
            .metric-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: var(--gradient-primary);
            }}
            
            .metric-card:hover {{
                transform: translateY(-5px) scale(1.02);
                box-shadow: 0 8px 25px rgba(0,0,0,0.2);
            }}
            
            .metric-card h2 {{
                color: var(--metric-text);
                font-size: 2.5rem;
                font-weight: 800;
                margin: 0.5rem 0;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
            }}
            
            .metric-card h3 {{
                color: var(--metric-text);
                font-size: 1.2rem;
                font-weight: 600;
                margin: 0;
                opacity: 1;
                text-shadow: 0px 0px 1px rgba(0,0,0,0.1);
            }}
            
            .metric-card p {{
                color: var(--metric-text);
                font-size: 0.9rem;
                font-weight: 500;
                margin: 0.5rem 0 0 0;
                opacity: 0.95;
            }}
            
            /* Chart Text Styling */
            .st-emotion-cache-1inwz65 text,
            .st-emotion-cache-1inwz65 .tick text,
            .st-emotion-cache-1inwz65 .axis-label,
            .st-emotion-cache-1inwz65 .legendtext,
            .st-emotion-cache-1inwz65 .annotation-text {{
                fill: var(--chart-text) !important;
                font-weight: 600 !important;
                color: var(--chart-text) !important;
                text-shadow: 0 0 1px rgba(0,0,0,0.1) !important;
            }}
            
            .st-emotion-cache-1inwz65 .tick text {{
                font-size: 11px !important;
            }}
            
            .st-emotion-cache-1inwz65 .axis-label {{
                font-weight: 700 !important;
                font-size: 13px !important;
            }}
            
            /* Chart title and legend */
            .st-emotion-cache-1inwz65 .gtitle,
            .st-emotion-cache-1inwz65 .legend text {{
                fill: var(--chart-text) !important;
                font-weight: 700 !important;
                font-size: 14px !important;
            }}
            
            /* Chart tooltips and hover text */
            .st-emotion-cache-1inwz65 .tooltip text,
            .st-emotion-cache-1inwz65 .hover text {{
                fill: var(--chart-text) !important;
                font-weight: 600 !important;
                font-size: 12px !important;
                text-shadow: 0 0 2px rgba(255,255,255,0.8) !important;
            }}
            
            /* Ensure contrast for trend indicators */
            .trend-indicator {{
                color: var(--metric-text);
                font-weight: bold;
                text-shadow: 0px 0px 2px rgba(0,0,0,0.1);
            }}
            
            /* Ensure contrast for compliance rates */
            .compliance-rate {{
                color: var(--metric-text);
                font-weight: bold;
                text-shadow: 0px 0px 2px rgba(0,0,0,0.2);
            }}
            
            /* High contrast text overlays */
            .metric-overlay {{
                color: var(--metric-text);
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 4px;
                background: rgba(0, 0, 0, 0.1);
            }}
            
            .dark .metric-overlay {{
                background: rgba(255, 255, 255, 0.1);
            }}
            
            /* Chart container background */
            .st-emotion-cache-1inwz65 {{
                background: var(--surface-color);
                padding: 1rem;
                border-radius: 8px;
                border: 1px solid var(--border-color);
            }}

            /* Enhanced plot text visibility */
            .plot-container text,
            .plot-container .xtick text,
            .plot-container .ytick text,
            .plot-container .legend text,
            .plot-container .annotation-text {{
                fill: var(--text-color) !important;
                color: var(--text-color) !important;
                font-weight: 600 !important;
            }}

            /* Risk metrics and percentages */
            .risk-metric,
            .percentage-value,
            .metric-value {{
                color: var(--text-color) !important;
                font-weight: 600 !important;
            }}

            /* Distribution plot text */
            .distribution-plot text,
            .distribution-plot .legend text {{
                fill: var(--text-color) !important;
                color: var(--text-color) !important;
                font-weight: 600 !important;
            }}

            /* General visualization text */
            [data-testid="stText"],
            [data-testid="stMarkdown"] {{
                color: var(--text-color) !important;
            }}
            
            /* Animated Elements */
            @keyframes fadeInUp {{
                from {{
                    opacity: 0;
                    transform: translateY(30px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            .fade-in-up {{
                animation: fadeInUp 0.6s ease-out;
            }}
            
            @keyframes pulse {{
                0% {{ transform: scale(1); }}
                50% {{ transform: scale(1.05); }}
                100% {{ transform: scale(1); }}
            }}
            
            .pulse {{
                animation: pulse 2s infinite;
            }}
            
            /* Responsive Design */
            @media (max-width: 768px) {{
                .main-header {{
                    font-size: 2rem;
                }}
                
                .metric-card {{
                    padding: 1rem;
                }}
            }}
            
            /* Custom Scrollbar */
            ::-webkit-scrollbar {{
                width: 8px;
            }}
            
            ::-webkit-scrollbar-track {{
                background: var(--surface-color);
            }}
            
            ::-webkit-scrollbar-thumb {{
                background: var(--primary-color);
                border-radius: 4px;
            }}
            
            ::-webkit-scrollbar-thumb:hover {{
                background: var(--secondary-color);
            }}

            /* Enhance table text visibility */
            .dataframe thead th,
            .dataframe tbody td {{
                color: var(--text-color) !important;
                font-weight: 500 !important;
            }}

            /* Ensure text visibility in expandable sections */
            .streamlit-expanderHeader,
            .streamlit-expanderContent {{
                color: var(--text-color) !important;
                font-weight: 500 !important;
            }}

            /* Status messages and alerts */
            .status-message,
            .alert-box {{
                color: var(--text-color) !important;
                font-weight: 500 !important;
                text-shadow: 0 0 1px rgba(0,0,0,0.1) !important;
            }}

            /* Sector and category labels */
            .sector-label,
            .category-label {{
                color: var(--text-color) !important;
                font-weight: 600 !important;
            }}

            /* Info boxes and tooltips */
            .info-box,
            .tooltip-content {{
                color: var(--text-color) !important;
                background-color: var(--surface-color) !important;
                border: 1px solid var(--border-color) !important;
                font-weight: 500 !important;
            }}
        </style>
        """
        
        st.markdown(css, unsafe_allow_html=True)
    
    def create_theme_info(self):
        """Create theme information display"""
        theme = self.get_current_theme()
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🎨 معلومات المظهر")
        st.sidebar.markdown(f"""
        **المظهر الحالي:** {theme['icon']} {theme['name']}
        
        **الألوان:**
        - 🔵 الأساسي: `{theme['primary_color']}`
        - 🟠 الثانوي: `{theme['secondary_color']}`
        - 🟢 النجاح: `{theme['success_color']}`
        - 🔴 التحذير: `{theme['warning_color']}`
        """)
    
    def save_theme_preferences(self, user_id=None):
        """Save theme preferences to local storage"""
        preferences = {
            'theme': st.session_state.current_theme,
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id or 'default'
        }
        
        # In a real application, you would save this to a database
        # For now, we'll use session state
        st.session_state.theme_preferences = preferences
    
    def load_theme_preferences(self, user_id=None):
        """Load theme preferences from local storage"""
        if 'theme_preferences' in st.session_state:
            preferences = st.session_state.theme_preferences
            if preferences.get('user_id') == (user_id or 'default'):
                self.set_theme(preferences.get('theme', 'light'))
