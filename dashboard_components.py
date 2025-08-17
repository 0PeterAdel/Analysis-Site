"""
Advanced Dashboard Components
Comprehensive visualization components for the Safety & Compliance Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class DashboardComponents:
    """Advanced dashboard components for safety and compliance visualization"""
    
    def __init__(self):
        self.color_palette = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#9467bd',
            'light': '#f8f9fa',
            'dark': '#343a40'
        }
        
    def create_kpi_cards(self, kpi_data):
        """Create KPI cards matching the Power BI layout"""
        if not kpi_data:
            st.warning("No KPI data available")
            return
        
        # Main KPI row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_inspections = sum([data.get('total_records', 0) for key, data in kpi_data.items() if 'inspection' in key.lower()])
            st.metric(
                label="إجمالي التفتيشات",
                value=f"{total_inspections:,}",
                delta="12% من الشهر الماضي"
            )
        
        with col2:
            total_incidents = sum([data.get('total_records', 0) for key, data in kpi_data.items() if 'incident' in key.lower()])
            st.metric(
                label="إجمالي الحوادث",
                value=f"{total_incidents:,}",
                delta="-5% من الشهر الماضي"
            )
        
        with col3:
            total_risks = sum([data.get('total_records', 0) for key, data in kpi_data.items() if 'risk' in key.lower()])
            st.metric(
                label="تقييمات المخاطر",
                value=f"{total_risks:,}",
                delta="8% من الشهر الماضي"
            )
        
        with col4:
            total_audits = sum([data.get('total_records', 0) for key, data in kpi_data.items() if 'contractor' in key.lower()])
            st.metric(
                label="تدقيق المقاولين",
                value=f"{total_audits:,}",
                delta="15% من الشهر الماضي"
            )
    
    def create_compliance_overview(self, unified_data):
        """Create compliance overview charts"""
        st.subheader("نظرة عامة على الامتثال")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Compliance status pie chart
            compliance_data = self._get_compliance_data(unified_data)
            if not compliance_data.empty:
                fig = px.pie(
                    compliance_data, 
                    values='count', 
                    names='status',
                    title="حالة الامتثال",
                    color_discrete_map={
                        'مغلق': self.color_palette['success'],
                        'مفتوح': self.color_palette['warning']
                    }
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Department performance
            dept_data = self._get_department_performance(unified_data)
            if not dept_data.empty:
                fig = px.bar(
                    dept_data,
                    x='department',
                    y='compliance_rate',
                    title="معدل الامتثال حسب القطاع",
                    color='compliance_rate',
                    color_continuous_scale='RdYlGn'
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
    
    def create_risk_management_section(self, unified_data):
        """Create risk management visualization section"""
        st.subheader("إدارة المخاطر")
        
        if 'risk_assessments' not in unified_data or unified_data['risk_assessments'].empty:
            st.warning("لا توجد بيانات تقييم المخاطر متاحة")
            return
        
        risk_data = unified_data['risk_assessments']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk level distribution
            risk_levels = self._get_risk_levels(risk_data)
            if not risk_levels.empty:
                fig = px.bar(
                    risk_levels,
                    x='risk_level',
                    y='count',
                    title="توزيع مستويات المخاطر",
                    color='risk_level',
                    color_discrete_map={
                        'عالي': self.color_palette['warning'],
                        'متوسط': '#ffa500',
                        'منخفض': self.color_palette['success']
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Risk trend over time
            risk_trend = self._get_risk_trend(risk_data)
            if not risk_trend.empty:
                fig = px.line(
                    risk_trend,
                    x='date',
                    y='risk_score',
                    title="اتجاه المخاطر عبر الزمن",
                    color='risk_level'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def create_activity_heatmap(self, unified_data):
        """Create activity heatmap"""
        st.subheader("خريطة حرارية للأنشطة")
        
        heatmap_data = self._prepare_heatmap_data(unified_data)
        if heatmap_data.empty:
            st.warning("لا توجد بيانات كافية لإنشاء الخريطة الحرارية")
            return
        
        fig = px.imshow(
            heatmap_data,
            title="كثافة الأنشطة حسب القطاع والنوع",
            color_continuous_scale='Reds',
            aspect='auto'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    def create_time_series_analysis(self, unified_data):
        """Create comprehensive time series analysis"""
        st.subheader("تحليل الاتجاهات الزمنية")
        
        # Create tabs for different time series
        tab1, tab2, tab3 = st.tabs(["الملاحظات", "الحوادث", "التدقيق"])
        
        with tab1:
            self._create_observations_trend(unified_data)
        
        with tab2:
            self._create_incidents_trend(unified_data)
        
        with tab3:
            self._create_audit_trend(unified_data)
    
    def create_interactive_filters(self, unified_data):
        """Create interactive filters for the dashboard"""
        st.sidebar.header("المرشحات التفاعلية")
        
        filters = {}
        
        # Date range filter
        date_range = self._get_overall_date_range(unified_data)
        if date_range:
            filters['date_range'] = st.sidebar.date_input(
                "نطاق التاريخ",
                value=(date_range['min_date'], date_range['max_date']),
                min_value=date_range['min_date'],
                max_value=date_range['max_date']
            )
        
        # Department filter
        departments = self._get_all_departments(unified_data)
        if departments:
            filters['departments'] = st.sidebar.multiselect(
                "القطاعات",
                options=departments,
                default=departments
            )
        
        # Status filter
        statuses = self._get_all_statuses(unified_data)
        if statuses:
            filters['statuses'] = st.sidebar.multiselect(
                "الحالة",
                options=statuses,
                default=statuses
            )
        
        # Activity type filter
        activities = self._get_all_activities(unified_data)
        if activities:
            filters['activities'] = st.sidebar.multiselect(
                "نوع النشاط",
                options=activities,
                default=activities[:10] if len(activities) > 10 else activities
            )
        
        return filters
    
    def create_detailed_tables(self, unified_data, filters=None):
        """Create detailed data tables with filtering"""
        st.subheader("الجداول التفصيلية")
        
        # Create tabs for different data types
        tabs = st.tabs(list(unified_data.keys()))
        
        for i, (data_type, df) in enumerate(unified_data.items()):
            with tabs[i]:
                if df.empty:
                    st.warning(f"لا توجد بيانات متاحة لـ {data_type}")
                    continue
                
                # Apply filters if provided
                filtered_df = self._apply_filters(df, filters) if filters else df
                
                # Display summary statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("إجمالي السجلات", len(filtered_df))
                with col2:
                    open_count = len(filtered_df[filtered_df.apply(lambda row: any('مفتوح' in str(val) for val in row), axis=1)])
                    st.metric("السجلات المفتوحة", open_count)
                with col3:
                    closed_count = len(filtered_df[filtered_df.apply(lambda row: any('مغلق' in str(val) for val in row), axis=1)])
                    st.metric("السجلات المغلقة", closed_count)
                
                # Display the table
                st.dataframe(
                    filtered_df,
                    use_container_width=True,
                    height=400
                )
                
                # Download button
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label=f"تحميل بيانات {data_type}",
                    data=csv,
                    file_name=f"{data_type}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    def _get_compliance_data(self, unified_data):
        """Extract compliance data from unified datasets"""
        compliance_counts = {'مغلق': 0, 'مفتوح': 0}
        
        for data_type, df in unified_data.items():
            if df.empty:
                continue
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['حالة', 'status']):
                    status_counts = df[col].value_counts()
                    for status, count in status_counts.items():
                        if 'مغلق' in str(status):
                            compliance_counts['مغلق'] += count
                        elif 'مفتوح' in str(status):
                            compliance_counts['مفتوح'] += count
        
        return pd.DataFrame([
            {'status': 'مغلق', 'count': compliance_counts['مغلق']},
            {'status': 'مفتوح', 'count': compliance_counts['مفتوح']}
        ])
    
    def _get_department_performance(self, unified_data):
        """Calculate department performance metrics"""
        dept_performance = {}
        
        for data_type, df in unified_data.items():
            if df.empty:
                continue
            
            dept_col = None
            status_col = None
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['إدارة', 'قطاع', 'department']):
                    dept_col = col
                elif any(keyword in col.lower() for keyword in ['حالة', 'status']):
                    status_col = col
            
            if dept_col and status_col:
                dept_status = df.groupby(dept_col)[status_col].value_counts().unstack(fill_value=0)
                for dept in dept_status.index:
                    closed = dept_status.loc[dept].get('مغلق', 0)
                    total = dept_status.loc[dept].sum()
                    compliance_rate = (closed / total * 100) if total > 0 else 0
                    
                    if dept not in dept_performance:
                        dept_performance[dept] = []
                    dept_performance[dept].append(compliance_rate)
        
        # Calculate average compliance rate per department
        result = []
        for dept, rates in dept_performance.items():
            avg_rate = np.mean(rates) if rates else 0
            result.append({'department': dept, 'compliance_rate': avg_rate})
        
        return pd.DataFrame(result)
    
    def _get_risk_levels(self, risk_data):
        """Extract risk level distribution"""
        risk_levels = {'عالي': 0, 'متوسط': 0, 'منخفض': 0}
        
        for col in risk_data.columns:
            if any(keyword in col.lower() for keyword in ['تصنيف', 'مخاطر', 'risk']):
                level_counts = risk_data[col].value_counts()
                for level, count in level_counts.items():
                    level_str = str(level).lower()
                    if 'عالي' in level_str or 'high' in level_str:
                        risk_levels['عالي'] += count
                    elif 'متوسط' in level_str or 'medium' in level_str:
                        risk_levels['متوسط'] += count
                    elif 'منخفض' in level_str or 'low' in level_str:
                        risk_levels['منخفض'] += count
        
        return pd.DataFrame([
            {'risk_level': level, 'count': count}
            for level, count in risk_levels.items()
        ])
    
    def _get_risk_trend(self, risk_data):
        """Calculate risk trend over time"""
        date_col = None
        risk_col = None
        
        for col in risk_data.columns:
            if risk_data[col].dtype == 'datetime64[ns]':
                date_col = col
                break
        
        for col in risk_data.columns:
            if any(keyword in col.lower() for keyword in ['نسب', 'مخاطر', 'risk', 'score']):
                if pd.api.types.is_numeric_dtype(risk_data[col]):
                    risk_col = col
                    break
        
        if not date_col or not risk_col:
            return pd.DataFrame()
        
        trend_data = risk_data[[date_col, risk_col]].dropna()
        trend_data = trend_data.groupby(pd.Grouper(key=date_col, freq='M')).agg({
            risk_col: 'mean'
        }).reset_index()
        
        trend_data.columns = ['date', 'risk_score']
        trend_data['risk_level'] = pd.cut(
            trend_data['risk_score'],
            bins=[0, 0.3, 0.7, 1.0],
            labels=['منخفض', 'متوسط', 'عالي']
        )
        
        return trend_data
    
    def _prepare_heatmap_data(self, unified_data):
        """Prepare data for activity heatmap"""
        activity_counts = {}
        
        for data_type, df in unified_data.items():
            if df.empty:
                continue
            
            dept_col = None
            activity_col = None
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['إدارة', 'قطاع', 'department']):
                    dept_col = col
                elif any(keyword in col.lower() for keyword in ['نشاط', 'activity', 'تصنيف']):
                    activity_col = col
            
            if dept_col and activity_col:
                cross_tab = pd.crosstab(df[dept_col], df[activity_col])
                for dept in cross_tab.index:
                    for activity in cross_tab.columns:
                        key = f"{dept}_{activity}"
                        activity_counts[key] = cross_tab.loc[dept, activity]
        
        if not activity_counts:
            return pd.DataFrame()
        
        # Convert to matrix format for heatmap
        departments = list(set([key.split('_')[0] for key in activity_counts.keys()]))
        activities = list(set(['_'.join(key.split('_')[1:]) for key in activity_counts.keys()]))
        
        heatmap_matrix = np.zeros((len(departments), len(activities)))
        
        for i, dept in enumerate(departments):
            for j, activity in enumerate(activities):
                key = f"{dept}_{activity}"
                heatmap_matrix[i, j] = activity_counts.get(key, 0)
        
        return pd.DataFrame(heatmap_matrix, index=departments, columns=activities)
    
    def _create_observations_trend(self, unified_data):
        """Create observations trend chart"""
        if 'inspections' not in unified_data or unified_data['inspections'].empty:
            st.warning("لا توجد بيانات ملاحظات متاحة")
            return
        
        df = unified_data['inspections']
        trend_data = self._extract_time_series(df, 'observations')
        
        if not trend_data.empty:
            fig = px.line(
                trend_data,
                x='date',
                y='count',
                title="اتجاه الملاحظات عبر الزمن",
                markers=True
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    def _create_incidents_trend(self, unified_data):
        """Create incidents trend chart"""
        if 'incidents' not in unified_data or unified_data['incidents'].empty:
            st.warning("لا توجد بيانات حوادث متاحة")
            return
        
        df = unified_data['incidents']
        trend_data = self._extract_time_series(df, 'incidents')
        
        if not trend_data.empty:
            fig = px.line(
                trend_data,
                x='date',
                y='count',
                title="اتجاه الحوادث عبر الزمن",
                markers=True,
                color_discrete_sequence=[self.color_palette['warning']]
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    def _create_audit_trend(self, unified_data):
        """Create audit trend chart"""
        if 'contractor_audits' not in unified_data or unified_data['contractor_audits'].empty:
            st.warning("لا توجد بيانات تدقيق متاحة")
            return
        
        df = unified_data['contractor_audits']
        trend_data = self._extract_time_series(df, 'audits')
        
        if not trend_data.empty:
            fig = px.line(
                trend_data,
                x='date',
                y='count',
                title="اتجاه التدقيق عبر الزمن",
                markers=True,
                color_discrete_sequence=[self.color_palette['info']]
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    def _extract_time_series(self, df, data_type):
        """Extract time series data from dataframe"""
        date_col = None
        for col in df.columns:
            if df[col].dtype == 'datetime64[ns]':
                date_col = col
                break
        
        if not date_col:
            return pd.DataFrame()
        
        time_series = df.groupby(pd.Grouper(key=date_col, freq='M')).size().reset_index()
        time_series.columns = ['date', 'count']
        
        return time_series
    
    def _get_overall_date_range(self, unified_data):
        """Get overall date range from all datasets"""
        all_dates = []
        
        for data_type, df in unified_data.items():
            if df.empty:
                continue
            
            for col in df.columns:
                if df[col].dtype == 'datetime64[ns]':
                    dates = df[col].dropna()
                    all_dates.extend(dates.tolist())
        
        if not all_dates:
            return None
        
        return {
            'min_date': min(all_dates).date(),
            'max_date': max(all_dates).date()
        }
    
    def _get_all_departments(self, unified_data):
        """Get all unique departments from datasets"""
        departments = set()
        
        for data_type, df in unified_data.items():
            if df.empty:
                continue
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['إدارة', 'قطاع', 'department']):
                    dept_values = df[col].dropna().unique()
                    departments.update(dept_values)
        
        return sorted(list(departments))
    
    def _get_all_statuses(self, unified_data):
        """Get all unique statuses from datasets"""
        statuses = set()
        
        for data_type, df in unified_data.items():
            if df.empty:
                continue
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['حالة', 'status']):
                    status_values = df[col].dropna().unique()
                    statuses.update(status_values)
        
        return sorted(list(statuses))
    
    def _get_all_activities(self, unified_data):
        """Get all unique activities from datasets"""
        activities = set()
        
        for data_type, df in unified_data.items():
            if df.empty:
                continue
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['نشاط', 'activity', 'تصنيف']):
                    activity_values = df[col].dropna().unique()
                    activities.update(activity_values)
        
        return sorted(list(activities))
    
    def _apply_filters(self, df, filters):
        """Apply filters to dataframe"""
        filtered_df = df.copy()
        
        if not filters:
            return filtered_df
        
        # Apply date filter
        if 'date_range' in filters and filters['date_range']:
            date_cols = [col for col in df.columns if df[col].dtype == 'datetime64[ns]']
            if date_cols:
                start_date, end_date = filters['date_range']
                for col in date_cols:
                    filtered_df = filtered_df[
                        (filtered_df[col].dt.date >= start_date) &
                        (filtered_df[col].dt.date <= end_date)
                    ]
        
        # Apply department filter
        if 'departments' in filters and filters['departments']:
            dept_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['إدارة', 'قطاع', 'department'])]
            if dept_cols:
                dept_filter = filtered_df[dept_cols[0]].isin(filters['departments'])
                filtered_df = filtered_df[dept_filter]
        
        # Apply status filter
        if 'statuses' in filters and filters['statuses']:
            status_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['حالة', 'status'])]
            if status_cols:
                status_filter = filtered_df[status_cols[0]].isin(filters['statuses'])
                filtered_df = filtered_df[status_filter]
        
        # Apply activity filter
        if 'activities' in filters and filters['activities']:
            activity_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['نشاط', 'activity', 'تصنيف'])]
            if activity_cols:
                activity_filter = filtered_df[activity_cols[0]].isin(filters['activities'])
                filtered_df = filtered_df[activity_filter]
        
        return filtered_df