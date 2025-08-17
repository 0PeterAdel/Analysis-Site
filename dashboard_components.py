"""
Advanced Dashboard Components
Comprehensive visualization components for the Safety & Compliance Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np # Keep numpy if used for linspace in gauge helper or similar
import warnings
warnings.filterwarnings('ignore')

# Import COLORS from settings for consistency
from src.config.settings import COLORS

class DashboardComponents:
    """
    Advanced dashboard components for safety and compliance visualization.
    These methods focus purely on rendering charts and tables using pre-processed data.
    They receive DataFrames and theme configurations as inputs.
    """
    
    def __init__(self):
        # Use COLORS from settings for consistency
        self.color_palette = COLORS 
        
    def create_kpi_cards(self, kpi_data: dict, theme: dict):
        """
        Creates KPI cards based on aggregated KPI data.
        Assumes kpi_data is a dictionary containing overall aggregated KPIs.
        """
        if not kpi_data:
            st.info("لا توجد مؤشرات أداء متاحة لعرض بطاقات KPI.")
            return

        # Aggregate KPIs from the kpi_data dictionary
        total_records = sum([data.get('total_records', 0) for data in kpi_data.values()])
        
        open_count = 0
        closed_count = 0
        for data in kpi_data.values():
            status_dist = data.get('status_distribution', {})
            open_count += status_dist.get('مفتوح', 0)
            closed_count += status_dist.get('مغلق', 0)

        datasets_count = len(kpi_data)
        closure_rate = (closed_count / (open_count + closed_count) * 100) if (open_count + closed_count) > 0 else 0

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

        # Render up to 4 cards per row
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
        
    def create_compliance_pie_chart(self, compliance_data_df: pd.DataFrame, theme: dict):
        """
        Creates a pie chart showing compliance status distribution.
        Assumes compliance_data_df has 'status' and 'count' columns.
        """
        if compliance_data_df.empty:
            st.info("لا توجد بيانات امتثال متاحة للرسم البياني.")
            return
            
        fig = px.pie(
            compliance_data_df, 
            values='count', 
            names='status',
            title="حالة الامتثال",
            color_discrete_map={
                'مغلق': theme['success_color'],
                'مفتوح': theme['warning_color']
            }
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            paper_bgcolor=theme['surface_color'],
            plot_bgcolor=theme['background_color'],
            font_color=theme['text_color']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def create_department_compliance_bar_chart(self, dept_performance_df: pd.DataFrame, theme: dict):
        """
        Creates a bar chart showing compliance rate by department.
        Assumes dept_performance_df has 'department' and 'compliance_rate' columns.
        """
        if dept_performance_df.empty:
            st.info("لا توجد بيانات أداء القطاعات متاحة للرسم البياني.")
            return
            
        fig = px.bar(
            dept_performance_df,
            x='department',
            y='compliance_rate',
            title="معدل الامتثال حسب القطاع",
            color='compliance_rate',
            color_continuous_scale=[theme['danger_color'], theme['warning_color'], theme['success_color']] # Red-Yellow-Green scale
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            paper_bgcolor=theme['surface_color'],
            plot_bgcolor=theme['background_color'],
            font_color=theme['text_color']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def create_risk_level_bar_chart(self, risk_levels_df: pd.DataFrame, theme: dict):
        """
        Creates a bar chart showing distribution of risk levels.
        Assumes risk_levels_df has 'risk_level' and 'count' columns.
        """
        if risk_levels_df.empty:
            st.info("لا توجد بيانات مستويات المخاطر متاحة للرسم البياني.")
            return
            
        fig = px.bar(
            risk_levels_df,
            x='risk_level',
            y='count',
            title="توزيع مستويات المخاطر",
            color='risk_level',
            color_discrete_map={
                'عالي': theme['danger_color'],
                'متوسط': theme['warning_color'],
                'منخفض': theme['success_color']
            },
            category_orders={"risk_level": ["عالي", "متوسط", "منخفض"]} # Ensure consistent order
        )
        fig.update_layout(
            paper_bgcolor=theme['surface_color'],
            plot_bgcolor=theme['background_color'],
            font_color=theme['text_color']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def create_risk_trend_line_chart(self, risk_trend_df: pd.DataFrame, theme: dict):
        """
        Creates a line chart showing risk trend over time.
        Assumes risk_trend_df has 'date', 'risk_score', and 'risk_level' columns.
        """
        if risk_trend_df.empty:
            st.info("لا توجد بيانات اتجاه المخاطر متاحة للرسم البياني.")
            return
            
        fig = px.line(
            risk_trend_df,
            x='date',
            y='risk_score',
            title="اتجاه المخاطر عبر الزمن",
            color='risk_level', # Color by categorized risk level
            color_discrete_map={
                'عالي': theme['danger_color'],
                'متوسط': theme['warning_color'],
                'منخفض': theme['success_color']
            },
            markers=True
        )
        fig.update_layout(
            paper_bgcolor=theme['surface_color'],
            plot_bgcolor=theme['background_color'],
            font_color=theme['text_color']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def create_activity_heatmap(self, heatmap_data_df: pd.DataFrame, theme: dict):
        """
        Creates a heatmap showing activity density by department and type.
        Assumes heatmap_data_df is a pivot table (departments as index, activities as columns).
        """
        if heatmap_data_df.empty:
            st.info("لا توجد بيانات كافية لإنشاء الخريطة الحرارية.")
            return
            
        fig = px.imshow(
            heatmap_data_df,
            labels=dict(x="النشاط", y="القطاع", color="العدد"),
            x=heatmap_data_df.columns.tolist(),
            y=heatmap_data_df.index.tolist(),
            title="كثافة الأنشطة حسب القطاع والنوع",
            color_continuous_scale='Reds', # Use a sequential color scale for density
            aspect='auto'
        )
        fig.update_layout(
            height=500,
            paper_bgcolor=theme['background_color'],
            plot_bgcolor=theme['background_color'],
            font_color=theme['text_color']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def create_time_series_line_chart(self, time_series_df: pd.DataFrame, title: str, color: str, theme: dict):
        """
        Creates a generic line chart for time series data.
        Assumes time_series_df has 'date' and 'count' columns.
        """
        if time_series_df.empty:
            st.info(f"لا توجد بيانات متاحة لـ {title.replace('اتجاه', '')} للرسم البياني.")
            return
            
        fig = px.line(
            time_series_df,
            x='date',
            y='count',
            title=title,
            markers=True,
            color_discrete_sequence=[color]
        )
        fig.update_layout(
            paper_bgcolor=theme['surface_color'],
            plot_bgcolor=theme['background_color'],
            font_color=theme['text_color']
        )
        st.plotly_chart(fig, use_container_width=True)

    def display_detailed_dataframe(self, df: pd.DataFrame, title: str, theme: dict, download_label: str = "تحميل البيانات"):
        """
        Displays a detailed DataFrame with a title and download button.
        """
        st.subheader(title)
        if df.empty:
            st.info(f"لا توجد بيانات متاحة لـ {title}.")
            return

        # Display summary statistics (can be moved to analyzer if needed for reuse)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("إجمالي السجلات", len(df))
        with col2:
            # Assuming 'الحالة' column exists for open/closed counts
            open_count = df['الحالة'].astype(str).str.contains('مفتوح', case=False, na=False).sum() if 'الحالة' in df.columns else 0
            st.metric("السجلات المفتوحة", open_count)
        with col3:
            closed_count = df['الحالة'].astype(str).str.contains('مغلق', case=False, na=False).sum() if 'الحالة' in df.columns else 0
            st.metric("السجلات المغلقة", closed_count)
        
        st.dataframe(
            df,
            use_container_width=True,
            height=400
        )
        
        csv = df.to_csv(index=False, encoding='utf-8-sig') # Ensure proper Arabic encoding
        st.download_button(
            label=download_label,
            data=csv,
            file_name=f"{title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
