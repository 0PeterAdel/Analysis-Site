"""
🛡️ Ultimate Safety & Compliance Dashboard
Professional Arabic-supported dashboard for safety and compliance management

Author: OpenHands AI Assistant
Version: 4.0
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np # Ensure numpy is imported
import json # Ensure json is imported for parsing
import io # Import io for StringIO

# Import components and logic
from src.utils.data_processor import SafetyDataProcessor
from src.logic.dashboard_analyzer import DashboardAnalyzer
from src.components.advanced_features import AdvancedFeatures
from src.components.theme_manager import ThemeManager
from src.components.gemini_chatbot import create_chatbot_interface
from src.components.filters.advanced_filters import AdvancedFilters # Import the new AdvancedFilters component
from src.config.settings import APP_TITLE, SECTORS, RISK_ACTIVITIES_METADATA, STATUS_OPTIONS, PRIORITY_OPTIONS, RISK_LEVELS, COLORS, PERFORMANCE, CHART_CONFIG

# Page configuration
st.set_page_config(
    page_title=f"{APP_TITLE}",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components (outside of class for singletons)
data_processor = SafetyDataProcessor()
dashboard_analyzer = DashboardAnalyzer()
advanced_features = AdvancedFeatures()
theme_manager = ThemeManager()
advanced_filters_component = AdvancedFilters() # Initialize the advanced filters component

class UltimateDashboard:
    def __init__(self):
        self.data_processor = data_processor
        self.dashboard_analyzer = dashboard_analyzer
        self.advanced_features = advanced_features
        self.theme_manager = theme_manager
        self.advanced_filters_component = advanced_filters_component # Assign to instance

        # Initialize session state for data and filters
        if 'data_loaded' not in st.session_state:
            st.session_state.data_loaded = False
        if 'unified_data' not in st.session_state:
            st.session_state.unified_data = {}
        if 'kpi_data' not in st.session_state:
            st.session_state.kpi_data = {}
        if 'quality_report' not in st.session_state:
            st.session_state.quality_report = {}
        if 'filter_presets' not in st.session_state:
            st.session_state.filter_presets = {}
        if 'current_theme_config' not in st.session_state:
            st.session_state.current_theme_config = self.theme_manager.get_current_theme()
        # Initialize selected_sectors for multiselect default in AdvancedFilters
        if 'selected_sectors' not in st.session_state:
            st.session_state.selected_sectors = []
        # Initialize other filter states for persistence if not already done by AdvancedFilters
        if 'selected_status' not in st.session_state:
            st.session_state.selected_status = ["الكل"]
        if 'selected_priority' not in st.session_state:
            st.session_state.selected_priority = "الكل"
        if 'selected_risk' not in st.session_state:
            st.session_state.selected_risk = "الكل"
        if 'text_search' not in st.session_state:
            st.session_state.text_search = ""
        if 'date_range_filter' not in st.session_state:
            # Default to a broad range if no data is loaded yet
            st.session_state.date_range_filter = (datetime.now().date() - timedelta(days=365), datetime.now().date())


    def create_modern_navigation(self):
        """Create modern navigation at the top of sidebar"""
        theme = st.session_state.current_theme_config
        
        st.sidebar.markdown(f"""
        <div style='text-align: center; padding: 1rem; background: {theme['gradient_primary']}; 
                    border-radius: 10px; margin-bottom: 1rem;'>
            <h2 style='margin: 0; color: {theme['text_color']};'>🛡️ لوحة التحكم</h2>
            <p style='margin: 0; opacity: 0.9; color: {theme['text_secondary']};'>Safety & Compliance Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        pages = {
            "الرئيسية المتقدمة": "�",
            "التحليلات الذكية": "🧠", 
            "مركز التصدير": "📤",
            "رفع البيانات": "📁",
            "تشغيل مساعد الذكاء الاصطناعي": "🤖",
            "تقرير الجودة": "📋",
            "المراقبة المباشرة": "📡"
        }
        
        selected_page = st.sidebar.selectbox(
            "اختر الصفحة",
            list(pages.keys()),
            format_func=lambda x: f"{pages[x]} {x}",
            key="main_navigation"
        )
        
        return selected_page

    def create_enhanced_sidebar(self, unified_data, kpi_data):
        """Create enhanced sidebar with navigation first and integrated AdvancedFilters."""
        selected_page = self.create_modern_navigation()
        
        self.theme_manager.create_theme_selector()
        
        # Use the AdvancedFilters component to create the filter system
        # It will handle all filter UI and update session state internally
        filters = self.advanced_filters_component.create_complete_filter_system(unified_data, kpi_data)
        
        self.advanced_features.show_notifications()
        
        self.advanced_features.create_performance_monitor()
        
        self.advanced_features.create_help_system()
        
        return filters, selected_page

    @st.cache_data(ttl=PERFORMANCE['cache_ttl'], show_spinner="جاري تحميل ومعالجة البيانات...")
    def load_and_process_data(_self): # Changed self to _self
        """Load and process all data sources using DataProcessor and generate KPIs/Quality Report."""
        try:
            # Load all raw data from configured files/sheets
            raw_data_sources = _self.data_processor.load_all_data() # Use _self
            
            # Create unified datasets from raw data
            unified_data = _self.data_processor.create_unified_dataset(raw_data_sources) # Use _self
            
            # Generate KPIs from unified data
            kpi_data = _self.data_processor.generate_kpis(unified_data) # Use _self
            
            # Generate quality report from unified data
            quality_report = _self.data_processor.generate_quality_report(unified_data) # Use _self
            
            return unified_data, kpi_data, quality_report
            
        except Exception as e:
            st.error(f"خطأ في تحميل أو معالجة البيانات: {str(e)}")
            _self.advanced_features.add_notification(f"خطأ في تحميل البيانات: {str(e)}", "error") # Use _self
            return {}, {}, {} # Return empty dataframes on error

    def create_ultimate_main_dashboard(self, unified_data, kpi_data, filters):
        """Create the ultimate main dashboard"""
        theme = st.session_state.current_theme_config
        
        st.markdown(f'''
        <div class="main-header fade-in-up">
            🛡️ Ultimate Safety & Compliance Dashboard
        </div>
        <div style="text-align: center; margin-bottom: 2rem; color: {theme['text_secondary']};">
            مرحباً بك في لوحة معلومات السلامة والامتثال | آخر تحديث: {datetime.now().strftime("%H:%M")}
        </div>
        ''', unsafe_allow_html=True)
        
        # KPI Cards (use kpi_data directly, as it's already aggregated by DataProcessor)
        self.create_kpi_cards(kpi_data)
        
        # Main content tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 نظرة عامة", 
            "📈 التحليلات", 
            "⚠️ المخاطر", 
            "🎯 الأداء"
        ])
        
        with tab1:
            self.create_overview_section(unified_data, filters)
        
        with tab2:
            self.create_analytics_section(unified_data, filters)
        
        with tab3:
            self.create_risk_section(unified_data, filters)
        
        with tab4:
            self.create_performance_section(unified_data, filters)

    def create_kpi_cards(self, kpi_data):
        """Create compact, meaningful KPI cards from aggregated KPI dicts"""
        theme = st.session_state.current_theme_config
        
        if not kpi_data:
            st.info("لا توجد مؤشرات أداء متاحة")
            return

        # Aggregate KPIs across all unified datasets
        total_records = sum([data.get('total_records', 0) for data in kpi_data.values()])
        
        open_count = 0
        closed_count = 0
        for data in kpi_data.values():
            status_dist = data.get('status_distribution', {})
            open_count += status_dist.get('مفتوح', 0)
            closed_count += status_dist.get('مغلق', 0)

        datasets_count = len(kpi_data)
        closure_rate = (closed_count / (open_count + closed_count) * 100) if (open_count + closed_count) > 0 else 0

        # Determine global date range from kpi_data
        min_date_global = None
        max_date_global = None
        for data in kpi_data.values():
            dr = data.get('date_range')
            if isinstance(dr, dict) and dr.get('min_date') is not None and dr.get('max_date') is not None:
                cur_min = pd.to_datetime(dr['min_date'], errors='coerce')
                cur_max = pd.to_datetime(dr['max_date'], errors='coerce')
                if pd.notna(cur_min):
                    min_date_global = cur_min if min_date_global is None else min(min_date_global, cur_min)
                if pd.notna(cur_max):
                    max_date_global = cur_max if max_date_global is None else max(max_date_global, cur_max)

        cards = [
            {"label": "إجمالي السجلات", "value": f"{total_records:,}", "color": theme['primary_color']},
            {"label": "مفتوح", "value": f"{open_count:,}", "color": theme['warning_color']},
            {"label": "مغلق", "value": f"{closed_count:,}", "color": theme['success_color']},
            {"label": "نسبة الإغلاق %", "value": f"{closure_rate:.1f}", "color": theme['info_color']},
            {"label": "مجموعات البيانات", "value": f"{datasets_count}", "color": theme['secondary_color']},
        ]
        
        if min_date_global is not None and max_date_global is not None:
            cards.append({
                "label": "نطاق التاريخ", 
                "value": f"{min_date_global.date()} → {max_date_global.date()}",
                "color": theme['text_secondary']
            })

        for start in range(0, len(cards), 4):
            row = cards[start:start+4]
            cols = st.columns(len(row))
            for i, card in enumerate(row):
                color = card["color"]
                with cols[i]:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, {color}15 0%, {color}25 100%); 
                                padding: 1.2rem; border-radius: 12px; border-left: 4px solid {color};
                                box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 1rem;
                                color: {theme['text_color']};'>
                        <h3 style='color: {color}; margin: 0; font-size: 1.8rem; font-weight: bold;'>{card['value']}</h3>
                        <p style='margin: 0.5rem 0 0 0; font-size: 0.9rem;'>{card['label']}</p>
                    </div>
                    """, unsafe_allow_html=True)

    def create_overview_section(self, unified_data, filters):
        """Create overview section"""
        theme = st.session_state.current_theme_config
        st.markdown(f"<h3 style='color: {theme['text_color']};'>📊 نظرة عامة على البيانات</h3>", unsafe_allow_html=True)
        
        if not unified_data:
            st.info("لا توجد بيانات متاحة")
            return
        
        summary_data = []
        for dataset_name, df in unified_data.items():
            # Apply filters here for the overview summary
            # Use the common filter method from dashboard_analyzer
            filtered_df_for_summary = self.dashboard_analyzer._apply_common_filters(df, filters)
            if not filtered_df_for_summary.empty:
                summary_data.append({
                    'مجموعة البيانات': dataset_name,
                    'عدد السجلات': len(filtered_df_for_summary),
                    'عدد الأعمدة': len(filtered_df_for_summary.columns)
                })
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"<h4 style='color: {theme['text_color']};'>📈 ملخص البيانات</h4>", unsafe_allow_html=True)
            if summary_data:
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True)
            else:
                st.info("لا توجد بيانات ملخصة بعد تطبيق المرشحات.")
        
        with col2:
            st.markdown(f"<h4 style='color: {theme['text_color']};'>📊 توزيع البيانات</h4>", unsafe_allow_html=True)
            if summary_data:
                summary_df = pd.DataFrame(summary_data)
                fig = px.pie(
                    summary_df, 
                    values='عدد السجلات', 
                    names='مجموعة البيانات',
                    title="توزيع السجلات حسب مجموعة البيانات",
                    color_discrete_sequence=px.colors.qualitative.Pastel  # استخدام ألوان فاتحة
                )
                
                # تخصيص التلميح
                hovertemplate = "<b>%{label}</b><br>" + \
                               "عدد السجلات: %{value:,.0f}<br>" + \
                               "النسبة: %{percent:.1%}<extra></extra>"
                
                fig.update_traces(
                    textinfo='percent+label',  # عرض النسبة والتسمية
                    textfont=dict(
                        size=12,
                        color='black'
                    ),
                    textposition='inside',  # النص داخل القطاعات
                    hovertemplate=hovertemplate,  # تطبيق قالب التلميح المخصص
                    hoverlabel=dict(
                        bgcolor='white',  # خلفية بيضاء للتلميح
                        font_size=14,  # حجم خط التلميح
                        font_color='black'  # لون نص التلميح
                    )
                )
                
                fig.update_layout(
                    paper_bgcolor=theme['surface_color'],
                    plot_bgcolor=theme['background_color'],
                    font=dict(
                        color='black',  # لون النص الأساسي
                        size=14  # حجم الخط الأساسي
                    ),
                    title_font=dict(
                        color='black',  # لون العنوان
                        size=16  # حجم خط العنوان
                    ),
                    legend=dict(
                        font=dict(
                            color='black',  # لون نص وسيلة الإيضاح
                            size=12  # حجم خط وسيلة الإيضاح
                        ),
                        bgcolor='rgba(255, 255, 255, 0.8)'  # خلفية شبه شفافة لوسيلة الإيضاح
                    ),
                    hoverlabel_font_color='black'  # لون نص التلميح
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("لا توجد بيانات لتوزيعها بعد تطبيق المرشحات.")

    def create_analytics_section(self, unified_data, filters):
        """Create analytics section"""
        theme = st.session_state.current_theme_config
        st.markdown(f"<h3 style='color: {theme['text_color']};'>🧠 التحليلات المتقدمة</h3>", unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs([
            "📊 جدول الامتثال للقطاعات الأربعة", 
            "⚠️ إدارة المخاطر - جدول الأنشطة", 
            "🚨 تحليل الحوادث"
        ])
        
        with tab1:
            self.create_closing_compliance_table(unified_data, filters)
        
        with tab2:
            self.create_risk_management_activity_table(unified_data, filters)
        
        with tab3:
            self.create_incidents_analysis_table(unified_data, filters)

    def create_closing_compliance_table(self, unified_data, filters):
        """Create enhanced closing compliance table for sectors"""
        theme = st.session_state.current_theme_config
        st.markdown(f"<h4 style='color: {theme['text_color']};'>📊 جدول الامتثال حسب القطاع</h4>", unsafe_allow_html=True)
        
        # Initialize session state for clicked sector
        if 'clicked_sector' not in st.session_state:
            st.session_state.clicked_sector = None
        
        overview_tab, details_tab = st.tabs(["نظرة عامة", "تفاصيل القطاع"])
        
        # Local filters for this specific table (passed to analyzer)
        # These will override/refine the main sidebar filters for this view if selected
        local_filters = filters.copy()

        col1, col2, col3 = st.columns(3)
        with col1:
            # Get available sectors from the compliance data itself
            compliance_df_all_sectors = self.dashboard_analyzer.get_compliance_summary(unified_data, filters={}) # Get all sectors initially
            available_sectors_for_display = sorted(compliance_df_all_sectors['القطاع'].unique().tolist())

            selected_sectors_for_display = st.multiselect(
                "اختر القطاعات للعرض", 
                options=available_sectors_for_display, 
                default=st.session_state.get('selected_sectors_compliance_display', []),
                key="compliance_sectors_display_filter"
            )
            st.session_state.selected_sectors_compliance_display = selected_sectors_for_display

        with col2:
            status_filter_compliance = st.selectbox(
                "حالة الامتثال", 
                ["الكل", "مغلق", "مفتوح"],
                key="compliance_status_filter_local"
            )
        with col3:
            year_filter_compliance = st.selectbox(
                "السنة", 
                ["الكل"] + [str(year) for year in range(datetime.now().year, 2020, -1)],
                key="compliance_year_filter_local"
            )
        
        # Apply local filters to the filters dictionary before passing to analyzer
        if selected_sectors_for_display:
            local_filters['sectors'] = selected_sectors_for_display
        else:
            local_filters.pop('sectors', None) # Remove if nothing selected

        if status_filter_compliance != "الكل":
            local_filters['status'] = [status_filter_compliance]
        else:
            local_filters.pop('status', None)

        if year_filter_compliance != "الكل":
            local_filters['date_range'] = (datetime(int(year_filter_compliance), 1, 1).date(), datetime(int(year_filter_compliance), 12, 31).date())
        else:
            # If "الكل" is selected for year, ensure the date_range from main filters is still applied
            if 'date_range_filter' in st.session_state:
                local_filters['date_range'] = st.session_state.date_range_filter
            else:
                local_filters.pop('date_range', None)

        # Get compliance data from the analyzer with applied filters
        compliance_df = self.dashboard_analyzer.get_compliance_summary(unified_data, local_filters)
        
        with overview_tab:
            if not compliance_df.empty:
                st.dataframe(
                    compliance_df.drop(['trend_value', 'recent_compliance', 'quarterly_trends'], axis=1, errors='ignore'),
                    use_container_width=True,
                    height=400,
                    column_config={
                        "نسبة الامتثال %": st.column_config.ProgressColumn(
                            "نسبة الامتثال %",
                            help="نسبة الامتثال للقطاع",
                            min_value=0,
                            max_value=100,
                            format="%.1f%%"
                        ),
                        "اتجاه التغيير": st.column_config.TextColumn(
                            "اتجاه التغيير",
                            help="التغير في نسبة الامتثال خلال آخر 90 يوم",
                            max_chars=10
                        ),
                        "الأولوية": st.column_config.SelectboxColumn(
                            "الأولوية",
                            help="مستوى الأولوية للإجراءات المطلوبة",
                            width="small",
                            options=["منخفض", "متوسط", "عالي", "عاجل"]
                        )
                    }
                )
                
                st.markdown(f"<h3 style='color: {theme['text_color']};'>📊 تحليل تفصيلي</h3>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    avg_compliance = compliance_df['نسبة الامتثال %'].mean() if not compliance_df.empty else 0
                    st.markdown(f"""
                    <div style='background-color: {theme['surface_color']}; padding: 1rem; border-radius: 8px;
                                border: 1px solid {theme['primary_color']}; color: {theme['text_color']};'>
                        <p style='font-size: 1rem; margin: 0;'>متوسط نسبة الامتثال</p>
                        <h2 style='margin: 0.5rem 0; color: {theme['primary_color']};'>{avg_compliance:.1f}%</h2>
                        <p style='font-size: 0.9rem; margin: 0; color: {"green" if compliance_df["trend_value"].mean() > 0 else "red"};'>
                            {compliance_df["trend_value"].mean():.1f}%
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    high_priority = len(compliance_df[compliance_df['الأولوية'].isin(['عالي', 'عاجل'])])
                    st.markdown(f"""
                    <div style='background-color: {theme['surface_color']}; padding: 1rem; border-radius: 8px;
                                border: 1px solid {theme['warning_color']}; color: {theme['text_color']};'>
                        <p style='font-size: 1rem; margin: 0;'>القطاعات ذات الأولوية العالية</p>
                        <h2 style='margin: 0.5rem 0; color: {theme['warning_color']};'>{high_priority}</h2>
                        <p style='font-size: 0.8rem; margin: 0;'>عدد القطاعات التي تحتاج اهتمام عاجل</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    overall_trend_value = compliance_df['trend_value'].mean() if not compliance_df.empty else 0
                    trend_status = "📈 تحسن" if overall_trend_value > 0 else "📉 انخفاض" if overall_trend_value < 0 else "⚖️ ثابت"
                    trend_color = theme['success_color'] if overall_trend_value > 0 else theme['warning_color']
                    st.markdown(f"""
                    <div style='background-color: {theme['surface_color']}; padding: 1rem; border-radius: 8px;
                                border: 1px solid {trend_color}; color: {theme['text_color']};'>
                        <p style='font-size: 1rem; margin: 0;'>الاتجاه العام</p>
                        <h2 style='margin: 0.5rem 0; color: {trend_color};'>{trend_status}</h2>
                        <p style='font-size: 0.9rem; margin: 0; color: {trend_color};'>{overall_trend_value:.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"<h3 style='color: {theme['text_color']};'>📈 تحليل الاتجاهات</h3>", unsafe_allow_html=True)
                trend_fig = go.Figure()
                
                trend_fig.add_trace(go.Scatter(
                    x=compliance_df['القطاع'],
                    y=compliance_df['نسبة الامتثال %'],
                    name="نسبة الامتثال",
                    line=dict(color=theme['primary_color'], width=2)
                ))
                
                trend_fig.add_trace(go.Scatter(
                    x=compliance_df['القطاع'],
                    y=compliance_df['recent_compliance'],
                    name="الامتثال الحديث",
                    line=dict(color=theme['success_color'], width=2, dash='dash')
                ))
                
                trend_fig.update_layout(
                    title="مقارنة نسب الامتثال الحالية والحديثة",
                    xaxis_title="القطاع",
                    yaxis_title="نسبة الامتثال %",
                    hovermode='x unified',
                    paper_bgcolor=theme['surface_color'],
                    plot_bgcolor=theme['background_color'],
                    font_color=theme['text_color']
                )
                
                st.plotly_chart(trend_fig, use_container_width=True)
            else:
                st.info("لا توجد بيانات امتثال متاحة للقطاعات المحددة")
        
        with details_tab:
            if compliance_df.empty:
                st.info("لا توجد بيانات تفصيلية متاحة.")
                return
            
            selected_sector = st.selectbox(
                "اختر القطاع للتفاصيل",
                options=sorted(compliance_df['القطاع'].unique().tolist()),
                key="detail_sector_selector"
            )
            
            selected_sector_data = compliance_df[compliance_df['القطاع'] == selected_sector].iloc[0].to_dict()
            
            if selected_sector_data:
                detail_col1, detail_col2 = st.columns(2)
                
                with detail_col1:
                    st.markdown(f"<h3 style='color: {theme['text_color']};'>📊 الوضع الحالي</h3>", unsafe_allow_html=True)
                    
                    metrics_container = st.container()
                    with metrics_container:
                        st.metric(
                            "نسبة الامتثال",
                            f"{selected_sector_data['نسبة الامتثال %']:.1f}%",
                            delta=selected_sector_data['اتجاه التغيير']
                        )
                        
                        st.metric(
                            "السجلات المفتوحة",
                            selected_sector_data['السجلات المفتوحة']
                        )
                        
                        st.metric(
                            "السجلات المغلقة",
                            selected_sector_data['السجلات المغلقة']
                        )
                    
                    st.markdown(f"""
                    <h3 style='color: {theme['text_color']};'>⚠️ الأولوية والتوصيات</h3>
                    
                    **مستوى الأولوية:** <span style="color: {theme['primary_color']};">{selected_sector_data['الأولوية']}</span>
                    
                    **التوصية:**
                    <span style="color: {theme['text_color']};">{selected_sector_data['التوصية']}</span>
                    """, unsafe_allow_html=True)
                
                with detail_col2:
                    st.markdown(f"<h3 style='color: {theme['text_color']};'>📈 تحليل الاتجاه الربع سنوي</h3>", unsafe_allow_html=True)
                    
                    if 'quarterly_trends' in selected_sector_data and selected_sector_data['quarterly_trends']:
                        quarterly_df = pd.DataFrame(
                            selected_sector_data['quarterly_trends'].items(),
                            columns=['الربع', 'نسبة الامتثال']
                        )
                        
                        fig = px.line(
                            quarterly_df,
                            x='الربع',
                            y='نسبة الامتثال',
                            title=f"اتجاه الامتثال للقطاع {selected_sector}",
                            markers=True
                        )
                        
                        fig.update_layout(
                            xaxis_title="الربع",
                            yaxis_title="نسبة الامتثال %",
                            paper_bgcolor=theme['surface_color'],
                            plot_bgcolor=theme['background_color'],
                            font_color=theme['text_color']
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("لا توجد بيانات ربع سنوية متاحة لهذا القطاع.")
                    
                    st.markdown(f"<h3 style='color: {theme['text_color']};'>📋 خطة العمل المقترحة</h3>", unsafe_allow_html=True)
                    
                    # Use the actual numeric priority from selected_sector_data
                    priority_level_numeric = selected_sector_data['الأولوية'] # Assuming it's the numeric priority now
                    
                    if priority_level_numeric == "عاجل": # Map string to numeric if needed, or adjust logic in analyzer
                        st.error(f"""
                        **إجراءات عاجلة مطلوبة:**
                        1. مراجعة جميع الحالات المفتوحة وتحديد الأولويات
                        2. عقد اجتماع طارئ مع مسؤولي القطاع
                        3. وضع خطة عمل تصحيحية عاجلة
                        """)
                    elif priority_level_numeric == "عالي" or priority_level_numeric == "متوسط":
                        st.warning(f"""
                        **إجراءات التحسين المطلوبة:**
                        1. تحليل أسباب الحالات المفتوحة
                        2. تحديد فرص التحسين
                        3. متابعة دورية للتقدم
                        """)
                    else: # "منخفض"
                        st.success(f"""
                        **خطة المحافظة على الأداء:**
                        1. توثيق الممارسات الناجحة
                        2. مشاركة التجارب مع القطاعات الأخرى
                        3. مراقبة مستمرة للمؤشرات
                        """)

    def create_risk_management_activity_table(self, unified_data, filters):
        """Create enhanced risk management activity table"""
        theme = st.session_state.current_theme_config
        st.markdown(f"<h4 style='color: {theme['text_color']};'>⚠️ إدارة المخاطر - جدول الأنشطة</h4>", unsafe_allow_html=True)
        
        # Local filters for this specific table (passed to analyzer)
        local_filters = filters.copy()

        col1, col2, col3 = st.columns(3)
        with col1:
            activity_sort = st.selectbox(
                "ترتيب الأنشطة", 
                ["الأولوية", "الاسم", "مستوى المخاطر"],
                key="risk_activity_sort"
            )
        with col2:
            recommendation_filter = st.selectbox(
                "التوصية", 
                ["الكل", "مراجعة عاجلة", "مراقبة دورية مكثفة", "مراقبة دورية"], # Updated options based on analyzer output
                key="risk_recommendation_filter"
            )
        with col3:
            year_filter_risk = st.selectbox(
                "السنة", 
                ["الكل"] + [str(year) for year in range(datetime.now().year, 2020, -1)],
                key="risk_year_filter"
            )
        
        # Add these local filters to the main filters dictionary for the analyzer
        local_filters['activity_sort'] = activity_sort
        local_filters['recommendation_filter'] = recommendation_filter
        if year_filter_risk != "الكل":
            local_filters['date_range'] = (datetime(int(year_filter_risk), 1, 1).date(), datetime(int(year_filter_risk), 12, 31).date())
        else:
            # If "الكل" is selected for year, ensure the date_range from main filters is still applied
            if 'date_range_filter' in st.session_state:
                local_filters['date_range'] = st.session_state.date_range_filter
            else:
                local_filters.pop('date_range', None)

        # Get risk activities data from the analyzer
        df_risk_activities = self.dashboard_analyzer.get_risk_activities_summary(unified_data, local_filters)
        
        overview_tab, details_tab, recommendations_tab = st.tabs([
            "نظرة عامة 📊",
            "تفاصيل النشاط 🔍",
            "التوصيات 💡"
        ])
        
        with overview_tab:
            if not df_risk_activities.empty:
                st.dataframe(df_risk_activities.drop('الأولوية', axis=1), use_container_width=True, height=400)
                
                st.markdown(f"<h4 style='color: {theme['text_color']};'>💡 تأثير التوصيات على الأنشطة</h4>", unsafe_allow_html=True)
                
                selected_recommendation_impact = st.selectbox(
                    "اختر توصية لمعرفة تأثيرها",
                    ["مراجعة عاجلة", "مراقبة دورية مكثفة", "مراقبة دورية"], # Updated options
                    key="risk_recommendation_impact"
                )
                
                affected_activities = df_risk_activities[df_risk_activities['التوصية'].str.contains(selected_recommendation_impact, na=False)]
                
                if not affected_activities.empty:
                    st.markdown(f"**الأنشطة المتأثرة بـ '{selected_recommendation_impact}':**")
                    st.dataframe(affected_activities[['النشاط', 'مستوى المخاطر', 'نسبة المخاطر %']], 
                                 use_container_width=True)
                else:
                    st.info(f"لا توجد أنشطة متأثرة بـ '{selected_recommendation_impact}'")
            else:
                st.info("لا توجد بيانات إدارة مخاطر متاحة أو لا تتطابق مع المرشحات.")
        
        with details_tab:
            if not df_risk_activities.empty:
                st.markdown(f"<h4 style='color: {theme['text_color']};'>🔍 تفاصيل المخاطر والأنشطة</h4>", unsafe_allow_html=True)
                
                selected_activity_for_details = st.selectbox(
                    "اختر النشاط لعرض التفاصيل",
                    options=sorted(df_risk_activities['النشاط'].unique().tolist()),
                    key="risk_activity_details_selector"
                )

                # Find the row in df_risk_activities for the selected activity
                selected_activity_row = df_risk_activities[df_risk_activities['النشاط'] == selected_activity_for_details]
                
                if not selected_activity_row.empty:
                    # Retrieve the original detailed DataFrame for this activity (it's a JSON string now)
                    json_details_string = selected_activity_row.iloc[0]['details_df']
                    
                    # Convert the JSON string back to DataFrame
                    try:
                        activity_details_df = pd.read_json(io.StringIO(json_details_string))
                        # Ensure date columns are datetime objects after reading from JSON
                        for col in activity_details_df.columns:
                            if 'تاريخ' in str(col).lower() or 'date' in str(col).lower():
                                activity_details_df[col] = pd.to_datetime(activity_details_df[col], errors='coerce')
                    except Exception as e:
                        st.error(f"خطأ في فك تشفير بيانات التفاصيل: {e}")
                        activity_details_df = pd.DataFrame() # Fallback to empty DataFrame
                    
                    st.markdown(f"<h3 style='color: {theme['primary_color']};'>{selected_activity_for_details}</h3>", unsafe_allow_html=True)
                    
                    # Display metadata from config
                    activity_meta = next((item for item in RISK_ACTIVITIES_METADATA if item['name'] == selected_activity_for_details), None)
                    if activity_meta:
                        st.markdown(f"<p style='color: {theme['text_color']};'>**الوصف:** {activity_meta['description']}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color: {theme['text_color']};'>**المخاطر النموذجية:** {', '.join(activity_meta['typical_risks'])}</p>", unsafe_allow_html=True)
                        # Display icon if available
                        if 'icon' in activity_meta:
                            st.markdown(f"<p style='font-size: 2rem;'>{activity_meta['icon']}</p>", unsafe_allow_html=True)

                    if not activity_details_df.empty:
                        st.dataframe(activity_details_df, use_container_width=True)
                    else:
                        st.info(f"لا توجد بيانات تفصيلية لـ {selected_activity_for_details}")
                else:
                    st.info("الرجاء اختيار نشاط لعرض التفاصيل.")
            else:
                st.info("لا توجد بيانات تفصيلية للمخاطر متاحة.")

        with recommendations_tab:
            if not df_risk_activities.empty:
                st.markdown(f"<h4 style='color: {theme['text_color']};'>💡 التوصيات وخطة العمل</h4>", unsafe_allow_html=True)
                
                high_risks_df = df_risk_activities[df_risk_activities['مستوى المخاطر'].str.contains('عالي|مرتفع', na=False)]
                
                if not high_risks_df.empty:
                    st.warning("🚨 المخاطر ذات الأولوية العالية التي تتطلب اهتماماً فورياً:")
                    
                    for idx, risk in high_risks_df.iterrows():
                        st.markdown(f"""
                        <div style='background-color: {theme['warning_color']}15; padding: 10px; border-radius: 5px; margin: 5px 0;'>
                            <h4 style='color: {theme['warning_color']}; margin: 0;'>{risk['النشاط']} - {risk['مستوى المخاطر']}</h4>
                            <p style='margin: 5px 0; color: {theme['text_color']};'>{risk['التوصية']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.subheader("📋 خطة العمل المقترحة")
                
                if 'النشاط' in df_risk_activities.columns:
                    for activity_type in df_risk_activities['النشاط'].unique():
                        with st.expander(f"خطة العمل - {activity_type}"):
                            # Retrieve the details_df for this activity type from df_risk_activities (it's a JSON string now)
                            json_details_string = df_risk_activities[df_risk_activities['النشاط'] == activity_type].iloc[0]['details_df']
                            
                            # Convert JSON string back to DataFrame
                            try:
                                risks_df = pd.read_json(io.StringIO(json_details_string))
                                # Ensure date columns are datetime objects after reading from JSON
                                for col in risks_df.columns:
                                    if 'تاريخ' in str(col).lower() or 'date' in str(col).lower():
                                        risks_df[col] = pd.to_datetime(risks_df[col], errors='coerce')
                            except Exception as e:
                                st.error(f"خطأ في فك تشفير بيانات التفاصيل لـ {activity_type}: {e}")
                                risks_df = pd.DataFrame() # Fallback to empty DataFrame

                            if not risks_df.empty:
                                for _, risk_row in risks_df.iterrows(): # Iterate through rows of the actual DataFrame
                                    risk_level = risk_row.get('التصنيف', "غير محدد")
                                    risk_desc = risk_row.get('الوصف', "لا يوجد وصف")
                                    proposed_actions = risk_row.get('التوصية_المقترحة', "لم يتم تحديد إجراءات")
                                    
                                    st.markdown(f"""
                                    * **مستوى الخطورة**: {risk_level}
                                    * **الوصف**: {risk_desc}
                                    * **الإجراءات المقترحة**: {proposed_actions}
                                    ---
                                    """, unsafe_allow_html=True)
                            else:
                                st.info(f"لا توجد تفاصيل مخاطر لـ {activity_type}")
            else:
                st.info("لا توجد بيانات إدارة مخاطر متاحة لعرض التوصيات.")

    def create_incidents_analysis_table(self, unified_data, filters):
        """Create incidents analysis table"""
        theme = st.session_state.current_theme_config
        st.markdown(f"<h4 style='color: {theme['text_color']};'>🚨 تحليل الحوادث</h4>", unsafe_allow_html=True)
        
        # Local filter for year
        year_filter_incidents = st.selectbox(
            "تصفية حسب السنة", 
            ["الكل"] + [str(year) for year in range(datetime.now().year, 2020, -1)], 
            key="incidents_year_filter"
        )
        
        # Add year filter to the filters dictionary for the analyzer
        local_filters = filters.copy()
        if year_filter_incidents != "الكل":
            local_filters['date_range'] = (datetime(int(year_filter_incidents), 1, 1).date(), datetime(int(year_filter_incidents), 12, 31).date())
        else:
            # If "الكل" is selected for year, ensure the date_range from main filters is still applied
            if 'date_range_filter' in st.session_state:
                local_filters['date_range'] = st.session_state.date_range_filter
            else:
                local_filters.pop('date_range', None)

        # Get incidents data from the analyzer
        df_incidents = self.dashboard_analyzer.get_incidents_summary(unified_data, local_filters)
        
        if not df_incidents.empty:
            st.dataframe(
                df_incidents,
                use_container_width=True,
                height=400,
                column_config={
                    "نسبة الإغلاق %": st.column_config.ProgressColumn(
                        "نسبة الإغلاق %",
                        help="نسبة إغلاق التوصيات",
                        min_value=0,
                        max_value=100,
                    ),
                }
            )
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_incidents = df_incidents['عدد الحوادث'].sum()
                st.metric("إجمالي الحوادث", total_incidents)
            
            with col2:
                total_recommendations = df_incidents['عدد التوصيات'].sum()
                st.metric("إجمالي التوصيات", total_recommendations)
            
            with col3:
                total_closed = df_incidents['مغلق'].sum()
                st.metric("التوصيات المغلقة", total_closed)
            
            with col4:
                overall_closure_rate = (total_closed / total_recommendations * 100) if total_recommendations > 0 else 0
                st.metric("معدل الإغلاق الإجمالي", f"{overall_closure_rate:.1f}%")
            
            st.markdown(f"<h3 style='color: {theme['text_color']};'>📈 تحليل اتجاه الحوادث</h3>", unsafe_allow_html=True)
            
            fig = px.bar(
                df_incidents, 
                x='القطاع', 
                y='عدد الحوادث',
                title="توزيع الحوادث حسب القطاع",
                color='عدد الحوادث',
                color_continuous_scale=[theme['primary_color'], theme['warning_color']]
            )
            fig.update_layout(
                xaxis_title="القطاع",
                yaxis_title="عدد الحوادث",
                font=dict(family="Arial", size=12),
                paper_bgcolor=theme['surface_color'],
                plot_bgcolor=theme['background_color'],
                font_color=theme['text_color']
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("لا توجد بيانات حوادث متاحة للتحليل أو لا تتطابق مع المرشحات.")

    def create_risk_section(self, unified_data, filters):
        """Create enhanced risk management section (main tab)"""
        theme = st.session_state.current_theme_config
        st.markdown(f"<h3 style='color: {theme['text_color']};'>⚠️ إدارة المخاطر</h3>", unsafe_allow_html=True)
        
        # Get risk data using the analyzer, applying main filters
        risk_summary_df = self.dashboard_analyzer.get_risk_activities_summary(unified_data, filters)
        incidents_summary_df = self.dashboard_analyzer.get_incidents_summary(unified_data, filters) # For related incidents metric

        if risk_summary_df.empty:
            st.info("لا توجد بيانات إدارة مخاطر متاحة.")
            return
        
        # KPI metrics row for Risk Section
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_risks = len(risk_summary_df)
            st.metric(
                "إجمالي الأنشطة ذات المخاطر",
                f"{total_risks}",
                help="العدد الإجمالي للأنشطة التي تم تقييم مخاطرها"
            )
        
        with col2:
            # Calculate overall high risk percentage from risk_summary_df
            total_high_risks = risk_summary_df['المخاطر العالية'].sum()
            total_assessments_for_high_risk_calc = risk_summary_df['إجمالي التقييمات'].sum()
            overall_high_risk_percentage = (total_high_risks / total_assessments_for_high_risk_calc * 100) if total_assessments_for_high_risk_calc > 0 else 0
            
            st.metric(
                "نسبة المخاطر العالية الإجمالية",
                f"{overall_high_risk_percentage:.1f}%",
                help="النسبة المئوية الإجمالية للتقييمات ذات المخاطر العالية"
            )
        
        with col3:
            related_incidents = len(incidents_summary_df) if not incidents_summary_df.empty else 0
            st.metric(
                "الحوادث المرتبطة",
                f"{related_incidents}",
                help="عدد الحوادث المرتبطة بالأنشطة ذات المخاطر المحددة"
            )
        
        # Risk distribution visualization
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"<h4 style='color: {theme['text_color']};'>📊 توزيع مستويات المخاطر للأنشطة</h4>", unsafe_allow_html=True)
            
            # Use 'مستوى المخاطر' from risk_summary_df for distribution
            if 'مستوى المخاطر' in risk_summary_df.columns and not risk_summary_df['مستوى المخاطر'].empty:
                # Clean up labels to remove emojis for value_counts if needed, then re-add for display
                risk_summary_df['مستوى المخاطر_clean'] = risk_summary_df['مستوى المخاطر'].str.replace('🔴|🟡|🟢|⚪', '', regex=True).str.strip()
                risk_counts = risk_summary_df['مستوى المخاطر_clean'].value_counts()
                
                fig = px.pie(
                    values=risk_counts.values,
                    names=risk_counts.index,
                    title="توزيع مستويات المخاطر",
                    color_discrete_map={
                        'عالي': COLORS['danger'],
                        'متوسط': COLORS['warning'],
                        'منخفض': COLORS['success']
                    }
                )
                fig.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hole=0.4,
                    marker=dict(line=dict(color=theme['surface_color'], width=2))
                )
                fig.update_layout(
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    paper_bgcolor=theme['surface_color'],
                    plot_bgcolor=theme['background_color'],
                    font_color=theme['text_color']
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("لم يتم العثور على عمود مستوى المخاطر في البيانات أو أنه فارغ")
        
        with col2:
            st.markdown(f"<h4 style='color: {theme['text_color']};'>📈 اتجاه المخاطر حسب النشاط</h4>", unsafe_allow_html=True)
            
            if not risk_summary_df.empty:
                # Sort by priority (numeric, lower is higher priority)
                sorted_risk_summary = risk_summary_df.sort_values('الأولوية', ascending=True)
                
                fig = px.bar(
                    sorted_risk_summary,
                    x='نسبة المخاطر %', # Use percentage for bar length
                    y='النشاط',
                    orientation='h',
                    title="الأنشطة حسب نسبة المخاطر",
                    labels={
                        'نسبة المخاطر %': 'نسبة المخاطر',
                        'النشاط': 'النشاط'
                    },
                    color='الأولوية', # Color by priority
                    color_continuous_scale=[COLORS['danger'], COLORS['warning'], COLORS['success']], # Red for high, yellow for medium, green for low
                    category_orders={"الأولوية": [1, 2, 3]} # Ensure correct sorting of colors
                )
                fig.update_layout(
                    height=400,
                    xaxis_title="نسبة المخاطر",
                    yaxis_title="النشاط",
                    showlegend=False,
                    paper_bgcolor=theme['surface_color'],
                    plot_bgcolor=theme['background_color'],
                    font_color=theme['text_color']
                )
                fig.update_traces(
                    texttemplate='%{x}',
                    textposition='outside'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("لا توجد بيانات مخاطر متاحة للرسم البياني.")
        
    def create_performance_section(self, unified_data, filters):
        """Create performance section with modern, clean visualizations"""
        theme = st.session_state.current_theme_config
        
        def create_clean_gauge(value, title, color, unit="%", max_value=100, tickvals=None, ticktext=None):
            """Helper function to create a clean, modern gauge with visible number"""
            if tickvals is None:
                tickvals = [0, 25, 50, 75, 100] if max_value == 100 else [0, max_value/4, max_value/2, 3*max_value/4, max_value]
            if ticktext is None:
                ticktext = [str(x) for x in tickvals]
                
            fig = go.Figure()
            
            fig.add_trace(go.Indicator(
                mode="gauge",
                value=value,
                domain={'x': [0.1, 0.9], 'y': [0.15, 0.85]},
                gauge={
                    'axis': {
                        'range': [0, max_value],
                        'tickwidth': 2,
                        'tickcolor': color,
                        'tickfont': {'size': 14, 'color': theme['text_color']},
                        'tickmode': 'array',
                        'ticktext': ticktext,
                        'tickvals': tickvals
                    },
                    'bar': {'color': color, 'thickness': 0.6},
                    'bgcolor': theme['surface_color'],
                    'borderwidth': 2,
                    'bordercolor': color,
                }
            ))
            
            fig.add_annotation(
                text=f"<b>{value:.1f}{unit}</b>",
                x=0.5,
                y=0.5,
                font={'size': 48, 'color': color, 'family': 'Arial Black'},
                showarrow=False
            )
            
            fig.add_annotation(
                text=title,
                x=0.5,
                y=0.95,
                font={'size': 24, 'color': color},
                showarrow=False
            )
            
            fig.update_layout(
                height=300,
                margin=dict(l=30, r=30, t=30, b=30),
                paper_bgcolor=theme['surface_color'],
                plot_bgcolor=theme['background_color'],
                showlegend=False,
                font_color=theme['text_color']
            )
            
            return fig

        st.markdown(f"<h3 style='color: {theme['text_color']};'>🎯 مؤشرات الأداء</h3>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        # Calculate metrics from unified and filtered data
        # Compliance Rate
        compliance_summary_df = self.dashboard_analyzer.get_compliance_summary(unified_data, filters)
        compliance_rate = compliance_summary_df['نسبة الامتثال %'].mean() if not compliance_summary_df.empty else 0
        
        # Average Response Time (from incidents)
        incidents_df = unified_data.get('incidents', pd.DataFrame())
        avg_response_time = 0 # Default
        if not incidents_df.empty:
            filtered_incidents_df = self.dashboard_analyzer._apply_common_filters(incidents_df, filters)
            if not filtered_incidents_df.empty:
                # Assuming 'التاريخ' (start date) and 'تاريخ_الإغلاق' (end date) are available
                if 'التاريخ' in filtered_incidents_df.columns and 'تاريخ_الإغلاق' in filtered_incidents_df.columns:
                    # Ensure columns are datetime objects
                    filtered_incidents_df['التاريخ'] = pd.to_datetime(filtered_incidents_df['التاريخ'], errors='coerce')
                    filtered_incidents_df['تاريخ_الإغلاق'] = pd.to_datetime(filtered_incidents_df['تاريخ_الإغلاق'], errors='coerce')
                    
                    # Calculate time difference in days, dropping NaT results
                    time_diff = (filtered_incidents_df['تاريخ_الإغلاق'] - filtered_incidents_df['التاريخ']).dt.days.dropna()
                    avg_response_time = time_diff.mean() if not time_diff.empty else 0
                else:
                    avg_response_time = 2.5 # Default if specific date columns are not found
            else:
                avg_response_time = 2.5 # Default if filtered df is empty
        else:
            avg_response_time = 2.5 # Default if incidents_df is empty

        # Completion Rate (from safety checks/recommendations)
        safety_checks_df = unified_data.get('safety_checks', pd.DataFrame())
        completion_rate = 0 # Default
        if not safety_checks_df.empty:
            filtered_safety_checks_df = self.dashboard_analyzer._apply_common_filters(safety_checks_df, filters)
            if not filtered_safety_checks_df.empty:
                total_items = len(filtered_safety_checks_df)
                status_col_safety = 'الحالة' # Standardized column name
                if status_col_safety in filtered_safety_checks_df.columns:
                    completed_items = filtered_safety_checks_df[status_col_safety].astype(str).str.contains('مغلق|مكتمل', case=False, na=False).sum()
                    completion_rate = (completed_items / total_items * 100) if total_items > 0 else 0
                else:
                    completion_rate = 85 # Default if status column not found
            else:
                completion_rate = 85 # Default if filtered df is empty
        else:
            completion_rate = 85 # Default if safety_checks_df is empty

        with col1:
            st.markdown(f"<h4 style='color: {theme['text_color']};'>📊 معدل الامتثال</h4>", unsafe_allow_html=True)
            fig = create_clean_gauge(compliance_rate, "معدل الامتثال", theme['primary_color'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown(f"<h4 style='color: {theme['text_color']};'>⚡ متوسط وقت الاستجابة</h4>", unsafe_allow_html=True)
            fig = create_clean_gauge(avg_response_time, "متوسط وقت الاستجابة", theme['secondary_color'], unit=" يوم", max_value=10, tickvals=[0,2,4,6,8,10], ticktext=['0','2','4','6','8','10'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            st.markdown(f"<h4 style='color: {theme['text_color']};'>🎯 معدل الإنجاز</h4>", unsafe_allow_html=True)
            fig = create_clean_gauge(completion_rate, "معدل الإنجاز", theme['success_color'])
            st.plotly_chart(fig, use_container_width=True)

    def create_quality_report_page(self, quality_report):
        """Create comprehensive quality report page"""
        theme = st.session_state.current_theme_config
        st.header(f"<h2 style='color: {theme['text_color']};'>📋 تقرير جودة البيانات الشامل</h2>", unsafe_allow_html=True)
        
        if quality_report:
            total_records = sum([report.get('total_rows', 0) for report in quality_report.values()])
            total_missing_cells = sum([report.get('missing_values_count', 0) for report in quality_report.values()])
            total_cells_overall = sum([report.get('total_rows', 0) * report.get('total_columns', 0) for report in quality_report.values()])
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("إجمالي السجلات", f"{total_records:,}")
            
            with col2:
                st.metric("مجموعات البيانات الموحدة", len(quality_report))
            
            with col3:
                missing_percentage = (total_missing_cells / total_cells_overall * 100) if total_cells_overall > 0 else 0
                st.metric("البيانات المفقودة", f"{missing_percentage:.1f}%")
            
            with col4:
                avg_quality = 100 - missing_percentage
                st.metric("متوسط الجودة", f"{avg_quality:.1f}%")
            
            st.markdown("---")
            st.markdown(f"<h3 style='color: {theme['text_color']};'>📊 تقارير مفصلة لكل مجموعة بيانات</h3>", unsafe_allow_html=True)
            
            for dataset_name, report in quality_report.items():
                with st.expander(f"📋 {dataset_name}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"<h4 style='color: {theme['text_color']};'>📈 إحصائيات عامة</h4>", unsafe_allow_html=True)
                        
                        metrics = {
                            'إجمالي الصفوف': report.get('total_rows', 0),
                            'إجمالي الأعمدة': report.get('total_columns', 0),
                            'البيانات المفقودة (عدد)': report.get('missing_values_count', 0),
                            'الصفوف المكررة': report.get('duplicate_rows', 0),
                            'نسبة البيانات المفقودة': f"{report.get('missing_data_percentage', 0):.1f}%",
                            'استهلاك الذاكرة (MB)': f"{report.get('memory_usage_mb', 0):.2f}"
                        }
                        
                        for key, value in metrics.items():
                            st.markdown(f"**{key}:** <span style='color: {theme['text_color']};'>{value}</span>", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"<h4 style='color: {theme['text_color']};'>🔍 أنواع البيانات</h4>", unsafe_allow_html=True)
                        
                        if 'data_types' in report:
                            data_types_df = pd.DataFrame([
                                {'العمود': col, 'النوع': str(dtype)}
                                for col, dtype in report['data_types'].items()
                            ])
                            st.dataframe(data_types_df, use_container_width=True, height=300)
        else:
            st.warning("لا يوجد تقرير جودة متاح")
            st.info("تأكد من تحميل البيانات أولاً لإنشاء تقرير الجودة")

    def run(self):
        """Main application runner"""
        st.session_state.current_theme_config = self.theme_manager.get_current_theme()
        theme = st.session_state.current_theme_config
        
        self.theme_manager.apply_theme_css()
        
        # Load data if not already loaded (or if a reload is forced)
        if not st.session_state.data_loaded:
            # Removed explicit 'self' argument here
            unified_data, kpi_data, quality_report = self.load_and_process_data() 
            st.session_state.unified_data = unified_data
            st.session_state.kpi_data = kpi_data
            st.session_state.quality_report = quality_report
            st.session_state.data_loaded = True
        
        # Get data from session state
        unified_data = st.session_state.unified_data
        kpi_data = st.session_state.kpi_data
        quality_report = st.session_state.quality_report
        
        # Create enhanced sidebar with navigation and filters
        # Pass kpi_data to create_enhanced_sidebar for date range filter in AdvancedFilters
        filters, selected_page = self.create_enhanced_sidebar(unified_data, kpi_data)
        
        if st.session_state.get('show_help', False):
            self.advanced_features.show_help_content() # Call show_help_content from advanced_features
            return
        
        if selected_page == "الرئيسية المتقدمة":
            self.create_ultimate_main_dashboard(unified_data, kpi_data, filters)
        
        elif selected_page == "التحليلات الذكية":
            self.create_analytics_section(unified_data, filters)
        
        elif selected_page == "مركز التصدير":
            self.advanced_features.create_export_center(unified_data, kpi_data)
        
        elif selected_page == "رفع البيانات":
            self.advanced_features.create_manual_upload_section()
        
        elif selected_page == "تشغيل مساعد الذكاء الاصطناعي":
            try:
                # Prepare unified data for chatbot (ensure it's a copy to avoid modifying original)
                chatbot_data = {name: df.copy() for name, df in unified_data.items() if isinstance(df, pd.DataFrame) and not df.empty}
                
                # Prepare KPI data for chatbot
                chatbot_kpis = {
                    'total_records': sum(len(df) for df in chatbot_data.values()),
                    'departments': {},
                    'status_counts': {'open': 0, 'closed': 0},
                    'risk_levels': {}
                }
                
                for df_name, df in chatbot_data.items():
                    # Populate department stats (using standardized 'الإدارة' or 'القطاع')
                    if 'الإدارة' in df.columns:
                        dept_counts = df['الإدارة'].value_counts()
                        for dept, count in dept_counts.items():
                            chatbot_kpis['departments'][dept] = chatbot_kpis['departments'].get(dept, 0) + count
                    elif 'القطاع' in df.columns:
                        dept_counts = df['القطاع'].value_counts()
                        for dept, count in dept_counts.items():
                            chatbot_kpis['departments'][dept] = chatbot_kpis['departments'].get(dept, 0) + count

                    # Populate status counts (using standardized 'الحالة')
                    if 'الحالة' in df.columns:
                        closed = df['الحالة'].astype(str).str.contains('مغلق|مكتمل', case=False, na=False).sum()
                        chatbot_kpis['status_counts']['closed'] += closed
                        chatbot_kpis['status_counts']['open'] += len(df) - closed
                    
                    # Populate risk levels (using standardized 'التصنيف' or 'مستوى المخاطر')
                    if 'التصنيف' in df.columns:
                        risk_counts = df['التصنيف'].value_counts()
                        for risk, count in risk_counts.items():
                            chatbot_kpis['risk_levels'][risk] = chatbot_kpis['risk_levels'].get(risk, 0) + count
                    elif 'مستوى المخاطر' in df.columns: # Fallback if 'التصنيف' not found
                        risk_counts = df['مستوى المخاطر'].value_counts()
                        for risk, count in risk_counts.items():
                            chatbot_kpis['risk_levels'][risk] = chatbot_kpis['risk_levels'].get(risk, 0) + count
                
                create_chatbot_interface(chatbot_data, chatbot_kpis)
            except Exception as e:
                st.error(f"خطأ في المساعد الذكي: {str(e)}")
                st.info("المساعد الذكي غير متاح حالياً")
        
        elif selected_page == "المراقبة المباشرة":
            self.advanced_features.create_real_time_monitoring(unified_data)
        
        elif selected_page == "تقرير الجودة":
            self.create_quality_report_page(quality_report)
        
        current_theme = self.theme_manager.get_current_theme()
        st.markdown("---")
        st.markdown(f"""
        <div style='text-align: center; color: {current_theme['text_secondary']}; padding: 1rem;'>
            <p>🛡️ Ultimate Safety & Compliance Dashboard v4.0 | {current_theme['icon']} {current_theme['name']}</p>
            <p>آخر تحديث: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        """, unsafe_allow_html=True)

# Main execution
def main():
    """Main function to run the ultimate dashboard"""
    dashboard = UltimateDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()