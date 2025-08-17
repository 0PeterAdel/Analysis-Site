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
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import components
from src.utils.data_processor import SafetyDataProcessor as DataProcessor
from src.components.advanced_features import AdvancedFeatures
from src.components.theme_manager import ThemeManager
from src.components.gemini_chatbot import create_chatbot_interface

# Page configuration
st.set_page_config(
    page_title="🛡️ Ultimate Safety & Compliance Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
data_processor = DataProcessor()
advanced_features = AdvancedFeatures()
theme_manager = ThemeManager()

class UltimateDashboard:
    def __init__(self):
        self.data_processor = data_processor
        self.advanced_features = advanced_features
        self.theme_manager = theme_manager
        
        # Initialize session state
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
        # Ensure current_theme_config is always available in session state
        if 'current_theme_config' not in st.session_state:
            st.session_state.current_theme_config = self.theme_manager.get_current_theme()

    def create_modern_navigation(self):
        """Create modern navigation at the top of sidebar"""
        # Get current theme to apply dynamic colors
        theme = st.session_state.current_theme_config
        
        st.sidebar.markdown(f"""
        <div style='text-align: center; padding: 1rem; background: {theme['gradient_primary']}; 
                    border-radius: 10px; margin-bottom: 1rem;'>
            <h2 style='margin: 0; color: {theme['text_color']};'>🛡️ لوحة التحكم</h2>
            <p style='margin: 0; opacity: 0.9; color: {theme['text_secondary']};'>Safety & Compliance Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Main navigation
        pages = {
            "الرئيسية المتقدمة": "🏠",
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

    def create_enhanced_filters(self, unified_data):
        """Create enhanced filters with better design"""
        theme = st.session_state.current_theme_config
        
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"""
        <div style='text-align: center; padding: 0.5rem; background: {theme['primary_color']}15; 
                    border-radius: 8px; margin-bottom: 1rem; border: 1px solid {theme['primary_color']}25;'>
            <h3 style='margin: 0; color: {theme['primary_color']}; font-weight: bold; text-shadow: 0 0 1px {theme["primary_color"]}30;'>🔍 المرشحات المتقدمة</h3>
        </div>
        """, unsafe_allow_html=True)

        filters = {}
        
        if not unified_data:
            st.sidebar.info("لا توجد بيانات متاحة للتصفية")
            return filters

        # Filter presets section
        with st.sidebar.expander("⚙️ إعدادات المرشحات", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ مسح جميع المرشحات", key="clear_all_filters"):
                    st.rerun()
            
            with col2:
                saved_presets = self.get_saved_filter_presets()
                if saved_presets:
                    selected_preset = st.selectbox(
                        "تحميل مرشح محفوظ", 
                        [""] + list(saved_presets.keys()),
                        key="load_filter_preset"
                    )
                    if selected_preset:
                        filters.update(saved_presets[selected_preset])

        # Date range filter
        st.sidebar.markdown("#### 📅 نطاق التاريخ")
        # Determine available global date range from data
        min_date_global = None
        max_date_global = None
        try:
            for df in unified_data.values():
                if df is None or df.empty:
                    continue
                for col in df.columns:
                    try:
                        if 'تاريخ' in str(col) or 'date' in str(col).lower():
                            dates = pd.to_datetime(df[col], errors='coerce')
                            if dates.notna().any():
                                dmin = dates.min()
                                dmax = dates.max()
                                if pd.notna(dmin):
                                    min_date_global = dmin if min_date_global is None else min(min_date_global, dmin)
                                if pd.notna(dmax):
                                    max_date_global = dmax if max_date_global is None else max(max_date_global, dmax)
                    except Exception:
                        continue
        except Exception:
            pass
        if min_date_global is None or max_date_global is None:
            min_date_global = datetime.now() - timedelta(days=365)
            max_date_global = datetime.now()
        date_range = st.sidebar.date_input(
            "اختر النطاق الزمني",
            value=(min_date_global.date(), max_date_global.date()),
            key="date_range_filter"
        )
        if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
            filters['date_range'] = date_range

        # Sector filter with select all option
        st.sidebar.markdown("#### 🏢 القطاعات")
        
        # Get available sectors
        available_sectors = set()
        for dataset_name, df in unified_data.items():
            if not df.empty:
                sector_columns = [col for col in df.columns if 'قطاع' in str(col) or 'sector' in str(col).lower()]
                for col in sector_columns:
                    available_sectors.update(df[col].dropna().unique())
        
        available_sectors = sorted(list(available_sectors))
        
        if available_sectors:
            # Select all/none buttons
            col1, col2 = st.sidebar.columns(2)
            with col1:
                if st.button("✅ تحديد الكل", key="select_all_sectors"):
                    st.session_state.selected_sectors = available_sectors
            with col2:
                if st.button("❌ إلغاء الكل", key="deselect_all_sectors"):
                    st.session_state.selected_sectors = []
            
            # Multi-select for sectors
            selected_sectors = st.sidebar.multiselect(
                "اختر القطاعات",
                available_sectors,
                default=st.session_state.get('selected_sectors', available_sectors[:3]),
                key="sector_multiselect"
            )
            filters['sectors'] = selected_sectors

        # Status filter
        st.sidebar.markdown("#### 📊 الحالة")
        status_options = ["الكل", "مفتوح", "مغلق", "قيد المراجعة", "مكتمل"]
        selected_status = st.sidebar.multiselect(
            "اختر الحالات",
            status_options,
            default=["الكل"],
            key="status_filter"
        )
        filters['status'] = selected_status

        # Priority filter
        st.sidebar.markdown("#### ⚡ الأولوية")
        priority_options = ["الكل", "عالي", "متوسط", "منخفض"]
        selected_priority = st.sidebar.selectbox(
            "مستوى الأولوية",
            priority_options,
            key="priority_filter"
        )
        filters['priority'] = selected_priority

        # Risk level filter
        st.sidebar.markdown("#### ⚠️ مستوى المخاطر")
        risk_options = ["الكل", "مرتفع", "متوسط", "منخفض"]
        selected_risk = st.sidebar.selectbox(
            "مستوى المخاطر",
            risk_options,
            key="risk_level_filter"
        )
        filters['risk_level'] = selected_risk

        # Save current filter preset
        st.sidebar.markdown("---")
        with st.sidebar.expander("💾 حفظ المرشح الحالي"):
            preset_name = st.text_input("اسم المرشح", key="preset_name_input")
            if st.button("حفظ", key="save_filter_preset") and preset_name:
                self.save_filter_preset(preset_name, filters)
                st.success(f"تم حفظ المرشح: {preset_name}")

        return filters

    def get_saved_filter_presets(self):
        """Get saved filter presets"""
        return st.session_state.get('filter_presets', {})

    def save_filter_preset(self, name, filters):
        """Save filter preset"""
        if 'filter_presets' not in st.session_state:
            st.session_state.filter_presets = {}
        st.session_state.filter_presets[name] = filters.copy()

    def create_enhanced_sidebar(self, unified_data):
        """Create enhanced sidebar with navigation first"""
        # Navigation first (at the top)
        selected_page = self.create_modern_navigation()
        
        # Theme selector
        theme_manager.create_theme_selector()
        
        # Enhanced filters
        filters = self.create_enhanced_filters(unified_data)
        
        # Notifications
        advanced_features.show_notifications()
        
        # Performance monitor
        advanced_features.create_performance_monitor()
        
        # Help system
        advanced_features.create_help_system()
        
        # Theme info - REMOVED as per user request
        # theme_manager.create_theme_info() 
        
        return filters, selected_page

    def load_and_process_data(self):
        """Load and process all data sources"""
        try:
            processor = DataProcessor()
            
            # Load all data from database directory
            all_data = processor.load_all_data()
            
            # Flatten the data structure for easier access
            unified_data = {}
            for source_name, source_data in all_data.items():
                if isinstance(source_data, dict):
                    # Excel file with multiple sheets
                    for sheet_name, sheet_data in source_data.items():
                        unified_data[f"{source_name}_{sheet_name}"] = sheet_data
                else:
                    # CSV file
                    unified_data[source_name.replace('.csv', '')] = sheet_data # Changed to sheet_data to match Excel case
            
            # Generate KPIs
            kpi_data = processor.generate_kpis(unified_data)
            
            # Generate quality report
            quality_report = processor.generate_quality_report(unified_data)
            
            return processor, unified_data, kpi_data, quality_report
            
        except Exception as e:
            st.error(f"خطأ في تحميل البيانات: {str(e)}")
            advanced_features.add_notification(f"خطأ في تحميل البيانات: {str(e)}", "error")
            return None, {}, {}, {}

    def create_ultimate_main_dashboard(self, unified_data, kpi_data, filters):
        """Create the ultimate main dashboard"""
        theme = st.session_state.current_theme_config
        
        # Animated header
        st.markdown(f'''
        <div class="main-header fade-in-up">
            🛡️ Ultimate Safety & Compliance Dashboard
        </div>
        <div style="text-align: center; margin-bottom: 2rem; color: {theme['text_secondary']};">
            مرحباً بك في لوحة معلومات السلامة والامتثال | آخر تحديث: {datetime.now().strftime("%H:%M")}
        </div>
        ''', unsafe_allow_html=True)
        
        # Apply filters
        filtered_data = self.apply_filters(unified_data, filters)
        
        # KPI Cards
        self.create_kpi_cards(kpi_data)
        
        # Main content tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 نظرة عامة", 
            "📈 التحليلات", 
            "⚠️ المخاطر", 
            "🎯 الأداء"
        ])
        
        with tab1:
            self.create_overview_section(filtered_data)
        
        with tab2:
            self.create_analytics_section(filtered_data)
        
        with tab3:
            self.create_risk_section(filtered_data)
        
        with tab4:
            self.create_performance_section(filtered_data)

    def apply_filters(self, unified_data, filters):
        """Apply filters to unified data"""
        filtered_data = {}
        
        for dataset_name, df in unified_data.items():
            if df.empty:
                filtered_data[dataset_name] = df
                continue
                
            filtered_df = df.copy()
            
            # Apply sector filter
            if 'sectors' in filters and filters['sectors']:
                sector_columns = [col for col in df.columns if 'قطاع' in str(col) or 'sector' in str(col).lower()]
                if sector_columns:
                    # Ensure column exists before filtering
                    if sector_columns[0] in filtered_df.columns:
                        sector_mask = filtered_df[sector_columns[0]].isin(filters['sectors'])
                        filtered_df = filtered_df[sector_mask]
            
            # Apply status filter
            if 'status' in filters and filters['status'] and 'الكل' not in filters['status']:
                status_columns = [col for col in df.columns if 'حالة' in str(col) or 'status' in str(col).lower()]
                if status_columns:
                    # Ensure column exists before filtering
                    if status_columns[0] in filtered_df.columns:
                        status_mask = filtered_df[status_columns[0]].str.contains('|'.join(filters['status']), case=False, na=False)
                        filtered_df = filtered_df[status_mask]
            
            # Apply date range filter
            if 'date_range' in filters and len(filters['date_range']) == 2:
                date_columns = [col for col in df.columns if 'تاريخ' in str(col) or 'date' in str(col).lower()]
                if date_columns:
                    # Ensure column exists before filtering
                    if date_columns[0] in filtered_df.columns:
                        try:
                            filtered_df[date_columns[0]] = pd.to_datetime(filtered_df[date_columns[0]], errors='coerce')
                            start_date, end_date = filters['date_range']
                            date_mask = (filtered_df[date_columns[0]] >= pd.Timestamp(start_date)) & \
                                        (filtered_df[date_columns[0]] <= pd.Timestamp(end_date))
                            filtered_df = filtered_df[date_mask]
                        except:
                            pass
            
            filtered_data[dataset_name] = filtered_df
        
        return filtered_data

    def create_kpi_cards(self, kpi_data):
        """Create compact, meaningful KPI cards from nested KPI dicts"""
        theme = st.session_state.current_theme_config
        
        if not kpi_data:
            st.info("لا توجد مؤشرات أداء متاحة")
            return

        # Aggregate KPIs across all datasets
        total_records = 0
        open_count = 0
        closed_count = 0
        activities_set = set()
        min_date = None
        max_date = None

        for data in kpi_data.values():
            try:
                total_records += int(data.get('total_records', 0))
            except Exception:
                pass

            status_dist = data.get('status_distribution', {}) or {}
            # Normalize keys to string
            open_count += int(status_dist.get('مفتوح', 0) or 0) + int(status_dist.get('Open', 0) or 0)
            closed_count += int(status_dist.get('مغلق', 0) or 0) + int(status_dist.get('Closed', 0) or 0)

            act_dist = data.get('activity_distribution', {}) or {}
            activities_set.update([str(k) for k in act_dist.keys()])

            dr = data.get('date_range')
            if isinstance(dr, dict) and dr.get('min_date') is not None and dr.get('max_date') is not None:
                cur_min = pd.to_datetime(dr['min_date'], errors='coerce')
                cur_max = pd.to_datetime(dr['max_date'], errors='coerce')
                if pd.notna(cur_min):
                    min_date = cur_min if min_date is None else min(min_date, cur_min)
                if pd.notna(cur_max):
                    max_date = cur_max if max_date is None else max(max_date, cur_max)

        datasets_count = len(kpi_data)
        closure_rate = (closed_count / (open_count + closed_count) * 100) if (open_count + closed_count) > 0 else 0

        # Prepare cards (4-5 concise cards only)
        cards = [
            {"label": "إجمالي السجلات", "value": f"{total_records:,}", "color": theme['primary_color']},
            {"label": "مفتوح", "value": f"{open_count:,}", "color": theme['warning_color']},
            {"label": "مغلق", "value": f"{closed_count:,}", "color": theme['success_color']},
            {"label": "نسبة الإغلاق %", "value": f"{closure_rate:.1f}", "color": theme['info_color']},
            {"label": "مجموعات البيانات", "value": f"{datasets_count}", "color": theme['secondary_color']},
        ]
        
        # Optional date range card if available
        if min_date is not None and max_date is not None:
            cards.append({
                "label": "نطاق التاريخ", 
                "value": f"{min_date.date()} → {max_date.date()}",
                "color": theme['text_secondary']
            })

        # Render up to 4 per row
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

    def create_overview_section(self, filtered_data):
        """Create overview section"""
        theme = st.session_state.current_theme_config
        st.markdown(f"<h3 style='color: {theme['text_color']};'>📊 نظرة عامة على البيانات</h3>", unsafe_allow_html=True)
        
        if not filtered_data:
            st.info("لا توجد بيانات متاحة")
            return
        
        # Data summary
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"<h4 style='color: {theme['text_color']};'>📈 ملخص البيانات</h4>", unsafe_allow_html=True)
            summary_data = []
            for dataset_name, df in filtered_data.items():
                if not df.empty:
                    summary_data.append({
                        'مجموعة البيانات': dataset_name,
                        'عدد السجلات': len(df),
                        'عدد الأعمدة': len(df.columns)
                    })
            
            if summary_data:
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True)
        
        with col2:
            st.markdown(f"<h4 style='color: {theme['text_color']};'>📊 توزيع البيانات</h4>", unsafe_allow_html=True)
            if summary_data:
                fig = px.pie(
                    summary_df, 
                    values='عدد السجلات', 
                    names='مجموعة البيانات',
                    title="توزيع السجلات حسب مجموعة البيانات"
                )
                # Update Plotly chart colors and background for theme consistency
                fig.update_layout(
                    paper_bgcolor=theme['surface_color'],
                    plot_bgcolor=theme['background_color'],
                    font_color=theme['text_color']
                )
                st.plotly_chart(fig, use_container_width=True)

    def create_analytics_section(self, filtered_data):
        """Create analytics section"""
        theme = st.session_state.current_theme_config
        st.markdown(f"<h3 style='color: {theme['text_color']};'>🧠 التحليلات المتقدمة</h3>", unsafe_allow_html=True)
        
        # Enhanced analytics tabs
        tab1, tab2, tab3 = st.tabs([
            "📊 جدول الامتثال للقطاعات الأربعة", 
            "⚠️ إدارة المخاطر - جدول الأنشطة", 
            "🚨 تحليل الحوادث"
        ])
        
        with tab1:
            self.create_closing_compliance_table(filtered_data)
        
        with tab2:
            self.create_risk_management_activity_table(filtered_data)
        
        with tab3:
            self.create_incidents_analysis_table(filtered_data)

    def _find_dataset_by_keywords(self, data_dict, keywords):
        """Return first dataframe whose key contains any of the keywords"""
        if not data_dict:
            return pd.DataFrame()
        for name, df in data_dict.items():
            key_lower = str(name).lower()
            if any(kw.lower() in key_lower for kw in keywords):
                return df
        return pd.DataFrame()

    def create_closing_compliance_table(self, filtered_data):
        """Create enhanced closing compliance table for sectors"""
        theme = st.session_state.current_theme_config
        st.markdown(f"<h4 style='color: {theme['text_color']};'>📊 جدول الامتثال حسب القطاع</h4>", unsafe_allow_html=True)
        
        # Fixed sectors list for consistent data
        sectors_fixed = ["قطاع المشاريع", "قطاع التشغيل", "قطاع الخدمات", "قطاع التخصيص", "أخرى"]
        
        # Initialize session state for clicked sector
        if 'clicked_sector' not in st.session_state:
            st.session_state.clicked_sector = None
        
        # Create tabs for different views
        overview_tab, details_tab = st.tabs(["نظرة عامة", "تفاصيل القطاع"])
        
        # Get inspection data dynamically
        inspection_data = self._find_dataset_by_keywords(filtered_data, ["تفتيش", "inspection"])
        if inspection_data.empty:
            st.info("لا توجد بيانات تفتيش متاحة")
            return
        
        # Try to detect sector and status columns
        sector_col = next((c for c in inspection_data.columns if any(x in str(c) for x in ["القطاع", "قطاع", "الإدارة", "ادارة", "إدارة", "department", "sector"])), None)
        status_col = next((c for c in inspection_data.columns if any(x in str(c) for x in ["الحالة", "status"])), None)
        
        if sector_col is None or status_col is None:
            st.warning("تعذر العثور على أعمدة القطاع/الحالة في بيانات التفتيش")
            st.dataframe(inspection_data.head(20), use_container_width=True)
            return
        
        # Build sector options from data
        sector_values = sorted([s for s in inspection_data[sector_col].dropna().unique().tolist()][:50])
        if not sector_values:
            sector_values = sectors_fixed  # Use the fixed sectors list
        
        # Create filters
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_sectors = st.multiselect(
                "اختر القطاعات", 
                sector_values, 
                default=sector_values[: min(5, len(sector_values))],
                key="compliance_sectors_filter"
            )
        with col2:
            status_filter = st.selectbox(
                "حالة الامتثال", 
                ["الكل", "مغلق", "مفتوح"],
                key="compliance_status_filter"
            )
        with col3:
            year_filter = st.selectbox(
                "السنة", 
                ["الكل"] + [str(year) for year in range(datetime.now().year, 2020, -1)], # Dynamic years
                key="compliance_year_filter"
            )
        
        with overview_tab:
            # Process compliance data with enhanced accuracy
            compliance_data = []
            df = inspection_data.copy()
            
            # Detect date column and process dates
            date_col = next((c for c in df.columns if "تاريخ" in str(c) or "date" in str(c).lower()), None)
            if date_col:
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                if year_filter != "الكل":
                    df = df[df[date_col].dt.year == int(year_filter)]
                
                # Add quarter and month for detailed analysis
                df['quarter'] = df[date_col].dt.quarter
                df['month'] = df[date_col].dt.month
            
            if selected_sectors:
                df = df[df[sector_col].isin(selected_sectors)]
            
            # Enhanced sector analysis
            for sector in (selected_sectors or sectors_fixed):
                sector_df = df[df[sector_col].astype(str).str.contains(str(sector), na=False)]
                if sector_df.empty:
                    continue
                
                # Basic metrics
                total_records = len(sector_df)
                closed_records = sector_df[status_col].astype(str).str.contains('مغلق|مكتمل|closed', case=False, na=False).sum()
                compliance_percentage = (closed_records / total_records * 100) if total_records > 0 else 0
                
                # Trend analysis
                recent_records = sector_df[sector_df[date_col] >= (pd.Timestamp.now() - pd.Timedelta(days=90))]
                recent_compliance = 0
                if not recent_records.empty:
                    recent_closed = recent_records[status_col].astype(str).str.contains('مغلق|مكتمل|closed', case=False, na=False).sum()
                    recent_compliance = (recent_closed / len(recent_records) * 100) if len(recent_records) > 0 else 0
                
                # Calculate compliance trend
                trend = recent_compliance - compliance_percentage
            
                # Enhanced recommendations based on multiple factors
                if compliance_percentage >= 90:
                    if trend >= 0:
                        recommendation = "ممتاز - استمر في الأداء الجيد"
                        status_color = "🟢"
                        priority = "منخفض"
                    else:
                        recommendation = "ممتاز مع تنبيه - راقب الانخفاض الأخير"
                        status_color = "🟢"
                        priority = "متوسط"
                elif compliance_percentage >= 70:
                    if trend > 5:
                        recommendation = "جيد مع تحسن - استمر في التطوير"
                        status_color = "🟡"
                        priority = "متوسط"
                    elif trend < -5:
                        recommendation = "يحتاج اهتمام - معدل الامتثال في انخفاض"
                        status_color = "🟡"
                        priority = "عالي"
                    else:
                        recommendation = "جيد - يحتاج تحسين طفيف"
                        status_color = "🟡"
                        priority = "متوسط"
                else:
                    if trend > 5:
                        recommendation = "يحتاج تحسين مع وجود تقدم إيجابي"
                        status_color = "🔴"
                        priority = "عالي"
                    else:
                        recommendation = "يحتاج تحسين عاجل وخطة عمل فورية"
                        status_color = "🔴"
                        priority = "عاجل"
            
                # Enhanced data structure
                sector_data = {
                    'القطاع': sector,
                    'إجمالي السجلات': total_records,
                    'السجلات المغلقة': int(closed_records),
                    'السجلات المفتوحة': int(total_records - closed_records),
                    'نسبة الامتثال %': float(compliance_percentage),
                    'اتجاه التغيير': f"{'+' if trend > 0 else ''}{trend:.1f}%",
                    'الحالة': f"{status_color} {'مغلق' if compliance_percentage >= 50 else 'مفتوح'}",
                    'الأولوية': priority,
                    'التوصية': recommendation,
                    'trend_value': trend,
                    'recent_compliance': recent_compliance
                }
                
                # Add sector detail data
                if not recent_records.empty:
                    quarterly_data = recent_records.groupby('quarter')[status_col].agg(lambda x: (x.astype(str).str.contains('مغلق|مكتمل|closed', case=False, na=False).sum() / len(x) * 100))
                    sector_data['quarterly_trends'] = quarterly_data.to_dict()
                
                compliance_data.append(sector_data)
            
            if compliance_data:
                out_df = pd.DataFrame(compliance_data)
                
                # Display interactive table with enhanced features
                st.dataframe(
                    out_df.drop(['trend_value', 'recent_compliance', 'quarterly_trends'], axis=1, errors='ignore'),
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
                
                # Add detailed analysis section
                st.markdown(f"<h3 style='color: {theme['text_color']};'>📊 تحليل تفصيلي</h3>", unsafe_allow_html=True)
                
                # Create columns for metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    avg_compliance = out_df['نسبة الامتثال %'].mean()
                    st.markdown(f"""
                        <div style='background-color: {theme['surface_color']}; padding: 1rem; border-radius: 8px;
                             border: 1px solid {theme['primary_color']}; color: {theme['text_color']};'>
                            <p style='font-size: 1rem; margin: 0;'>متوسط نسبة الامتثال</p>
                            <h2 style='margin: 0.5rem 0; color: {theme['primary_color']};'>{avg_compliance:.1f}%</h2>
                            <p style='font-size: 0.9rem; margin: 0; color: {"green" if out_df["trend_value"].mean() > 0 else "red"};'>
                                {out_df["trend_value"].mean():.1f}%
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    high_priority = len(out_df[out_df['الأولوية'].isin(['عالي', 'عاجل'])])
                    st.markdown(f"""
                        <div style='background-color: {theme['surface_color']}; padding: 1rem; border-radius: 8px;
                             border: 1px solid {theme['warning_color']}; color: {theme['text_color']};'>
                            <p style='font-size: 1rem; margin: 0;'>القطاعات ذات الأولوية العالية</p>
                            <h2 style='margin: 0.5rem 0; color: {theme['warning_color']};'>{high_priority}</h2>
                            <p style='font-size: 0.8rem; margin: 0;'>عدد القطاعات التي تحتاج اهتمام عاجل</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    overall_trend = out_df['trend_value'].mean()
                    trend_status = "📈 تحسن" if overall_trend > 0 else "📉 انخفاض" if overall_trend < 0 else "⚖️ ثابت"
                    trend_color = theme['success_color'] if overall_trend > 0 else theme['warning_color']
                    st.markdown(f"""
                        <div style='background-color: {theme['surface_color']}; padding: 1rem; border-radius: 8px;
                             border: 1px solid {trend_color}; color: {theme['text_color']};'>
                            <p style='font-size: 1rem; margin: 0;'>الاتجاه العام</p>
                            <h2 style='margin: 0.5rem 0; color: {trend_color};'>{trend_status}</h2>
                            <p style='font-size: 0.9rem; margin: 0; color: {trend_color};'>{overall_trend:.1f}%</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Add trend visualization
                st.markdown(f"<h3 style='color: {theme['text_color']};'>📈 تحليل الاتجاهات</h3>", unsafe_allow_html=True)
                trend_fig = go.Figure()
                
                # Add compliance rate line
                trend_fig.add_trace(go.Scatter(
                    x=out_df['القطاع'],
                    y=out_df['نسبة الامتثال %'],
                    name="نسبة الامتثال",
                    line=dict(color=theme['primary_color'], width=2)
                ))
                
                # Add recent compliance points
                trend_fig.add_trace(go.Scatter(
                    x=out_df['القطاع'],
                    y=out_df['recent_compliance'],
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
        
        # Sector detail view
        with details_tab:
            if not compliance_data:
                st.info("لا توجد بيانات تفصيلية متاحة")
                return
            
            # Sector selector
            selected_sector_data = None
            selected_sector = st.selectbox(
                "اختر القطاع للتفاصيل",
                options=[d['القطاع'] for d in compliance_data]
            )
            
            for data in compliance_data:
                if data['القطاع'] == selected_sector:
                    selected_sector_data = data
                    break
            
            if selected_sector_data:
                # Create detailed view columns
                detail_col1, detail_col2 = st.columns(2)
                
                with detail_col1:
                    # Current status metrics
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
                    
                    # Priority and recommendations
                    st.markdown(f"""
                    <h3 style='color: {theme['text_color']};'>⚠️ الأولوية والتوصيات</h3>
                    
                    **مستوى الأولوية:** <span style="color: {theme['primary_color']};">{selected_sector_data['الأولوية']}</span>
                    
                    **التوصية:**
                    <span style="color: {theme['text_color']};">{selected_sector_data['التوصية']}</span>
                    """, unsafe_allow_html=True)
                
                with detail_col2:
                    # Quarterly trend analysis
                    st.markdown(f"<h3 style='color: {theme['text_color']};'>📈 تحليل الاتجاه الربع سنوي</h3>", unsafe_allow_html=True)
                    
                    if 'quarterly_trends' in selected_sector_data:
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
                    
                    # Action items and recommendations
                    st.markdown(f"<h3 style='color: {theme['text_color']};'>📋 خطة العمل المقترحة</h3>", unsafe_allow_html=True)
                    
                    if selected_sector_data['نسبة الامتثال %'] < 70:
                        st.error(f"""
                        **إجراءات عاجلة مطلوبة:**
                        1. مراجعة جميع الحالات المفتوحة وتحديد الأولويات
                        2. عقد اجتماع طارئ مع مسؤولي القطاع
                        3. وضع خطة عمل تصحيحية عاجلة
                        """)
                    elif selected_sector_data['نسبة الامtثtال %'] < 90:
                        st.warning(f"""
                        **إجراءات التحسين المطلوبة:**
                        1. تحليل أسباب الحالات المفتوحة
                        2. تحديد فرص التحسين
                        3. متابعة دورية للتقدم
                        """)
                    else:
                        st.success(f"""
                        **خطة المحافظة على الأداء:**
                        1. توثيق الممارسات الناجحة
                        2. مشاركة التجارب مع القطاعات الأخرى
                        3. مراقبة مستمرة للمؤشرات
                        """)

    def create_risk_management_activity_table(self, filtered_data):
        """Create enhanced risk management activity table"""
        theme = st.session_state.current_theme_config
        st.markdown(f"<h4 style='color: {theme['text_color']};'>⚠️ إدارة المخاطر - جدول الأنشطة</h4>", unsafe_allow_html=True)
        
        # Risk activities with metadata
        risk_activities = {
            "الأماكن المغلقة": {
                "icon": "🏗️",
                "description": "العمل في الأماكن المغلقة والضيقة",
                "typical_risks": ["نقص الأكسجين", "الغازات السامة", "صعوبة الإخلاء"]
            },
            "الارتفاعات": {
                "icon": "🏢",
                "description": "العمل على ارتفاعات عالية",
                "typical_risks": ["السقوط", "سقوط المعدات", "الظروف الجوية"]
            },
            "الحفريات": {
                "icon": "⛏️",
                "description": "أعمال الحفر والخنادق",
                "typical_risks": ["انهيار التربة", "المرافق المدفونة", "الغرق"]
            },
            "الكهرباء": {
                "icon": "⚡",
                "description": "العمل مع الأنظمة الكهربائية",
                "typical_risks": ["الصعق الكهربائي", "الحرائق", "القوس الكهربائي"]
            }
        }
        
        # Create enhanced filters with better organization
        filter_col1, filter_col2 = st.columns([2, 1])
        
        with filter_col1:
            # Main filters in a container
            with st.container():
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
                        ["الكل", "عاجل", "متوسط", "منخفض"],
                        key="risk_recommendation_filter"
                    )
                with col3:
                    year_filter_risk = st.selectbox(
                        "السنة", 
                        ["الكل"] + [str(year) for year in range(datetime.now().year, 2020, -1)],
                        key="risk_year_filter"
                    )
        
        with filter_col2:
            # Quick actions
            st.markdown(f"<h3 style='color: {theme['text_color']};'>⚡ إجراءات سريعة</h3>", unsafe_allow_html=True)
            if st.button("🔄 تحديث التقييمات", help="تحديث جميع تقييمات المخاطر"):
                st.session_state.risk_update_requested = True
        
        # Create tabs for different views
        overview_tab, details_tab, recommendations_tab = st.tabs([
            "نظرة عامة 📊",
            "تفاصيل النشاط 🔍",
            "التوصيات 💡"
        ])
        
        # Process risk data with enhanced analysis
        risk_data_list = [] # Renamed to avoid conflict with `risk_data` from filtered_data
        
        # Get risk assessment data and incident data
        risk_assessment_data = self._find_dataset_by_keywords(filtered_data, ["تقييم_المخاطر", "risk_assessment"]) # Use keywords
        incidents_data = self._find_dataset_by_keywords(filtered_data, ["الحوادث", "incidents"]) # Use keywords
        
        if not risk_assessment_data.empty:
            # Filter by year
            if year_filter_risk != "الكل":
                date_col_risk = next((c for c in risk_assessment_data.columns if "تاريخ" in str(c) or "date" in str(c).lower()), None)
                if date_col_risk:
                    risk_assessment_data[date_col_risk] = pd.to_datetime(risk_assessment_data[date_col_risk], errors='coerce')
                    risk_assessment_data = risk_assessment_data[risk_assessment_data[date_col_risk].dt.year == int(year_filter_risk)]

            for activity in risk_activities:
                # Filter data for this activity
                # Assuming 'تصنيف النشاط' or similar column exists in risk_assessment_data
                activity_col = next((c for c in risk_assessment_data.columns if 'تصنيف النشاط' in str(c) or 'activity_type' in str(c).lower()), None)
                
                if activity_col:
                    activity_data_df = risk_assessment_data[
                        risk_assessment_data[activity_col].astype(str).str.contains(activity, na=False)
                    ]
                else:
                    activity_data_df = pd.DataFrame() # No relevant column found

                if not activity_data_df.empty:
                    total_assessments = len(activity_data_df)
                    # Assuming 'التصنيف' or 'risk_level' column exists for high risk
                    risk_level_col_df = next((c for c in activity_data_df.columns if 'التصنيف' in str(c) or 'risk_level' in str(c).lower()), None)
                    
                    high_risk_count = 0
                    if risk_level_col_df:
                        high_risk_count = activity_data_df[
                            activity_data_df[risk_level_col_df].astype(str).str.contains('عالي|مرتفع|high', case=False, na=False)
                        ].sum()
                    
                    # Generate risk level
                    risk_percentage = (high_risk_count / total_assessments * 100) if total_assessments > 0 else 0
                    
                    if risk_percentage >= 70:
                        risk_level = "🔴 عالي"
                        priority = 1
                    elif risk_percentage >= 40:
                        risk_level = "🟡 متوسط"
                        priority = 2
                    else:
                        risk_level = "🟢 منخفض"
                        priority = 3
                    
                    risk_data_list.append({
                        'النشاط': activity,
                        'إجمالي التقييمات': total_assessments,
                        'المخاطر العالية': high_risk_count,
                        'مستوى المخاطر': risk_level,
                        'نسبة المخاطر %': f"{risk_percentage:.1f}%",
                        'الأولوية': priority,
                        'التوصية': 'مراجعة عاجلة' if risk_percentage >= 70 else 'مراقبة دورية'
                    })
        
        if risk_data_list:
            df_risk_activities = pd.DataFrame(risk_data_list)
            
            # Sort based on selection
            if activity_sort == "الأولوية":
                df_risk_activities = df_risk_activities.sort_values('الأولوية')
            elif activity_sort == "الاسم":
                df_risk_activities = df_risk_activities.sort_values('النشاط')
            elif activity_sort == "مستوى المخاطر":
                df_risk_activities = df_risk_activities.sort_values('نسبة المخاطر %', ascending=False)
            
            with overview_tab:
                st.dataframe(df_risk_activities.drop('الأولوية', axis=1), use_container_width=True, height=400)
                
                # Recommendation impact analysis
                st.markdown(f"<h4 style='color: {theme['text_color']};'>💡 تأثير التوصيات على الأنشطة</h4>", unsafe_allow_html=True)
                
                selected_recommendation = st.selectbox(
                    "اختر توصية لمعرفة تأثيرها",
                    ["مراجعة عاجلة", "مراقبة دورية", "تدريب إضافي", "تحديث الإجراءات"],
                    key="risk_recommendation_impact"
                )
                
                affected_activities = df_risk_activities[df_risk_activities['التوصية'].str.contains(selected_recommendation, na=False)]
                
                if not affected_activities.empty:
                    st.markdown(f"**الأنشطة المتأثرة بـ '{selected_recommendation}':**")
                    st.dataframe(affected_activities[['النشاط', 'مستوى المخاطر', 'نسبة المخاطر %']], 
                                 use_container_width=True)
                else:
                    st.info(f"لا توجد أنشطة متأثرة بـ '{selected_recommendation}'")
            
            with details_tab:
                st.markdown(f"<h4 style='color: {theme['text_color']};'>🔍 تفاصيل المخاطر والأنشطة</h4>", unsafe_allow_html=True)
                # Add detailed charts or tables for each activity
                for activity_name, activity_meta in risk_activities.items():
                    st.markdown(f"<h3 style='color: {theme['primary_color']};'>{activity_meta['icon']} {activity_name}</h3>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color: {theme['text_color']};'>**الوصف:** {activity_meta['description']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color: {theme['text_color']};'>**المخاطر النموذجية:** {', '.join(activity_meta['typical_risks'])}</p>", unsafe_allow_html=True)
                    
                    # Display relevant data for this activity
                    activity_df_filtered = risk_assessment_data[
                        risk_assessment_data[activity_col].astype(str).str.contains(activity_name, na=False)
                    ] if activity_col else pd.DataFrame()

                    if not activity_df_filtered.empty:
                        st.dataframe(activity_df_filtered, use_container_width=True)
                    else:
                        st.info(f"لا توجد بيانات تفصيلية لـ {activity_name}")

            with recommendations_tab:
                st.markdown(f"<h4 style='color: {theme['text_color']};'>💡 التوصيات وخطة العمل</h4>", unsafe_allow_html=True)
                
                # Prioritize high risks
                high_risks_df = df_risk_activities[
                    df_risk_activities['مستوى المخاطر'].str.contains('عالي|مرتفع', na=False)
                ]
                
                if not high_risks_df.empty:
                    st.warning("🚨 المخاطر ذات الأولوية العالية التي تتطلب اهتماماً فورياً:")
                    
                    for idx, risk in high_risks_df.iterrows():
                        st.markdown(f"""
                        <div style='background-color: {theme['warning_color']}15; padding: 10px; border-radius: 5px; margin: 5px 0; color: {theme['text_color']};'>
                            <h4 style='color: {theme['warning_color']}; margin: 0;'>{risk['النشاط']} - {risk['مستوى المخاطر']}</h4>
                            <p style='margin: 5px 0; color: {theme['text_color']};'>{risk['التوصية']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Add action items section
                st.subheader("📋 خطة العمل المقترحة")
                
                if activity_col: # Use activity_col from risk_assessment_data
                    for activity_type in df_risk_activities['النشاط'].unique(): # Iterate through unique activities in the processed df
                        with st.expander(f"خطة العمل - {activity_type}"):
                            # Filter original risk_assessment_data for this activity type
                            risks_for_type = risk_assessment_data[
                                risk_assessment_data[activity_col].astype(str).str.contains(activity_type, na=False)
                            ] if activity_col else pd.DataFrame()

                            if not risks_for_type.empty:
                                for _, risk in risks_for_type.iterrows():
                                    risk_level = risk.get(risk_level_col_df, "غير محدد") if risk_level_col_df else "غير محدد"
                                    risk_desc = risk.get('وصف الخطر', "لا يوجد وصف") if 'وصف الخطر' in risk.index else "لا يوجد وصف"
                                    proposed_actions = risk.get('الإجراءات المقترحة', "لم يتم تحديد إجراءات") if 'الإجراءات المقترحة' in risk.index else "لم يتم تحديد إجراءات"
                                    
                                    st.markdown(f"""
                                    * **مستوى الخطورة**: {risk_level}
                                    * **الوصف**: {risk_desc}
                                    * **الإجراءات المقترحة**: {proposed_actions}
                                    ---
                                    """, unsafe_allow_html=True)
                            else:
                                st.info(f"لا توجد تفاصيل مخاطر لـ {activity_type}")
        else:
            st.info("لا توجد بيانات إدارة مخاطر متاحة")

    def create_incidents_analysis_table(self, filtered_data):
        """Create incidents analysis table"""
        theme = st.session_state.current_theme_config
        st.markdown(f"<h4 style='color: {theme['text_color']};'>🚨 تحليل الحوادث</h4>", unsafe_allow_html=True)
        
        # Create year filter
        year_filter_incidents = st.selectbox(
            "تصفية حسب السنة", 
            ["الكل"] + [str(year) for year in range(datetime.now().year, 2020, -1)], 
            key="incidents_year_filter"
        )
        
        # Process incidents data
        incidents_data_list = [] # Renamed to avoid conflict with `incidents_data` from filtered_data
        
        # Get incidents data if available
        incidents_df = self._find_dataset_by_keywords(filtered_data, ["الحوادث", "incidents"]) # Use keywords
        
        if not incidents_df.empty:
            # Filter by year
            date_col_incidents = next((c for c in incidents_df.columns if "تاريخ" in str(c) or "date" in str(c).lower()), None)
            if date_col_incidents:
                incidents_df[date_col_incidents] = pd.to_datetime(incidents_df[date_col_incidents], errors='coerce')
                if year_filter_incidents != "الكل":
                    incidents_df = incidents_df[incidents_df[date_col_incidents].dt.year == int(year_filter_incidents)]

            # Define sectors for incidents analysis
            sector_col_incidents = next((c for c in incidents_df.columns if 'القطاع' in str(c) or 'sector' in str(c).lower()), None)
            sectors = incidents_df[sector_col_incidents].dropna().unique().tolist() if sector_col_incidents and not incidents_df[sector_col_incidents].empty else ["قطاع المشاريع", "قطاع التشغيل", "قطاع الخدمات", "قطاع التخصيص"]
            
            for sector in sectors:
                if pd.isna(sector):
                    continue
                
                # Filter incidents for this sector
                sector_incidents = incidents_df[
                    incidents_df[sector_col_incidents].astype(str).str.contains(str(sector), na=False)
                ] if sector_col_incidents else incidents_df.sample(n=min(10, len(incidents_df)))
                
                if not sector_incidents.empty:
                    total_incidents = len(sector_incidents)
                    
                    # Count recommendations (assuming there's a recommendations column)
                    recommendations_count = 0
                    closed_count = 0
                    
                    # Check for recommendations columns
                    rec_columns = [col for col in sector_incidents.columns if 'توصي' in str(col) or 'recommendation' in str(col).lower()]
                    if rec_columns:
                        recommendations_count = sector_incidents[rec_columns[0]].notna().sum()
                    else:
                        recommendations_count = total_incidents  # Assume each incident has a recommendation
                    
                    # Check for status columns
                    status_columns = [col for col in sector_incidents.columns if 'حالة' in str(col) or 'status' in str(col).lower()]
                    if status_columns:
                        closed_count = sector_incidents[status_columns[0]].str.contains('مغلق|مكتمل|closed', na=False).sum()
                    else:
                        closed_count = int(total_incidents * 0.7)  # Assume 70% are closed
                    
                    closure_percentage = (closed_count / recommendations_count * 100) if recommendations_count > 0 else 0
                    
                    incidents_data_list.append({
                        'القطاع': sector,
                        'عدد الحوادث': total_incidents,
                        'عدد التوصيات': recommendations_count,
                        'مغلق': closed_count,
                        'مفتوح': recommendations_count - closed_count,
                        'نسبة الإغلاق %': closure_percentage
                    })
            
            if incidents_data_list:
                df_incidents = pd.DataFrame(incidents_data_list)
                
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
                
                # Summary statistics
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
                
                # Incidents trend analysis
                st.markdown(f"<h3 style='color: {theme['text_color']};'>📈 تحليل اتجاه الحوادث</h3>", unsafe_allow_html=True)
                
                if not incidents_df.empty:
                    # Try to create a simple trend chart
                    fig = px.bar(
                        df_incidents, 
                        x='القطاع', 
                        y='عدد الحوادث',
                        title="توزيع الحوادث حسب القطاع",
                        color='عدد الحوادث',
                        color_continuous_scale=[theme['primary_color'], theme['warning_color']] # Dynamic color scale
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
                    st.info("لا توجد بيانات حوادث متاحة للتحليل")
            else:
                st.info("لا توجد بيانات حوادث متاحة للقطاعات المحددة")

    def create_risk_section(self, filtered_data):
        """Create enhanced risk management section"""
        theme = st.session_state.current_theme_config
        st.markdown(f"<h3 style='color: {theme['text_color']};'>⚠️ إدارة المخاطر</h3>", unsafe_allow_html=True)
        
        risk_data = self._find_dataset_by_keywords(filtered_data, ["تقييم_المخاطر", "risk_assessment"]) # Use keywords
        incidents_data = self._find_dataset_by_keywords(filtered_data, ["الحوادث", "incidents"]) # Use keywords
        
        if not risk_data.empty:
            # Create tabs for different views
            overview_tab, details_tab, recommendations_tab = st.tabs([
                "نظرة عامة 📊",
                "تفاصيل النشاط 🔍",
                "التوصيات 💡"
            ])
            
            with overview_tab:
                # KPI metrics row
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_risks = len(risk_data)
                    # Assuming 'التصنيف' or 'risk_level' column exists for high risk
                    risk_level_col_data = next((c for c in risk_data.columns if 'التصنيف' in str(c) or 'risk_level' in str(c).lower()), None)
                    high_risks = 0
                    if risk_level_col_data and not risk_data[risk_level_col_data].empty:
                        high_risks = risk_data[risk_level_col_data].astype(str).str.contains('عالي|مرتفع|high', case=False, na=False).sum()
                    
                    st.metric(
                        "إجمالي المخاطر المحددة",
                        f"{total_risks}",
                        help="العدد الإجمالي للمخاطر المحددة"
                    )
                
                with col2:
                    risk_percentage = (high_risks / total_risks * 100) if total_risks > 0 else 0
                    st.metric(
                        "نسبة المخاطر العالية",
                        f"{risk_percentage:.1f}%",
                        help="نسبة المخاطر ذات المستوى العالي"
                    )
                
                with col3:
                    if not incidents_data.empty:
                        related_incidents = len(incidents_data)
                        st.metric(
                            "الحوادث المرتبطة",
                            f"{related_incidents}",
                            help="عدد الحوادث المرتبطة بالمخاطر المحددة"
                        )
                
                # Risk distribution visualization
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"<h4 style='color: {theme['text_color']};'>📊 توزيع المخاطر</h4>", unsafe_allow_html=True)
                    
                    # Get risk level column
                    risk_level_col = next((c for c in risk_data.columns if 'مستوى' in str(c) or 'التصنيف' in str(c)), None) # Added التصنيف
                    
                    if risk_level_col and not risk_data[risk_level_col].empty:
                        risk_counts = risk_data[risk_level_col].value_counts()
                        
                        fig = px.pie(
                            values=risk_counts.values,
                            names=risk_counts.index,
                            title="توزيع مستويات المخاطر",
                            color_discrete_sequence=[theme['warning_color'], theme['secondary_color'], theme['success_color']] # Dynamic colors
                        )
                        fig.update_traces(
                            textposition='inside',
                            textinfo='percent+label',
                            hole=0.4,
                            marker=dict(line=dict(color=theme['surface_color'], width=2)) # Dynamic border color
                        )
                        fig.update_layout(
                            showlegend=True,
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                            paper_bgcolor=theme['surface_color'], # Dynamic background
                            plot_bgcolor=theme['background_color'], # Dynamic plot background
                            font_color=theme['text_color'] # Dynamic font color
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("لم يتم العثور على عمود مستوى المخاطر في البيانات أو أنه فارغ")
                
                with col2:
                    st.markdown(f"<h4 style='color: {theme['text_color']};'>📈 اتجاه المخاطر حسب القطاع</h4>", unsafe_allow_html=True)
                    
                    # Get sector column
                    sector_col = next((c for c in risk_data.columns if 'قطاع' in str(c) or 'الإدارة' in str(c)), None) # Added الإدارة
                    
                    if sector_col and not risk_data[sector_col].empty:
                        # Get risk counts by sector
                        sector_risks = risk_data.groupby(sector_col).size().reset_index(name='count')
                        sector_risks = sector_risks.sort_values('count', ascending=True)  # Sort for better visualization
                        
                        fig = px.bar(
                            sector_risks,
                            x='count',
                            y=sector_col,
                            orientation='h',  # Horizontal bars for better label visibility
                            title="توزيع المخاطر حسب القطاع",
                            labels={
                                'count': 'عدد المخاطر',
                                sector_col: 'القطاع'
                            },
                            color='count',
                            color_continuous_scale=[theme['primary_color'], theme['warning_color']] # Dynamic colors
                        )
                        fig.update_layout(
                            height=400,
                            xaxis_title="عدد المخاطر",
                            yaxis_title="القطاع",
                            showlegend=False,
                            paper_bgcolor=theme['surface_color'], # Dynamic background
                            plot_bgcolor=theme['background_color'], # Dynamic plot background
                            font_color=theme['text_color'] # Dynamic font color
                        )
                        fig.update_traces(
                            texttemplate='%{x}',
                            textposition='outside'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("لم يتم العثور على عمود القطاع في البيانات أو أنه فارغ")
            
            # The 'details_tab' and 'recommendations_tab' implementations are assumed to be correct
            # and would also need to use theme variables for any hardcoded styles.
            # I've added a basic dynamic color for the warning box in recommendations_tab.
            with details_tab:
                st.markdown(f"<h4 style='color: {theme['text_color']};'>🔍 تفاصيل المخاطر</h4>", unsafe_allow_html=True)
                
                # Initialize variables
                selected_risk_level = []
                selected_risk_type = []
                risk_level_col = None
                risk_type_col = None
                
                # Add filters
                col1, col2 = st.columns(2)
                with col1:
                    # Get risk level column
                    risk_level_col = next((c for c in risk_data.columns if 'مستوى' in str(c) or 'التصنيف' in str(c)), None)
                    if risk_level_col and not risk_data[risk_level_col].empty:
                        selected_risk_level = st.multiselect(
                            "تصفية حسب مستوى المخاطر",
                            options=sorted(risk_data[risk_level_col].unique()),
                            key="risk_level_filter"
                        )
                
                with col2:
                    # Get risk type column
                    risk_type_col = next((c for c in risk_data.columns if 'نوع' in str(c) or 'تصنيف النشاط' in str(c)), None) # Added تصنيف النشاط
                    if risk_type_col and not risk_data[risk_type_col].empty:
                        selected_risk_type = st.multiselect(
                            "تصفية حسب نوع الخطر",
                            options=sorted(risk_data[risk_type_col].unique()),
                            key="risk_type_filter"
                        )
                
                # Filter data based on selections
                filtered_risk_data = risk_data.copy()
                if selected_risk_level and risk_level_col:
                    filtered_risk_data = filtered_risk_data[
                        filtered_risk_data[risk_level_col].isin(selected_risk_level)
                    ]
                if selected_risk_type and risk_type_col:
                    filtered_risk_data = filtered_risk_data[
                        filtered_risk_data[risk_type_col].isin(selected_risk_type)
                    ]
                
                # Display filtered data with formatting
                def highlight_high_risk(val):
                    # Use theme colors for highlighting
                    if 'عالي' in str(val) or 'مرتفع' in str(val) or 'high' in str(val).lower():
                        return f'background-color: {theme["warning_color"]}30; color: {theme["warning_color"]};'
                    return ''
                
                if risk_level_col:
                    styled_df = filtered_risk_data.style.applymap(
                        highlight_high_risk,
                        subset=[risk_level_col]
                    )
                else:
                    styled_df = filtered_risk_data.style
                
                st.dataframe(
                    styled_df,
                    height=400,
                    use_container_width=True
                )
            
            with recommendations_tab:
                st.markdown(f"<h4 style='color: {theme['text_color']};'>💡 التوصيات وخطة العمل</h4>", unsafe_allow_html=True)
                
                # Prioritize high risks
                high_risks_df = filtered_risk_data[
                    filtered_risk_data.astype(str).apply(
                        lambda x: x.str.contains('عالي|مرتفع|high', na=False)
                    ).any(axis=1)
                ]
                
                if not high_risks_df.empty:
                    st.warning("🚨 المخاطر ذات الأولوية العالية التي تتطلب اهتماماً فورياً:")
                    
                    for idx, risk in high_risks_df.iterrows():
                        risk_type = risk.get(risk_type_col, "غير محدد") if risk_type_col else "غير محدد"
                        # Assuming 'وصف الخطر' column exists or similar
                        risk_desc = risk.get('وصف الخطر', "لا يوجد وصف") if 'وصف الخطر' in risk.index else "لا يوجد وصف"
                        
                        st.markdown(f"""
                        <div style='background-color: {theme['warning_color']}15; padding: 10px; border-radius: 5px; margin: 5px 0;'>
                            <h4 style='color: {theme['warning_color']}; margin: 0;'>{risk_type}</h4>
                            <p style='margin: 5px 0; color: {theme['text_color']};'>{risk_desc}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Add action items section
                st.subheader("📋 خطة العمل المقترحة")
                
                if risk_type_col: # Ensure risk_type_col is identified
                    for activity_type in df_risk_activities['النشاط'].unique(): # Iterate through unique activities in the processed df
                        with st.expander(f"خطة العمل - {activity_type}"):
                            # Filter original risk_assessment_data for this activity type
                            risks_for_type = risk_assessment_data[
                                risk_assessment_data[activity_col].astype(str).str.contains(activity_type, na=False)
                            ] if activity_col else pd.DataFrame()

                            if not risks_for_type.empty:
                                for _, risk in risks_for_type.iterrows():
                                    risk_level = risk.get(risk_level_col_df, "غير محدد") if risk_level_col_df else "غير محدد"
                                    risk_desc = risk.get('وصف الخطر', "لا يوجد وصف") if 'وصف الخطر' in risk.index else "لا يوجد وصف"
                                    proposed_actions = risk.get('الإجراءات المقترحة', "لم يتم تحديد إجراءات") if 'الإجراءات المقترحة' in risk.index else "لم يتم تحديد إجراءات"
                                    
                                    st.markdown(f"""
                                    * **مستوى الخطورة**: {risk_level}
                                    * **الوصف**: {risk_desc}
                                    * **الإجراءات المقترحة**: {proposed_actions}
                                    ---
                                    """, unsafe_allow_html=True)
                            else:
                                st.info(f"لا توجد تفاصيل مخاطر لـ {activity_type}")
        else:
            st.info("لا توجد بيانات إدارة مخاطر متاحة")

    def create_performance_section(self, filtered_data):
        """Create performance section with modern, clean visualizations"""
        theme = st.session_state.current_theme_config
        
        def create_clean_gauge(value, title, color):
            """Helper function to create a clean, modern gauge with visible number"""
            fig = go.Figure()
            
            # Add the gauge
            fig.add_trace(go.Indicator(
                mode="gauge",  # Only gauge, no number
                value=value,
                domain={'x': [0.1, 0.9], 'y': [0.15, 0.85]},
                gauge={
                    'axis': {
                        'range': [0, 100],
                        'tickwidth': 2,
                        'tickcolor': color,
                        'tickfont': {'size': 14, 'color': theme['text_color']}, # Dynamic tick font color
                        'tickmode': 'array',
                        'ticktext': ['0', '25', '50', '75', '100'],
                        'tickvals': [0, 25, 50, 75, 100]
                    },
                    'bar': {'color': color, 'thickness': 0.6},
                    'bgcolor': theme['surface_color'], # Dynamic background
                    'borderwidth': 2,
                    'bordercolor': color,
                }
            ))
            
            # Add central number display
            fig.add_annotation(
                text=f"<b>{value:.1f}%</b>",
                x=0.5,
                y=0.5,
                font={'size': 48, 'color': color, 'family': 'Arial Black'},
                showarrow=False
            )
            
            # Add title
            fig.add_annotation(
                text=title,
                x=0.5,
                y=0.95,
                font={'size': 24, 'color': color},
                showarrow=False
            )
            
            # Update layout
            fig.update_layout(
                height=300,
                margin=dict(l=30, r=30, t=30, b=30),
                paper_bgcolor=theme['surface_color'], # Dynamic background
                plot_bgcolor=theme['background_color'], # Dynamic plot background
                showlegend=False,
                font_color=theme['text_color'] # Dynamic font color
            )
            
            return fig
        st.markdown(f"<h3 style='color: {theme['text_color']};'>🎯 مؤشرات الأداء</h3>", unsafe_allow_html=True)
        
        # Performance metrics
        col1, col2, col3 = st.columns(3)
        
        # Calculate metrics from actual data
        inspection_data = self._find_dataset_by_keywords(filtered_data, ["التفتيش", "inspection"])
        incidents_data = self._find_dataset_by_keywords(filtered_data, ["الحوادث", "incidents"])
        safety_data = self._find_dataset_by_keywords(filtered_data, ["أنظمة_السلامة_والإطفاء", "safety_systems"])
        
        with col1:
            st.markdown(f"<h4 style='color: {theme['text_color']};'>📊 معدل الامتثال</h4>", unsafe_allow_html=True)
            if not inspection_data.empty:
                # Calculate compliance rate from inspection data
                total_inspections = len(inspection_data)
                status_col = next((c for c in inspection_data.columns if 'حالة' in str(c)), None)
                if status_col:
                    completed_inspections = inspection_data[status_col].str.contains('مكتمل|مغلق|completed|closed', case=False, na=False).sum()
                    compliance_rate = (completed_inspections / total_inspections * 100) if total_inspections > 0 else 0
                else:
                    compliance_rate = 75  # Default value if status column not found
                
                fig = create_clean_gauge(compliance_rate, "معدل الامتثال", theme['primary_color'])
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("لا تتوفر بيانات التفتيش")
        
        with col2:
            st.markdown(f"<h4 style='color: {theme['text_color']};'>⚡ الاستجابة السريعة</h4>", unsafe_allow_html=True)
            if not incidents_data.empty:
                # Calculate average response time from incidents data
                date_cols = [c for c in incidents_data.columns if 'تاريخ' in str(c)]
                avg_response_time = 2.5 # Default value
                if len(date_cols) >= 2:  # If we have both start and end dates
                    try:
                        # Assuming the first date column is start_date and second is end_date
                        incidents_data['start_date'] = pd.to_datetime(incidents_data[date_cols[0]], errors='coerce')
                        incidents_data['end_date'] = pd.to_datetime(incidents_data[date_cols[1]], errors='coerce')
                        avg_response_time = (incidents_data['end_date'] - incidents_data['start_date']).mean().days
                    except:
                        pass # Use default if calculation fails
                
                fig = go.Figure()
                
                # Create a gauge for response time (0-5 days scale)
                normalized_value = min(100, (avg_response_time / 5) * 100)  # Convert days to percentage (5 days = 100%)
                
                # Add the gauge
                fig.add_trace(go.Indicator(
                    mode="gauge",
                    value=normalized_value,
                    domain={'x': [0.1, 0.9], 'y': [0.15, 0.85]},
                    gauge={
                        'axis': {
                            'range': [0, 100],
                            'tickwidth': 2,
                            'tickcolor': theme['secondary_color'],
                            'tickfont': {'size': 14, 'color': theme['text_color']}, # Dynamic tick font color
                            'tickmode': 'array',
                            'ticktext': ['0', '1', '2', '3', '4', '5'],
                            'tickvals': [0, 20, 40, 60, 80, 100]
                        },
                        'bar': {'color': theme['secondary_color'], 'thickness': 0.6},
                        'bgcolor': theme['surface_color'], # Dynamic background
                        'borderwidth': 2,
                        'bordercolor': theme['secondary_color'],
                    }
                ))
                
                # Add central number display
                fig.add_annotation(
                    text=f"<b>{avg_response_time:.1f}</b>",
                    x=0.5,
                    y=0.5,
                    font={'size': 48, 'color': theme['secondary_color'], 'family': 'Arial Black'},
                    showarrow=False
                )
                
                # Add "days" label below the number
                fig.add_annotation(
                    text="يوم",
                    x=0.5,
                    y=0.4,
                    font={'size': 20, 'color': theme['secondary_color']},
                    showarrow=False
                )
                
                # Add title
                fig.add_annotation(
                    text="متوسط وقت الاستجابة",
                    x=0.5,
                    y=0.95,
                    font={'size': 24, 'color': theme['secondary_color']},
                    showarrow=False
                )
                
                # Update layout
                fig.update_layout(
                    height=300,
                    margin=dict(l=30, r=30, t=30, b=30),
                    paper_bgcolor=theme['surface_color'], # Dynamic background
                    plot_bgcolor=theme['background_color'], # Dynamic plot background
                    showlegend=False,
                    font_color=theme['text_color'] # Dynamic font color
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("لا تتوفر بيانات الحوادث")
        
        with col3:
            st.markdown(f"<h4 style='color: {theme['text_color']};'>🎯 معدل الإنجاز</h4>", unsafe_allow_html=True)
            if not safety_data.empty:
                # Calculate completion rate from safety systems data
                total_items = len(safety_data)
                status_col = next((c for c in safety_data.columns if 'حالة' in str(c)), None)
                if status_col:
                    completed_items = safety_data[status_col].str.contains('مكتمل|منجز|completed', case=False, na=False).sum()
                    completion_rate = (completed_items / total_items * 100) if total_items > 0 else 0
                else:
                    completion_rate = 85  # Default value if status column not found
                
                fig = create_clean_gauge(completion_rate, "معدل الإنجاز", theme['success_color'])
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("لا تتوفر بيانات أنظمة السلامة")

    def create_quality_report_page(self, quality_report):
        """Create comprehensive quality report page"""
        theme = st.session_state.current_theme_config
        st.header(f"<h2 style='color: {theme['text_color']};'>📋 تقرير جودة البيانات الشامل</h2>", unsafe_allow_html=True)
        
        if quality_report:
            # Overall summary
            total_records = sum([report.get('total_rows', 0) for report in quality_report.values()])
            total_missing = sum([report.get('missing_values', 0) for report in quality_report.values()])
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("إجمالي السجلات", f"{total_records:,}")
            
            with col2:
                st.metric("مجموعات البيانات", len(quality_report))
            
            with col3:
                missing_percentage = (total_missing / total_records * 100) if total_records > 0 else 0
                st.metric("البيانات المفقودة", f"{missing_percentage:.1f}%")
            
            with col4:
                avg_quality = 100 - missing_percentage
                st.metric("متوسط الجودة", f"{avg_quality:.1f}%")
            
            # Detailed reports for each dataset
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
                            'البيانات المفقودة': report.get('missing_values', 0),
                            'الصفوف المكررة': report.get('duplicate_rows', 0),
                            'نسبة البيانات المفقودة': f"{report.get('missing_data_percentage', 0):.1f}%"
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
        # Set current theme config in session state for global access
        st.session_state.current_theme_config = self.theme_manager.get_current_theme()
        theme = st.session_state.current_theme_config # Get the theme config after it's set
        
        # Apply global theme CSS for consistent styles
        theme_manager.apply_theme_css()
        
        # Load data if not already loaded
        if not st.session_state.data_loaded:
            with st.spinner("جاري تحميل ومعالجة البيانات..."):
                try:
                    processor, unified_data, kpi_data, quality_report = self.load_and_process_data()
                    
                    st.session_state.processor = processor
                    st.session_state.unified_data = unified_data
                    st.session_state.kpi_data = kpi_data
                    st.session_state.quality_report = quality_report
                    st.session_state.data_loaded = True
                    
                except Exception as e:
                    advanced_features.add_notification(f"خطأ في تحميل البيانات: {str(e)}", "error")
                    st.session_state.processor = None
                    st.session_state.unified_data = {}
                    st.session_state.kpi_data = {}
                    st.session_state.quality_report = {}
                    st.session_state.data_loaded = True # Set to True to avoid infinite loading loop on error
        
        # Get data from session state
        unified_data = st.session_state.unified_data
        kpi_data = st.session_state.kpi_data
        quality_report = st.session_state.quality_report
        
        # Create enhanced sidebar with navigation first
        filters, selected_page = self.create_enhanced_sidebar(unified_data)
        
        # Show help if requested
        if st.session_state.get('show_help', False):
            return
        
        # Display selected page
        if selected_page == "الرئيسية المتقدمة":
            self.create_ultimate_main_dashboard(unified_data, kpi_data, filters)
        
        elif selected_page == "التحليلات الذكية":
            self.create_analytics_section(unified_data)
        
        elif selected_page == "مركز التصدير":
            advanced_features.create_export_center(unified_data, kpi_data)
        
        elif selected_page == "رفع البيانات":
            advanced_features.create_manual_upload_section()
        
        elif selected_page == "تشغيل مساعد الذكاء الاصطناعي":
            try:
                # Prepare unified data for chatbot
                chatbot_data = {}
                for name, df in unified_data.items():
                    if isinstance(df, pd.DataFrame) and not df.empty:
                        # Convert any date columns to datetime
                        for col in df.columns:
                            if any(x in str(col).lower() for x in ['تاريخ', 'date']):
                                try:
                                    df[col] = pd.to_datetime(df[col], errors='coerce')
                                except:
                                    pass
                        # Add to chatbot data
                        chatbot_data[name] = df
                
                # Prepare KPI data
                chatbot_kpis = {
                    'total_records': sum(len(df) for df in chatbot_data.values()),
                    'departments': {},
                    'status_counts': {'open': 0, 'closed': 0},
                    'risk_levels': {}
                }
                
                # Process KPIs
                for df in chatbot_data.values():
                    # Get department stats
                    dept_col = next((col for col in df.columns 
                                     if any(x in str(col).lower() for x in ['قطاع', 'إدارة', 'department'])), None)
                    if dept_col:
                        dept_counts = df[dept_col].value_counts()
                        for dept, count in dept_counts.items():
                            if dept in chatbot_kpis['departments']:
                                chatbot_kpis['departments'][dept] += count
                            else:
                                chatbot_kpis['departments'][dept] = count
                    
                    # Get status counts
                    status_col = next((col for col in df.columns 
                                       if any(x in str(col).lower() for x in ['حالة', 'status'])), None)
                    if status_col:
                        closed = df[status_col].str.contains('مغلق|closed', case=False, na=False).sum()
                        chatbot_kpis['status_counts']['closed'] += closed
                        chatbot_kpis['status_counts']['open'] += len(df) - closed
                    
                    # Get risk levels
                    risk_col = next((col for col in df.columns 
                                     if any(x in str(col).lower() for x in ['مخاطر', 'risk'])), None)
                    if risk_col:
                        risk_counts = df[risk_col].value_counts()
                        for risk, count in risk_counts.items():
                            if risk in chatbot_kpis['risk_levels']:
                                chatbot_kpis['risk_levels'][risk] += count
                            else:
                                chatbot_kpis['risk_levels'][risk] = count
                
                create_chatbot_interface(chatbot_data, chatbot_kpis)
            except Exception as e:
                st.error(f"خطأ في المساعد الذكي: {str(e)}")
                st.info("المساعد الذكي غير متاح حالياً")
        
        elif selected_page == "المراقبة المباشرة":
            advanced_features.create_real_time_monitoring(unified_data)
        
        elif selected_page == "تقرير الجودة":
            self.create_quality_report_page(quality_report)
        
        # Footer
        current_theme = theme_manager.get_current_theme()
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
