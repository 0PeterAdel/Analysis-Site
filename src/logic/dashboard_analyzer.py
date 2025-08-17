"""
Business Logic Module for the Safety & Compliance Dashboard.
Handles calculations, aggregations, and advanced analytics based on unified data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
import json # Import json for serialization

# Ensure the config directory is in the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))

try:
    from config.settings import SECTORS, RISK_ACTIVITIES, STATUS_OPTIONS, PRIORITY_OPTIONS, RISK_LEVELS
except ImportError:
    # Fallback for local testing if config.settings is not directly accessible
    SECTORS = ["قطاع المشاريع", "قطاع التشغيل", "قطاع الخدمات", "قطاع التخصيص", "أخرى"]
    RISK_ACTIVITIES = ["الأماكن المغلقة", "الارتفاعات", "الحفريات", "الكهرباء"]
    STATUS_OPTIONS = ["الكل", "مفتوح", "مغلق", "قيد المراجعة", "مكتمل"]
    PRIORITY_OPTIONS = ["الكل", "عالي", "متوسط", "منخفض"]
    RISK_LEVELS = ["الكل", "مرتفع", "متوسط", "منخفض"]


class DashboardAnalyzer:
    """
    Analyzes unified safety and compliance data to generate insights,
    KPIs, and detailed reports.
    """

    def __init__(self):
        pass # No complex initialization needed here, data is passed to methods

    def _apply_common_filters(self, df: pd.DataFrame, filters: dict, 
                              date_col_name: str = 'التاريخ', 
                              sector_col_name: str = 'الإدارة',
                              status_col_name: str = 'الحالة',
                              activity_col_name: str = 'النشاط',
                              risk_level_col_name: str = 'التصنيف',
                              search_col_names: list = None):
        """
        Applies common filters (date range, sectors, status, priority, risk level, text search) to a DataFrame.
        Assumes standardized column names for filtering.
        """
        filtered_df = df.copy()

        # Apply date range filter
        if 'date_range' in filters and len(filters['date_range']) == 2:
            start_date, end_date = filters['date_range']
            if date_col_name in filtered_df.columns and pd.api.types.is_datetime64_any_dtype(filtered_df[date_col_name]):
                date_mask = (filtered_df[date_col_name] >= pd.Timestamp(start_date)) & \
                            (filtered_df[date_col_name] <= pd.Timestamp(end_date))
                filtered_df = filtered_df[date_mask]

        # Apply sector filter
        if 'sectors' in filters and filters['sectors']:
            actual_sector_col = None
            if sector_col_name in filtered_df.columns:
                actual_sector_col = sector_col_name
            elif 'القطاع' in filtered_df.columns:
                actual_sector_col = 'القطاع'

            if actual_sector_col:
                sector_mask = filtered_df[actual_sector_col].isin(filters['sectors'])
                filtered_df = filtered_df[sector_mask]
        
        # Apply status filter
        if 'status' in filters and filters['status'] and 'الكل' not in filters['status']:
            if status_col_name in filtered_df.columns:
                status_mask = filtered_df[status_col_name].astype(str).str.contains('|'.join(filters['status']), case=False, na=False)
                filtered_df = filtered_df[status_mask]

        # Apply priority filter (assuming 'الأولوية' column exists and contains string values like 'عالي', 'متوسط', 'منخفض', 'عاجل')
        if 'priority' in filters and filters['priority'] != "الكل":
            if 'الأولوية' in filtered_df.columns:
                priority_mask = filtered_df['الأولوية'].astype(str).str.contains(filters['priority'], case=False, na=False)
                filtered_df = filtered_df[priority_mask]

        # Apply risk level filter (assuming 'مستوى المخاطر' column exists and contains string values)
        if 'risk_level' in filters and filters['risk_level'] != "الكل":
            if 'مستوى المخاطر' in filtered_df.columns:
                risk_level_mask = filtered_df['مستوى المخاطر'].astype(str).str.contains(filters['risk_level'], case=False, na=False)
                filtered_df = filtered_df[risk_level_mask]

        # Apply text search filter
        if 'search_query' in filters and filters['search_query']:
            query = filters['search_query']
            if search_col_names is None:
                # Default to all object (string) columns if not specified
                search_col_names = filtered_df.select_dtypes(include=['object']).columns.tolist()
            
            if search_col_names:
                search_mask = filtered_df[search_col_names[0]].astype(str).str.contains(query, case=False, na=False)
                for col in search_col_names[1:]:
                    if col in filtered_df.columns:
                        search_mask |= filtered_df[col].astype(str).str.contains(query, case=False, na=False)
                filtered_df = filtered_df[search_mask]

        return filtered_df

    def get_compliance_summary(self, unified_data: dict, filters: dict = None) -> pd.DataFrame:
        """
        Generates a compliance summary DataFrame by sector.
        Calculates compliance percentage, trend, and priority.
        """
        inspections_df = unified_data.get('inspections', pd.DataFrame())
        
        if inspections_df.empty:
            return pd.DataFrame()

        # Apply common filters
        filtered_inspections_df = self._apply_common_filters(
            inspections_df, filters,
            date_col_name='التاريخ',
            sector_col_name='الإدارة',
            status_col_name='الحالة'
        )

        compliance_data = []

        if 'الحالة' not in filtered_inspections_df.columns or 'التاريخ' not in filtered_inspections_df.columns:
            return pd.DataFrame()
        if not pd.api.types.is_datetime64_any_dtype(filtered_inspections_df['التاريخ']):
            return pd.DataFrame()
        
        actual_sector_col = 'الإدارة' if 'الإدارة' in filtered_inspections_df.columns else \
                            'القطاع' if 'القطاع' in filtered_inspections_df.columns else None
        if actual_sector_col is None:
            return pd.DataFrame()

        available_sectors_in_data = filtered_inspections_df[actual_sector_col].dropna().unique().tolist()
        sectors_to_analyze = filters.get('sectors', available_sectors_in_data)
        if not sectors_to_analyze:
             sectors_to_analyze = SECTORS # Fallback to predefined if no sectors found

        for sector in sorted(list(set(sectors_to_analyze))):
            sector_df = filtered_inspections_df[
                filtered_inspections_df[actual_sector_col].astype(str).str.contains(str(sector), case=False, na=False)
            ]
            
            if sector_df.empty:
                continue
            
            total_records = len(sector_df)
            closed_records = sector_df['الحالة'].astype(str).str.contains('مغلق|مكتمل', case=False, na=False).sum()
            
            compliance_percentage = (closed_records / total_records * 100) if total_records > 0 else 0

            # Trend analysis (last 90 days vs. overall)
            recent_records_df = sector_df[sector_df['التاريخ'] >= (pd.Timestamp.now() - pd.Timedelta(days=90))]
            recent_compliance = 0
            if not recent_records_df.empty:
                recent_closed = recent_records_df['الحالة'].astype(str).str.contains('مغلق|مكتمل', case=False, na=False).sum()
                recent_compliance = (recent_closed / len(recent_records_df) * 100) if len(recent_records_df) > 0 else 0
            
            trend = recent_compliance - compliance_percentage

            # Enhanced recommendations based on multiple factors
            recommendation = "لا توجد توصية محددة"
            status_color = "⚪"
            priority = "متوسط"

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
            else: # Below 70%
                if trend > 5:
                    recommendation = "يحتاج تحسين مع وجود تقدم إيجابي"
                    status_color = "🔴"
                    priority = "عالي"
                else:
                    recommendation = "يحتاج تحسين عاجل وخطة عمل فورية"
                    status_color = "🔴"
                    priority = "عاجل"

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
            
            # Quarterly trend for detailed view
            if not recent_records_df.empty:
                # Group by quarter and calculate compliance percentage
                quarterly_trend_series = recent_records_df.groupby(recent_records_df['التاريخ'].dt.quarter)['الحالة'].apply(
                    lambda x: (x.astype(str).str.contains('مغلق|مكتمل', case=False, na=False).sum() / len(x) * 100) if len(x) > 0 else 0
                )
                sector_data['quarterly_trends'] = quarterly_trend_series.to_dict()
            else:
                sector_data['quarterly_trends'] = {} # No quarterly data if no recent records

            compliance_data.append(sector_data)
            
        return pd.DataFrame(compliance_data)

    def get_risk_activities_summary(self, unified_data: dict, filters: dict = None) -> pd.DataFrame:
        """
        Generates a summary of risk activities.
        
        Args:
            unified_data (dict): Dictionary of unified DataFrames (e.g., {'risk_assessments': df}).
            filters (dict, optional): Dictionary of filters to apply. Defaults to None.
            
        Returns:
            pd.DataFrame: A DataFrame with risk metrics per activity.
        """
        risk_assessments_df = unified_data.get('risk_assessments', pd.DataFrame())
        
        if risk_assessments_df.empty:
            return pd.DataFrame()

        # Apply common filters
        filtered_risk_df = self._apply_common_filters(
            risk_assessments_df, filters,
            date_col_name='التاريخ',
            sector_col_name='الإدارة',
            risk_level_col_name='التصنيف' # Pass risk_level_col_name to common filter
        )

        risk_data_list = []

        # Standardized column names from data_processor
        activity_col = 'النشاط' # Assuming 'تصنيف النشاط' is mapped to 'النشاط'
        risk_level_col = 'التصنيف' # Assuming 'التصنيف' or 'risk_level' is mapped to 'التصنيف'
        recommendation_col = 'التوصية_المقترحة' # Assuming 'الإجراءات التصحيحية والتوصيات' is mapped to 'التوصية_المقترحة'

        if activity_col not in filtered_risk_df.columns:
            print(f"Warning: '{activity_col}' column not found in risk assessments data.")
            return pd.DataFrame()
        
        # Handle missing 'التصنيف' column by deriving from 'نسبة_المخاطرة'
        if risk_level_col not in filtered_risk_df.columns:
            if 'نسبة_المخاطرة' in filtered_risk_df.columns:
                # Silently derive risk level from 'نسبة_المخاطرة'
                def categorize_risk_by_percentage(percentage):
                    try:
                        val = float(str(percentage).replace('%', ''))
                        if val >= 0.7: return 'عالي'
                        elif val >= 0.4: return 'متوسط'
                        else: return 'منخفض'
                    except (ValueError, TypeError):
                        return 'غير محدد'
                filtered_risk_df[risk_level_col] = filtered_risk_df['نسبة_المخاطرة'].apply(categorize_risk_by_percentage)
            else:
                # If neither column exists, create a default risk level
                filtered_risk_df[risk_level_col] = 'غير محدد'
        
        # Use a predefined list of activities or derive from data if empty
        activities_to_analyze = filtered_risk_df[activity_col].dropna().unique().tolist()
        if not activities_to_analyze:
            activities_to_analyze = RISK_ACTIVITIES # Fallback to general list from config

        for activity in sorted(list(set(activities_to_analyze))):
            activity_df = filtered_risk_df[
                filtered_risk_df[activity_col].astype(str).str.contains(str(activity), case=False, na=False)
            ]
            
            if activity_df.empty:
                continue

            total_assessments = len(activity_df)
            
            # Count high risks using the standardized risk_level_col
            high_risk_count = activity_df[
                activity_df[risk_level_col].astype(str).str.contains('عالي|مرتفع', case=False, na=False)
            ].shape[0] # Use .shape[0] for row count of filtered df

            risk_percentage = (high_risk_count / total_assessments * 100) if total_assessments > 0 else 0

            # Determine risk level and priority
            risk_level_label = "🟢 منخفض"
            priority_val = 3 # 1 (high), 2 (medium), 3 (low)
            recommendation = "مراقبة دورية"

            if risk_percentage >= 70:
                risk_level_label = "🔴 عالي"
                priority_val = 1
                recommendation = "مراجعة عاجلة"
            elif risk_percentage >= 40:
                risk_level_label = "🟡 متوسط"
                priority_val = 2
                recommendation = "مراقبة دورية مكثفة"
            
            risk_data_list.append({
                'النشاط': activity,
                'إجمالي التقييمات': total_assessments,
                'المخاطر العالية': high_risk_count,
                'مستوى المخاطر': risk_level_label,
                'نسبة المخاطر %': float(risk_percentage),
                'الأولوية': priority_val, # Numeric priority for sorting
                'التوصية': recommendation,
                # Convert the DataFrame to a JSON string to avoid UnhashableTypeError
                'details_df': activity_df.astype(str).to_json(orient='records', date_format='iso')
            })

        df_risk_activities = pd.DataFrame(risk_data_list)
        
        # Apply recommendation filter from UI
        if filters and 'recommendation_filter' in filters and filters['recommendation_filter'] != "الكل":
            if filters['recommendation_filter'] == "عاجل":
                df_risk_activities = df_risk_activities[df_risk_activities['الأولوية'] == 1]
            elif filters['recommendation_filter'] == "متوسط":
                df_risk_activities = df_risk_activities[df_risk_activities['الأولوية'] == 2]
            elif filters['recommendation_filter'] == "منخفض":
                df_risk_activities = df_risk_activities[df_risk_activities['الأولوية'] == 3]

        # Apply activity sort from UI
        if filters and 'activity_sort' in filters:
            if filters['activity_sort'] == "الأولوية":
                df_risk_activities = df_risk_activities.sort_values('الأولوية', ascending=True)
            elif filters['activity_sort'] == "الاسم":
                df_risk_activities = df_risk_activities.sort_values('النشاط', ascending=True)
            elif filters['activity_sort'] == "مستوى المخاطر":
                # Need to convert 'نسبة المخاطر %' to numeric for proper sorting
                df_risk_activities['نسبة المخاطر %_numeric'] = df_risk_activities['نسبة المخاطر %'].astype(float) # Already float, just ensure
                df_risk_activities = df_risk_activities.sort_values('نسبة المخاطر %_numeric', ascending=False)
                df_risk_activities = df_risk_activities.drop(columns=['نسبة المخاطر %_numeric'])
                
        return df_risk_activities

    def get_incidents_summary(self, unified_data: dict, filters: dict = None) -> pd.DataFrame:
        """
        Generates a summary of incidents by sector, including closure rates.
        
        Args:
            unified_data (dict): Dictionary of unified DataFrames (e.g., {'incidents': df}).
            filters (dict, optional): Dictionary of filters to apply. Defaults to None.
            
        Returns:
            pd.DataFrame: A DataFrame with incident metrics per sector.
        """
        incidents_df = unified_data.get('incidents', pd.DataFrame())
        
        if incidents_df.empty:
            return pd.DataFrame()

        # Apply common filters
        filtered_incidents_df = self._apply_common_filters(
            incidents_df, filters,
            date_col_name='التاريخ',
            sector_col_name='الإدارة',
            status_col_name='الحالة'
        )

        incidents_data_list = []

        # Determine actual sector column to use
        actual_sector_col = None
        if 'الإدارة' in filtered_incidents_df.columns:
            actual_sector_col = 'الإدارة'
        elif 'القطاع' in filtered_incidents_df.columns:
            actual_sector_col = 'القطاع'
        else:
            print("Warning: No suitable sector/department column found for incidents summary.")
            return pd.DataFrame()

        # Use unique sectors from the filtered data
        sectors_to_analyze = filtered_incidents_df[actual_sector_col].dropna().unique().tolist()
        if not sectors_to_analyze:
            sectors_to_analyze = SECTORS # Fallback

        for sector in sorted(list(set(sectors_to_analyze))):
            sector_incidents = filtered_incidents_df[
                filtered_incidents_df[actual_sector_col].astype(str).str.contains(str(sector), case=False, na=False)
            ]
            
            if sector_incidents.empty:
                continue

            total_incidents = len(sector_incidents)
            
            # Assuming 'التوصية_المقترحة' or similar is mapped to 'التوصية_المقترحة'
            # and 'الحالة' is mapped to 'الحالة'
            recommendations_count = sector_incidents['التوصية_المقترحة'].notna().sum() if 'التوصية_المقترحة' in sector_incidents.columns else total_incidents
            closed_count = sector_incidents['الحالة'].astype(str).str.contains('مغلق|مكتمل', case=False, na=False).sum()

            closure_percentage = (closed_count / recommendations_count * 100) if recommendations_count > 0 else 0

            incidents_data_list.append({
                'القطاع': sector,
                'عدد الحوادث': total_incidents,
                'عدد التوصيات': recommendations_count,
                'مغلق': closed_count,
                'مفتوح': recommendations_count - closed_count,
                'نسبة الإغلاق %': float(closure_percentage)
            })

        return pd.DataFrame(incidents_data_list)
    
    def get_compliance_status_distribution(self, unified_data: dict, filters: dict = None) -> pd.DataFrame:
        """
        Extracts compliance status distribution from unified inspections data.
        """
        inspections_df = unified_data.get('inspections', pd.DataFrame())
        if inspections_df.empty:
            return pd.DataFrame()

        filtered_df = self._apply_common_filters(inspections_df, filters, status_col_name='الحالة')

        compliance_counts = {'مغلق': 0, 'مفتوح': 0}
        if 'الحالة' in filtered_df.columns:
            status_counts = filtered_df['الحالة'].value_counts()
            compliance_counts['مغلق'] = status_counts.get('مغلق', 0)
            compliance_counts['مفتوح'] = status_counts.get('مفتوح', 0)
        
        return pd.DataFrame([
            {'status': 'مغلق', 'count': compliance_counts['مغلق']},
            {'status': 'مفتوح', 'count': compliance_counts['مفتوح']}
        ])

    def get_department_compliance_performance(self, unified_data: dict, filters: dict = None) -> pd.DataFrame:
        """
        Calculates department compliance performance metrics from unified inspections data.
        """
        inspections_df = unified_data.get('inspections', pd.DataFrame())
        if inspections_df.empty:
            return pd.DataFrame()
        
        filtered_df = self._apply_common_filters(inspections_df, filters, 
                                                sector_col_name='الإدارة', 
                                                status_col_name='الحالة')

        dept_performance = {}
        
        actual_dept_col = 'الإدارة' if 'الإدارة' in filtered_df.columns else \
                          'القطاع' if 'القطاع' in filtered_df.columns else None
        
        if actual_dept_col and 'الحالة' in filtered_df.columns:
            dept_status = filtered_df.groupby(actual_dept_col)['الحالة'].value_counts().unstack(fill_value=0)
            for dept in dept_status.index:
                closed = dept_status.loc[dept].get('مغلق', 0)
                total = dept_status.loc[dept].sum()
                compliance_rate = (closed / total * 100) if total > 0 else 0
                
                dept_performance[dept] = compliance_rate
        
        result = [{'department': dept, 'compliance_rate': rate} for dept, rate in dept_performance.items()]
        return pd.DataFrame(result)

    def get_risk_level_distribution(self, unified_data: dict, filters: dict = None) -> pd.DataFrame:
        """
        Extracts risk level distribution from unified risk assessments data.
        """
        risk_assessments_df = unified_data.get('risk_assessments', pd.DataFrame())
        if risk_assessments_df.empty:
            return pd.DataFrame()
        
        filtered_df = self._apply_common_filters(risk_assessments_df, filters, risk_level_col_name='التصنيف')

        risk_level_col = 'التصنيف' # Standardized column name
        if risk_level_col not in filtered_df.columns:
            # Fallback to deriving from 'نسبة_المخاطرة' if 'التصنيف' is missing
            if 'نسبة_المخاطرة' in filtered_df.columns:
                def categorize_risk_by_percentage(percentage):
                    try:
                        val = float(str(percentage).replace('%', ''))
                        if val >= 0.7: return 'عالي'
                        elif val >= 0.4: return 'متوسط'
                        else: return 'منخفض'
                    except (ValueError, TypeError):
                        return 'غير محدد'
                filtered_df[risk_level_col] = filtered_df['نسبة_المخاطرة'].apply(categorize_risk_by_percentage)
            else:
                return pd.DataFrame() # Cannot determine risk levels

        risk_counts = filtered_df[risk_level_col].value_counts().to_dict()
        
        # Ensure all standard risk levels are present, even if count is 0
        standard_risk_levels = ['عالي', 'متوسط', 'منخفض']
        for level in standard_risk_levels:
            if level not in risk_counts:
                risk_counts[level] = 0

        return pd.DataFrame([
            {'risk_level': level, 'count': count}
            for level, count in risk_counts.items()
        ]).sort_values('risk_level', ascending=False) # Sort for consistent display

    def get_risk_trend_over_time(self, unified_data: dict, filters: dict = None) -> pd.DataFrame:
        """
        Calculates risk trend over time from unified risk assessments data.
        """
        risk_assessments_df = unified_data.get('risk_assessments', pd.DataFrame())
        if risk_assessments_df.empty:
            return pd.DataFrame()
        
        filtered_df = self._apply_common_filters(risk_assessments_df, filters, date_col_name='التاريخ')

        date_col = 'التاريخ'
        risk_score_col = 'نسبة_المخاطرة' # Standardized column for numeric risk score

        if date_col not in filtered_df.columns or risk_score_col not in filtered_df.columns:
            return pd.DataFrame()
        
        # Ensure risk_score_col is numeric
        filtered_df[risk_score_col] = pd.to_numeric(filtered_df[risk_score_col], errors='coerce')
        
        trend_data = filtered_df[[date_col, risk_score_col]].dropna()
        
        if trend_data.empty:
            return pd.DataFrame()

        # Group by month for trend
        trend_data = trend_data.groupby(pd.Grouper(key=date_col, freq='M')).agg(
            risk_score=(risk_score_col, 'mean')
        ).reset_index()
        
        trend_data.columns = ['date', 'risk_score']
        
        # Categorize risk level for coloring/labeling
        trend_data['risk_level'] = pd.cut(
            trend_data['risk_score'],
            bins=[0, 0.3, 0.7, 1.0], # Example bins, adjust as per your risk model
            labels=['منخفض', 'متوسط', 'عالي'],
            right=True # Include the rightmost bin edge
        )
        
        return trend_data

    def prepare_activity_heatmap_data(self, unified_data: dict, filters: dict = None) -> pd.DataFrame:
        """
        Prepares data for an activity heatmap, showing density by department and activity type.
        """
        all_data_for_heatmap = pd.DataFrame()
        # Concatenate relevant dataframes for heatmap (e.g., inspections, incidents, risk_assessments)
        for key in ['inspections', 'incidents', 'risk_assessments', 'contractor_audits', 'safety_checks', 'recommendations']:
            df = unified_data.get(key)
            if df is not None and not df.empty:
                # Select relevant columns, assuming 'الإدارة'/'القطاع' and 'النشاط' are standardized
                if 'الإدارة' in df.columns and 'النشاط' in df.columns:
                    all_data_for_heatmap = pd.concat([all_data_for_heatmap, df[['الإدارة', 'النشاط']]], ignore_index=True)
                elif 'القطاع' in df.columns and 'النشاط' in df.columns:
                     all_data_for_heatmap = pd.concat([all_data_for_heatmap, df[['القطاع', 'النشاط']].rename(columns={'القطاع': 'الإدارة'})], ignore_index=True)

        if all_data_for_heatmap.empty:
            return pd.DataFrame()
        
        # Apply common filters to the combined data
        filtered_data_for_heatmap = self._apply_common_filters(
            all_data_for_heatmap, filters,
            sector_col_name='الإدارة',
            activity_col_name='النشاط'
        )

        if filtered_data_for_heatmap.empty or 'الإدارة' not in filtered_data_for_heatmap.columns or 'النشاط' not in filtered_data_for_heatmap.columns:
            return pd.DataFrame()

        # Clean and standardize department and activity names
        filtered_data_for_heatmap['الإدارة'] = filtered_data_for_heatmap['الإدارة'].astype(str).str.strip()
        filtered_data_for_heatmap['النشاط'] = filtered_data_for_heatmap['النشاط'].astype(str).str.strip()

        # Create a pivot table (cross-tabulation)
        heatmap_pivot = pd.crosstab(
            filtered_data_for_heatmap['الإدارة'], 
            filtered_data_for_heatmap['النشاط'], 
            dropna=False # Keep NaN values if any, though _clean_text_data should handle it
        )
        
        # Fill any NaN values (where a combination doesn't exist) with 0
        heatmap_matrix = heatmap_pivot.fillna(0)
        
        return heatmap_matrix

    def get_time_series_data(self, unified_data: dict, data_type_key: str, filters: dict = None) -> pd.DataFrame:
        """
        Extracts and aggregates time series data for a specific unified data type.
        """
        df = unified_data.get(data_type_key, pd.DataFrame())
        if df.empty:
            return pd.DataFrame()
        
        filtered_df = self._apply_common_filters(df, filters, date_col_name='التاريخ')

        date_col = 'التاريخ'
        if date_col not in filtered_df.columns or not pd.api.types.is_datetime64_any_dtype(filtered_df[date_col]):
            return pd.DataFrame()
        
        # Group by month for trend
        time_series = filtered_df.groupby(pd.Grouper(key=date_col, freq='M')).size().reset_index()
        time_series.columns = ['date', 'count']
        
        return time_series

    def generate_analytics_insights(self, unified_data: dict, filters: dict = None) -> list:
        """
        Generates AI-powered analytics insights based on the unified data.
        This function now uses the analyzer's own methods to get aggregated data.
        """
        insights = []

        # Insight 1: Data completeness (using overall KPI data)
        overall_kpis = {}
        # Access kpi_data from st.session_state as it's generated by DataProcessor and stored there
        if 'kpi_data' in st.session_state:
            for kpi_type, kpi_info in st.session_state.kpi_data.items():
                if kpi_info and kpi_info.get('total_records') is not None:
                    overall_kpis[kpi_type] = kpi_info

        total_records_overall = sum([data.get('total_records', 0) for data in overall_kpis.values()])
        if total_records_overall > 0:
            insights.append({
                'title': 'اكتمال البيانات',
                'description': f'يحتوي النظام على {total_records_overall:,} سجل عبر {len(overall_kpis)} مجموعة بيانات.',
                'recommendation': 'تأكد من تحديث البيانات بانتظام للحصول على رؤى دقيقة.',
                'priority': 'متوسط'
            })
        
        # Insight 2: Compliance Rate
        compliance_summary_df = self.get_compliance_summary(unified_data, filters)
        if not compliance_summary_df.empty:
            overall_compliance_rate = compliance_summary_df['نسبة الامتثال %'].mean()
            
            if overall_compliance_rate < 70:
                priority = 'عالي'
                recommendation = 'معدل الامتثال منخفض. يجب التركيز على إغلاق الحالات المفتوحة.'
            elif overall_compliance_rate < 85:
                priority = 'متوسط'
                recommendation = 'معدل الامتثال جيد ولكن يمكن تحسينه.'
            else:
                priority = 'منخفض'
                recommendation = 'معدل الامtثtال ممتاز. حافظ على هذا الأداء.'
            
            insights.append({
                'title': 'معدل الامتثال الإجمالي',
                'description': f'معدل الامتثال الإجمالي الحالي هو {overall_compliance_rate:.1f}%.',
                'recommendation': recommendation,
                'priority': priority
            })
        
        # Insight 3: Top Risk Activity
        risk_activities_summary_df = self.get_risk_activities_summary(unified_data, filters)
        if not risk_activities_summary_df.empty:
            # Sort by priority (1=high, 3=low) to find the most critical activity
            most_critical_activity_row = risk_activities_summary_df.sort_values('الأولوية', ascending=True).iloc[0]
            
            insights.append({
                'title': 'النشاط الأكثر خطورة',
                'description': f'النشاط الأكثر خطورة هو "{most_critical_activity_row["النشاط"]}" بمستوى مخاطر "{most_critical_activity_row["مستوى المخاطر"]}" ونسبة مخاطر {most_critical_activity_row["نسبة المخاطر %"]}.',
                'recommendation': most_critical_activity_row['التوصية'],
                'priority': most_critical_activity_row['الأولوية'] # Use the string priority
            })

        # Insight 4: Incident Closure Rate
        incidents_summary_df = self.get_incidents_summary(unified_data, filters)
        if not incidents_summary_df.empty:
            total_closed_incidents = incidents_summary_df['مغلق'].sum()
            total_recommendations_incidents = incidents_summary_df['عدد التوصيات'].sum()
            overall_incident_closure_rate = (total_closed_incidents / total_recommendations_incidents * 100) if total_recommendations_incidents > 0 else 0

            if overall_incident_closure_rate < 70:
                priority = 'عالي'
                recommendation = 'معدل إغلاق الحوادث منخفض. يجب تسريع الإجراءات التصحيحية للحوادث المفتوحة.'
            elif overall_incident_closure_rate < 90:
                priority = 'متوسط'
                recommendation = 'معدل إغلاق الحوادث جيد. استمر في المتابعة لتحقيق نسبة أعلى.'
            else:
                priority = 'منخفض'
                recommendation = 'معدل إغلاق الحوادث ممتاز. حافظ على فعالية عمليات الإغلاق.'
            
            insights.append({
                'title': 'معدل إغلاق الحوادث',
                'description': f'معدل إغلاق توصيات الحوادث الإجمالي هو {overall_incident_closure_rate:.1f}%.',
                'recommendation': recommendation,
                'priority': priority
            })
        
        return insights


# Example usage (for testing this module independently)
def main():
    # This example requires data_processor to be functional
    from src.utils.data_processor import SafetyDataProcessor
    
    processor = SafetyDataProcessor()
    
    # Load all raw data
    raw_data_sources = processor.load_all_data()
            
    # Create unified dataset
    unified_data = processor.create_unified_dataset(raw_data_sources)
    
    analyzer = DashboardAnalyzer()

    # Test compliance summary
    compliance_df = analyzer.get_compliance_summary(unified_data)
    print("\n--- Compliance Summary ---")
    print(compliance_df.head())
    
    # Test risk activities summary
    risk_df = analyzer.get_risk_activities_summary(unified_data)
    print("\n--- Risk Activities Summary ---")
    print(risk_df.head())

    # Test incidents summary
    incidents_df = analyzer.get_incidents_summary(unified_data)
    print("\n--- Incidents Summary ---")
    print(incidents_df.head())

    # Test new analytical functions
    compliance_dist = analyzer.get_compliance_status_distribution(unified_data)
    print("\n--- Compliance Status Distribution ---")
    print(compliance_dist)

    dept_perf = analyzer.get_department_compliance_performance(unified_data)
    print("\n--- Department Compliance Performance ---")
    print(dept_perf.head())

    risk_dist = analyzer.get_risk_level_distribution(unified_data)
    print("\n--- Risk Level Distribution ---")
    print(risk_dist)

    risk_trend = analyzer.get_risk_trend_over_time(unified_data)
    print("\n--- Risk Trend Over Time ---")
    print(risk_trend.head())

    heatmap_data = analyzer.prepare_activity_heatmap_data(unified_data)
    print("\n--- Activity Heatmap Data ---")
    print(heatmap_data.head())

    time_series_obs = analyzer.get_time_series_data(unified_data, 'inspections')
    print("\n--- Observations Time Series ---")
    print(time_series_obs.head())
    
    insights = analyzer.generate_analytics_insights(unified_data)
    print("\n--- Generated Insights ---")
    for insight in insights:
        print(f"Title: {insight['title']}, Priority: {insight['priority']}")


if __name__ == "__main__":
    main()
