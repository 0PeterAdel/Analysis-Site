"""
Gemini AI Chatbot Integration
Intelligent chatbot for safety and compliance data analysis using Google's Gemini API
"""
import dotenv
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import re
import requests
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Gemini API configuration
GEMINI_API_KEY = dotenv.get_key('.env', 'GEMINI_API_KEY')  # Load from .env file
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent'

# Note: In production, you would use the actual Google Gemini API
# For this demo, we'll create a comprehensive mock implementation

class GeminiChatbot:
    """Intelligent chatbot for safety and compliance data analysis"""
    
    def __init__(self, unified_data, kpi_data):
        self.unified_data = unified_data
        self.kpi_data = kpi_data
        self.conversation_history = []
        
        # Initialize knowledge base
        self.knowledge_base = self._build_knowledge_base()
        
        # Common queries and responses
        self.query_patterns = {
            'total_incidents': ['كم عدد الحوادث', 'إجمالي الحوادث', 'total incidents'],
            'open_cases': ['الحالات المفتوحة', 'المفتوح', 'open cases'],
            'closed_cases': ['الحالات المغلقة', 'المغلق', 'closed cases'],
            'department_performance': ['أداء القطاع', 'القطاعات', 'department performance'],
            'risk_assessment': ['تقييم المخاطر', 'المخاطر', 'risk assessment'],
            'compliance_rate': ['معدل الامتثال', 'الامتثال', 'compliance rate'],
            'trends': ['الاتجاهات', 'التطور', 'trends', 'trend'],
            'statistics': ['إحصائيات', 'statistics', 'stats']
        }
    
    def _analyze_columns(self, df):
        """Analyze dataframe columns and categorize them by type"""
        column_analysis = {
            'date_columns': [],
            'numeric_columns': [],
            'categorical_columns': [],
            'text_columns': [],
            'status_columns': [],
            'department_columns': []
        }
        
        for col in df.columns:
            col_lower = str(col).lower()
            # Analyze column type and content
            if df[col].dtype == 'datetime64[ns]' or any(x in col_lower for x in ['تاريخ', 'date', 'وقت', 'time']):
                column_analysis['date_columns'].append(col)
            elif df[col].dtype in ['int64', 'float64'] or any(x in col_lower for x in ['عدد', 'number', 'كمية', 'quantity']):
                column_analysis['numeric_columns'].append(col)
            elif any(x in col_lower for x in ['حالة', 'status', 'مغلق', 'مفتوح']):
                column_analysis['status_columns'].append(col)
            elif any(x in col_lower for x in ['إدارة', 'قطاع', 'department']):
                column_analysis['department_columns'].append(col)
            elif df[col].dtype == 'object' and df[col].nunique() <= 20:
                column_analysis['categorical_columns'].append(col)
            else:
                column_analysis['text_columns'].append(col)
        
        return column_analysis
    
    def _suggest_visualizations(self, df, columns, query):
        """Suggest appropriate visualizations based on column types and query"""
        charts = []
        query_lower = query.lower()
        
        # Time series analysis
        if any(word in query_lower for word in ['تطور', 'اتجاه', 'trend', 'over time']) and columns['date_columns']:
            date_col = columns['date_columns'][0]
            if columns['numeric_columns']:
                for num_col in columns['numeric_columns'][:2]:  # Limit to 2 metrics
                    fig = go.Figure()
                    df[date_col] = pd.to_datetime(df[date_col])
                    monthly_data = df.groupby(df[date_col].dt.strftime('%Y-%m'))[num_col].mean()
                    fig.add_trace(go.Scatter(
                        x=monthly_data.index,
                        y=monthly_data.values,
                        mode='lines+markers',
                        name=num_col
                    ))
                    fig.update_layout(
                        title=f"تطور {num_col} عبر الزمن",
                        xaxis_title="الشهر",
                        yaxis_title=num_col,
                        template="plotly_white"
                    )
                    charts.append(fig)
        
        # Distribution analysis
        if any(word in query_lower for word in ['توزيع', 'distribution']):
            if columns['categorical_columns']:
                for cat_col in columns['categorical_columns'][:2]:  # Limit to 2 categories
                    value_counts = df[cat_col].value_counts()
                    fig = px.pie(
                        values=value_counts.values,
                        names=value_counts.index,
                        title=f"توزيع {cat_col}"
                    )
                    charts.append(fig)
        
        # Status analysis
        if any(word in query_lower for word in ['حالة', 'status']) and columns['status_columns']:
            for status_col in columns['status_columns']:
                value_counts = df[status_col].value_counts()
                fig = go.Figure(data=[
                    go.Pie(
                        labels=value_counts.index,
                        values=value_counts.values,
                        hole=.3
                    )
                ])
                fig.update_layout(
                    title=f"توزيع {status_col}",
                    template="plotly_white"
                )
                charts.append(fig)
        
        # Department performance
        if any(word in query_lower for word in ['قطاع', 'إدارة', 'department']) and columns['department_columns']:
            dept_col = columns['department_columns'][0]
            if columns['numeric_columns']:
                for metric in columns['numeric_columns'][:2]:
                    dept_metrics = df.groupby(dept_col)[metric].mean().sort_values(ascending=False)
                    fig = px.bar(
                        x=dept_metrics.index,
                        y=dept_metrics.values,
                        title=f"{metric} حسب {dept_col}",
                        labels={'x': dept_col, 'y': metric}
                    )
                    charts.append(fig)
        
        return charts
    
    def _build_knowledge_base(self):
        """Build knowledge base from unified data"""
        knowledge = {
            'data_summary': {},
            'key_metrics': {},
            'insights': [],
            'column_analysis': {}  # Add column analysis to knowledge base
        }
        
        total_records = 0
        total_open = 0
        total_closed = 0
        dept_counts = {}
        
        # Build data summary
        for data_type, df in self.unified_data.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                total_records += len(df)
                
                # Status analysis
                status_col = next((col for col in df.columns 
                                 if any(x in str(col).lower() for x in ['حالة', 'status'])), None)
                if status_col:
                    closed = df[status_col].str.contains('مغلق|closed', case=False, na=False).sum()
                    opened = len(df) - closed
                    total_closed += closed
                    total_open += opened
                
                # Department analysis
                dept_col = next((col for col in df.columns 
                               if any(x in str(col).lower() for x in ['إدارة', 'قطاع', 'department'])), None)
                if dept_col:
                    for dept, count in df[dept_col].value_counts().items():
                        dept_counts[dept] = dept_counts.get(dept, 0) + count
                
                knowledge['data_summary'][data_type] = {
                    'total_records': len(df),
                    'columns': list(df.columns),
                    'date_range': self._get_date_range(df),
                    'key_statistics': self._get_key_statistics(df)
                }
        
        # Build key metrics
        knowledge['key_metrics'] = self.kpi_data if self.kpi_data else {}
        
        # Generate main insights
        insights = []
        insights.append(f"يحتوي النظام على إجمالي {total_records:,} سجل عبر جميع أنواع البيانات")
        
        if total_open + total_closed > 0:
            compliance_rate = (total_closed / (total_open + total_closed)) * 100
            insights.append(f"معدل الامتثال الإجمالي هو {compliance_rate:.1f}% ({total_closed:,} مغلق من أصل {total_open + total_closed:,})")
        
        if dept_counts:
            top_dept = max(dept_counts.items(), key=lambda x: x[1])
            insights.append(f"القطاع الأكثر نشاطاً هو {top_dept[0]} بـ {top_dept[1]:,} سجل")
        
        knowledge['insights'] = insights
        
        return knowledge
    
    def _get_date_range(self, df):
        """Get date range from dataframe"""
        date_columns = [col for col in df.columns if df[col].dtype == 'datetime64[ns]']
        if not date_columns:
            return None
        
        all_dates = pd.concat([df[col].dropna() for col in date_columns])
        if len(all_dates) == 0:
            return None
        
        return {
            'start': all_dates.min().strftime('%Y-%m-%d'),
            'end': all_dates.max().strftime('%Y-%m-%d'),
            'days': (all_dates.max() - all_dates.min()).days
        }
    
    def _get_key_statistics(self, df):
        """Get key statistics from dataframe"""
        stats = {}
        
        # Status distribution
        status_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['حالة', 'status'])]
        if status_cols:
            status_dist = df[status_cols[0]].value_counts().to_dict()
            stats['status_distribution'] = status_dist
        
        # Department distribution
        dept_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['إدارة', 'قطاع', 'department'])]
        if dept_cols:
            dept_dist = df[dept_cols[0]].value_counts().head(5).to_dict()
            stats['top_departments'] = dept_dist
        
        return stats
    
    def _generate_insights(self):
        """Generate automatic insights from data"""
        insights = []
        
        # Total records insight
        total_records = sum([len(df) for df in self.unified_data.values() if not df.empty])
        insights.append(f"يحتوي النظام على إجمالي {total_records:,} سجل عبر جميع أنواع البيانات")
        
        # Compliance insight
        total_open = 0
        total_closed = 0
        
        for data_type, df in self.unified_data.items():
            if df.empty:
                continue
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['حالة', 'status']):
                    status_counts = df[col].value_counts()
                    for status, count in status_counts.items():
                        if 'مفتوح' in str(status):
                            total_open += count
                        elif 'مغلق' in str(status):
                            total_closed += count
        
        if total_open + total_closed > 0:
            compliance_rate = (total_closed / (total_open + total_closed)) * 100
            insights.append(f"معدل الامتثال الإجمالي هو {compliance_rate:.1f}% ({total_closed:,} مغلق من أصل {total_open + total_closed:,})")
        
        # Department insight
        dept_performance = {}
        for data_type, df in self.unified_data.items():
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
                dept_counts = df[dept_col].value_counts()
                top_dept = dept_counts.index[0] if len(dept_counts) > 0 else None
                if top_dept:
                    insights.append(f"القطاع الأكثر نشاطاً هو {top_dept} بـ {dept_counts.iloc[0]:,} سجل")
                    break
        
        return insights
    
    def call_gemini_api(self, prompt):
        """Call Gemini API with the given prompt"""
        try:
            url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                return "عذراً، لم أتمكن من فهم الاستفسار. هل يمكنك إعادة صياغة السؤال؟"
                
        except Exception as e:
            st.error(f"Error calling Gemini API: {str(e)}")
            return "عذراً، حدث خطأ في معالجة الاستفسار. الرجاء المحاولة مرة أخرى."
    
    def _prepare_context_for_gemini(self):
        """Prepare context about the data for Gemini"""
        context = "أنا مساعد ذكي متخصص في تحليل بيانات السلامة والامتثال. لدي الوصول إلى البيانات التالية وسأقوم بتحليلها:\n\n"
        
        # Process and analyze data first
        incidents_data = None
        for data_type, df in self.unified_data.items():
            if 'حوادث' in str(data_type) and not df.empty:
                incidents_data = df
                break
        
        # Add specific incident analysis if available
        if incidents_data is not None:
            # Find date column
            date_col = None
            for col in incidents_data.columns:
                if any(x in str(col).lower() for x in ['تاريخ', 'date']):
                    date_col = col
                    break
            
            if date_col:
                try:
                    incidents_data[date_col] = pd.to_datetime(incidents_data[date_col], errors='coerce')
                    latest_incidents = incidents_data.sort_values(date_col, ascending=False).head(5)
                    
                    context += "تحليل الحوادث:\n"
                    context += f"• إجمالي عدد الحوادث: {len(incidents_data)}\n"
                    context += f"• آخر تاريخ حادث: {latest_incidents[date_col].iloc[0].strftime('%Y-%m-%d')}\n"
                    context += "\nآخر 5 حوادث:\n"
                    
                    desc_col = next((col for col in incidents_data.columns if any(x in str(col).lower() for x in ['وصف', 'description', 'تفاصيل'])), None)
                    
                    for idx, incident in latest_incidents.iterrows():
                        incident_desc = incident[desc_col] if desc_col else "لا يوجد وصف"
                        incident_date = incident[date_col].strftime('%Y-%m-%d')
                        context += f"• {incident_date}: {incident_desc[:100]}...\n"
                except Exception as e:
                    context += f"\nملاحظة: تم العثور على بيانات الحوادث ولكن هناك مشكلة في تنسيق التواريخ: {str(e)}\n"
        
        # Add general data overview
        context += "\nالبيانات المتوفرة:\n"
        for data_type, df in self.unified_data.items():
            if not df.empty:
                context += f"• {data_type}: {len(df)} سجل\n"
                context += f"  - الأعمدة: {', '.join(df.columns[:5])}... وغيرها\n"
        
        if self.kpi_data:
            context += "\nمؤشرات الأداء الرئيسية المتوفرة:\n"
            for kpi_name, kpi_value in self.kpi_data.items():
                context += f"• {kpi_name}\n"
        
        return context

    def analyze_data_for_query(self, query):
        """Analyze data based on the query and generate visualizations"""
        query_lower = query.lower()
        response_text = ""
        fig = None
        data = None

        # Check different query types and generate appropriate visualizations
        if any(word in query_lower for word in ['حوادث', 'حادث', 'آخر']):
            # Find incidents data
            incidents_data = None
            for data_type, df in self.unified_data.items():
                if any(x in str(data_type).lower() for x in ['حوادث', 'incidents']) and not df.empty:
                    incidents_data = df.copy()  # Create a copy to avoid modifying original
                    break
            
            if incidents_data is not None:
                # Find date column
                date_col = next((col for col in incidents_data.columns 
                               if any(x in str(col).lower() for x in ['تاريخ', 'date', 'وقت', 'time'])), None)
                
                if date_col:
                    try:
                        # Convert dates and handle errors
                        incidents_data[date_col] = pd.to_datetime(incidents_data[date_col], errors='coerce')
                        incidents_data = incidents_data.dropna(subset=[date_col])  # Remove rows with invalid dates
                        
                        # Get latest incidents
                        latest_incidents = incidents_data.sort_values(date_col, ascending=False).head(5)
                        
                        # Create monthly trend chart
                        fig = go.Figure()
                        monthly_counts = incidents_data.groupby(incidents_data[date_col].dt.strftime('%Y-%m'))[date_col].count()
                        
                        fig.add_trace(go.Scatter(
                            x=monthly_counts.index,
                            y=monthly_counts.values,
                            mode='lines+markers',
                            name='عدد الحوادث الشهري',
                            line=dict(color='#1f77b4', width=2),
                            marker=dict(size=8)
                        ))
                        
                        fig.update_layout(
                            title="توزيع الحوادث الشهري",
                            xaxis_title="الشهر",
                            yaxis_title="عدد الحوادث",
                            template="plotly_white",
                            showlegend=True,
                            hovermode='x unified'
                        )
                        
                        data = latest_incidents
                        response_text = "تحليل بيانات الحوادث:\n\n"
                        response_text += f"📊 إجمالي عدد الحوادث: {len(incidents_data)}\n"
                        response_text += f"📅 آخر تاريخ حادث: {latest_incidents[date_col].iloc[0].strftime('%Y-%m-%d')}\n\n"
                        response_text += "آخر 5 حوادث:\n"
                        
                        desc_col = next((col for col in incidents_data.columns 
                                       if any(x in str(col).lower() for x in ['وصف', 'description'])), None)
                        
                        for idx, incident in latest_incidents.iterrows():
                            incident_desc = incident[desc_col] if desc_col else "لا يوجد وصف"
                            incident_date = incident[date_col].strftime('%Y-%m-%d')
                            response_text += f"\n📌 {incident_date}: {incident_desc}"
                    except Exception as e:
                        response_text = f"عذراً، حدث خطأ في تحليل بيانات الحوادث: {str(e)}"

        elif any(word in query_lower for word in ['مخاطر', 'خطر', 'risk']):
            risk_data = None
            for data_type, df in self.unified_data.items():
                if 'مخاطر' in str(data_type) and not df.empty:
                    risk_data = df
                    break
            
            if risk_data is not None:
                risk_level_col = next((col for col in risk_data.columns 
                                     if any(x in str(col).lower() for x in ['مستوى', 'level'])), None)
                
                if risk_level_col:
                    risk_counts = risk_data[risk_level_col].value_counts()
                    
                    fig = px.pie(
                        values=risk_counts.values,
                        names=risk_counts.index,
                        title="توزيع مستويات المخاطر"
                    )
                    
                    data = risk_data
                    response_text = "تحليل المخاطر:\n\n"
                    response_text += f"📊 إجمالي عدد المخاطر: {len(risk_data)}\n\n"
                    response_text += "توزيع مستويات المخاطر:\n"
                    for level, count in risk_counts.items():
                        response_text += f"• {level}: {count} ({count/len(risk_data)*100:.1f}%)\n"

        elif any(word in query_lower for word in ['امتثال', 'compliance']):
            total_open = 0
            total_closed = 0
            compliance_data = {}
            
            for data_type, df in self.unified_data.items():
                if df.empty:
                    continue
                
                status_col = next((col for col in df.columns 
                                 if any(x in str(col).lower() for x in ['حالة', 'status'])), None)
                
                if status_col:
                    closed = df[status_col].str.contains('مغلق|closed', case=False, na=False).sum()
                    opened = len(df) - closed
                    total_closed += closed
                    total_open += opened
                    compliance_data[data_type] = {'مغلق': closed, 'مفتوح': opened}
            
            if compliance_data:
                fig = go.Figure()
                for status in ['مغلق', 'مفتوح']:
                    values = [data[status] for data in compliance_data.values()]
                    fig.add_trace(go.Bar(
                        name=status,
                        x=list(compliance_data.keys()),
                        y=values
                    ))
                
                fig.update_layout(
                    barmode='stack',
                    title="معدل الامتثال حسب نوع البيانات",
                    xaxis_title="نوع البيانات",
                    yaxis_title="عدد السجلات"
                )
                
                total = total_open + total_closed
                compliance_rate = (total_closed / total * 100) if total > 0 else 0
                
                response_text = "تحليل الامتثال:\n\n"
                response_text += f"📊 معدل الامتثال الإجمالي: {compliance_rate:.1f}%\n"
                response_text += f"✅ الحالات المغلقة: {total_closed}\n"
                response_text += f"⏳ الحالات المفتوحة: {total_open}\n"

        return response_text, fig, data

    def process_query(self, user_query):
        """Process user query and generate data-driven response with visualizations"""
        user_query = user_query.strip()
        query_lower = user_query.lower()
        
        # Add to conversation history
        self.conversation_history.append({
            'timestamp': datetime.now(),
            'user_query': user_query,
            'response': None
        })
        
        try:
            # First try to analyze the query specifically
            response = self._analyze_data_for_query(user_query)
            
            # If no specific analysis found, try general overview
            if not response and any(word in query_lower for word in ['تصور', 'عام', 'نظرة', 'overview', 'general']):
                # Initialize data for visualization
                data_summary = {
                    'total_records': 0,
                    'closed_count': 0,
                    'open_count': 0,
                    'data_types': {},
                    'departments': {}
                }
                
                # Process each dataset
                for data_type, df in self.unified_data.items():
                    if isinstance(df, pd.DataFrame) and not df.empty:
                        # Count records
                        data_summary['data_types'][data_type] = len(df)
                        data_summary['total_records'] += len(df)
                        
                        # Process status
                        status_col = next((col for col in df.columns 
                                         if any(x in str(col).lower() for x in ['حالة', 'status'])), None)
                        if status_col:
                            closed = df[status_col].str.contains('مغلق|closed', case=False, na=False).sum()
                            data_summary['closed_count'] += closed
                            data_summary['open_count'] += len(df) - closed
                        
                        # Process departments
                        dept_col = next((col for col in df.columns 
                                       if any(x in str(col).lower() for x in ['قطاع', 'إدارة', 'department'])), None)
                        if dept_col:
                            dept_counts = df[dept_col].value_counts()
                            for dept, count in dept_counts.items():
                                if dept in data_summary['departments']:
                                    data_summary['departments'][dept] += count
                                else:
                                    data_summary['departments'][dept] = count
                
                # Create separate figures for better control
                
                # First figure: Data types distribution
                fig1 = go.Figure()
                data_types_values = list(data_summary['data_types'].values())
                data_types_labels = list(data_summary['data_types'].keys())
                
                fig1.add_trace(go.Bar(
                    x=data_types_labels,
                    y=data_types_values,
                    marker_color='#1f77b4',
                    text=data_types_values,
                    textposition='auto',
                ))
                
                fig1.update_layout(
                    title="توزيع البيانات حسب النوع",
                    height=400,
                    showlegend=False,
                    margin=dict(l=50, r=50, t=80, b=50),
                    paper_bgcolor='white',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis_title="نوع البيانات",
                    yaxis_title="عدد السجلات",
                    font=dict(size=14)
                )
                
                # Second figure: Status distribution
                fig2 = None
                if data_summary['closed_count'] + data_summary['open_count'] > 0:
                    fig2 = go.Figure()
                    fig2.add_trace(go.Pie(
                        values=[data_summary['closed_count'], data_summary['open_count']],
                        labels=['مغلق', 'مفتوح'],
                        hole=.4,
                        marker_colors=['#2ecc71', '#e74c3c'],
                        textinfo='label+percent',
                        textposition='inside'
                    ))
                    
                    fig2.update_layout(
                        title="توزيع حالة الملفات",
                        height=400,
                        showlegend=True,
                        margin=dict(l=50, r=50, t=80, b=50),
                        paper_bgcolor='white',
                        font=dict(size=14)
                    )
                
                # Calculate compliance rate
                total_files = data_summary['closed_count'] + data_summary['open_count']
                compliance_rate = (data_summary['closed_count'] / total_files * 100) if total_files > 0 else 0
                
                # Find top department
                top_dept = max(data_summary['departments'].items(), key=lambda x: x[1]) if data_summary['departments'] else None
                
                # Generate response text
                response_text = "نظرة عامة على البيانات:\n\n"
                response_text += f"• يحتوي النظام على إجمالي {data_summary['total_records']:,} سجل عبر جميع أنواع البيانات\n"
                if total_files > 0:
                    response_text += f"• معدل الامتثال الإجمالي هو {compliance_rate:.1f}% ({data_summary['closed_count']:,} مغلق من أصل {total_files:,})\n"
                if top_dept:
                    response_text += f"• القطاع الأكثر نشاطاً هو {top_dept[0]} بـ {top_dept[1]:,} سجل\n"
                
                # Create response with both charts
                charts = []
                if fig1 is not None:
                    charts.append(fig1)
                if fig2 is not None:
                    charts.append(fig2)
                
                # Create response dictionary with proper chart handling
                response = {
                    'text': response_text,
                    'data': pd.DataFrame(list(data_summary['data_types'].items()), 
                                       columns=['نوع البيانات', 'عدد السجلات'])
                }
                
                # Add charts only if we have them
                if len(charts) > 0:
                    response['charts'] = charts
                    # For backward compatibility
                    response['chart'] = charts[0] if len(charts) > 0 else None
            else:
                # For other queries
                query_type = self._classify_query(user_query)
                response = self._generate_response(query_type, user_query)
                
                if not response or not response.get('text'):
                    response = self._analyze_data_for_query(user_query)
                
                if not response or not response.get('text'):
                    # If no specific analysis, use Gemini API with context
                    context = self._prepare_context_for_gemini()
                    gemini_prompt = f"""Based on the following data context:

{context}

Please analyze and answer this question (in Arabic):
{user_query}

Focus on:
1. Direct answer using available data
2. Key statistics and metrics
3. Insights and recommendations

Response MUST be in Arabic and maintain a professional, analytical tone."""
                    
                    gemini_response = self.call_gemini_api(gemini_prompt)
                    response = {
                        'text': gemini_response,
                        'chart': self._generate_relevant_chart(user_query),
                        'data': None
                    }            # Add response to conversation history
            self.conversation_history[-1]['response'] = response
            return response
            
        except Exception as e:
            error_response = {
                'text': f"عذراً، حدث خطأ في معالجة استفسارك: {str(e)}",
                'chart': None,
                'data': None
            }
            self.conversation_history[-1]['response'] = error_response
            return error_response
    
    def _analyze_data_for_query(self, query):
        """Analyze data based on query content"""
        query_lower = query.lower()
        response_text = ""
        charts = []
        data = None
        
        # Define query categories and their keywords
        query_categories = {
            'incidents': ['حوادث', 'حادث', 'accident', 'incident'],
            'risks': ['مخاطر', 'خطر', 'risk', 'hazard'],
            'inspections': ['تفتيش', 'فحص', 'inspection'],
            'compliance': ['امتثال', 'التزام', 'compliance'],
            'performance': ['أداء', 'performance', 'قطاع', 'إدارة'],
            'trends': ['تطور', 'اتجاه', 'trend', 'تغير'],
            'distribution': ['توزيع', 'distribution', 'تقسيم']
        }
        
        # Find relevant datasets based on query
        relevant_data = {}
        for data_type, df in self.unified_data.items():
            if not df.empty:
                # Analyze columns for this dataset
                columns = self._analyze_columns(df)
                if columns:  # If we have analyzable columns
                    relevant_data[data_type] = {
                        'df': df,
                        'columns': columns
                    }
        
        # For general data overview
        if any(word in query_lower for word in ['عام', 'تصور', 'نظرة', 'overview', 'general']):
            all_stats = {
                'total_records': 0,
                'open_cases': 0,
                'closed_cases': 0,
                'types_distribution': {},
                'dept_stats': {}
            }
            
            for data_type, df in self.unified_data.items():
                if isinstance(df, pd.DataFrame) and not df.empty:
                    # Basic counts
                    all_stats['types_distribution'][data_type] = len(df)
                    all_stats['total_records'] += len(df)
                    
                    # Status analysis
                    status_col = next((col for col in df.columns 
                                     if any(x in str(col).lower() for x in ['حالة', 'status'])), None)
                    if status_col:
                        closed = df[status_col].str.contains('مغلق|closed', case=False, na=False).sum()
                        all_stats['closed_cases'] += closed
                        all_stats['open_cases'] += (len(df) - closed)
                    
                    # Department analysis
                    dept_col = next((col for col in df.columns 
                                   if any(x in str(col).lower() for x in ['إدارة', 'قطاع', 'department'])), None)
                    if dept_col:
                        dept_counts = df[dept_col].value_counts()
                        for dept, count in dept_counts.items():
                            if dept not in all_stats['dept_stats']:
                                all_stats['dept_stats'][dept] = 0
                            all_stats['dept_stats'][dept] += count
            
            if all_stats['total_records'] > 0:
                # Create main visualization
                fig = go.Figure()
                
                # Types distribution
                fig.add_trace(go.Bar(
                    name='توزيع البيانات',
                    x=list(all_stats['types_distribution'].keys()),
                    y=list(all_stats['types_distribution'].values()),
                    text=list(all_stats['types_distribution'].values()),
                    textposition='auto',
                ))
                
                # Status overview if available
                if all_stats['open_cases'] + all_stats['closed_cases'] > 0:
                    fig.add_trace(go.Pie(
                        values=[all_stats['open_cases'], all_stats['closed_cases']],
                        labels=['مفتوح', 'مغلق'],
                        domain={'x': [0.7, 1], 'y': [0, 1]},
                        name='حالة الملفات',
                        hole=.4,
                        textinfo='percent+label'
                    ))
                
                fig.update_layout(
                    title="نظرة عامة على البيانات",
                    showlegend=True,
                    height=500,
                    grid={'rows': 1, 'columns': 2},
                    annotations=[
                        dict(text="توزيع البيانات", x=0.25, y=1.1, showarrow=False, font_size=16),
                        dict(text="حالة الملفات", x=0.85, y=1.1, showarrow=False, font_size=16)
                    ]
                )
                
                # Generate response text
                response_text = f"""نظرة عامة على البيانات:

📊 إجمالي السجلات: {all_stats['total_records']:,}

حالة الملفات:
✅ مغلق: {all_stats['closed_cases']:,}
⏳ مفتوح: {all_stats['open_cases']:,}

توزيع البيانات:"""
                
                for data_type, count in all_stats['types_distribution'].items():
                    response_text += f"\n• {data_type}: {count:,} سجل"
                
                if all_stats['dept_stats']:
                    response_text += "\n\nأعلى القطاعات نشاطاً:"
                    top_depts = sorted(all_stats['dept_stats'].items(), key=lambda x: x[1], reverse=True)[:3]
                    for dept, count in top_depts:
                        response_text += f"\n• {dept}: {count:,} سجل"
                
                data = pd.DataFrame({
                    'نوع البيانات': list(all_stats['types_distribution'].keys()),
                    'عدد السجلات': list(all_stats['types_distribution'].values()),
                    'النسبة': [f"{(v/all_stats['total_records'])*100:.1f}%" 
                              for v in all_stats['types_distribution'].values()]
                })
                
                return {
                    'text': response_text,
                    'chart': fig,
                    'data': data
                }
        
        # Check different aspects of the query
        elif any(word in query_lower for word in ['حوادث', 'حادث', 'آخر', 'incident']):
            for data_type, df in self.unified_data.items():
                if 'حوادث' in str(data_type) and not df.empty:
                    date_col = next((col for col in df.columns 
                                   if any(x in str(col).lower() for x in ['تاريخ', 'date'])), None)
                    
                    if date_col:
                        try:
                            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                            latest = df.sort_values(date_col, ascending=False).head(5)
                            
                            monthly_counts = df.groupby(df[date_col].dt.strftime('%Y-%m'))[date_col].count()
                            
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=monthly_counts.index,
                                y=monthly_counts.values,
                                mode='lines+markers',
                                name='عدد الحوادث الشهري'
                            ))
                            
                            fig.update_layout(
                                title="توزيع الحوادث الشهري",
                                xaxis_title="الشهر",
                                yaxis_title="عدد الحوادث"
                            )
                            
                            response_text = f"تحليل بيانات الحوادث:\n\n"
                            response_text += f"📊 إجمالي عدد الحوادث: {len(df)}\n"
                            response_text += f"📅 آخر تحديث: {latest[date_col].iloc[0].strftime('%Y-%m-%d')}\n\n"
                            
                            desc_col = next((col for col in df.columns 
                                           if any(x in str(col).lower() for x in ['وصف', 'description'])), None)
                            
                            if desc_col:
                                response_text += "آخر 5 حوادث:\n"
                                for _, row in latest.iterrows():
                                    response_text += f"\n📌 {row[date_col].strftime('%Y-%m-%d')}: {row[desc_col]}"
                            
                            data = latest
                            break
                        except Exception as e:
                            continue
        
        elif any(word in query_lower for word in ['مخاطر', 'خطر', 'risk']):
            for data_type, df in self.unified_data.items():
                if 'مخاطر' in str(data_type) and not df.empty:
                    risk_col = next((col for col in df.columns 
                                   if any(x in str(col).lower() for x in ['مستوى', 'تصنيف', 'level'])), None)
                    
                    if risk_col:
                        risk_counts = df[risk_col].value_counts()
                        
                        fig = px.pie(
                            values=risk_counts.values,
                            names=risk_counts.index,
                            title="توزيع مستويات المخاطر"
                        )
                        
                        response_text = "تحليل المخاطر:\n\n"
                        response_text += f"📊 إجمالي عدد المخاطر: {len(df)}\n\n"
                        response_text += "توزيع المخاطر حسب المستوى:\n"
                        for level, count in risk_counts.items():
                            response_text += f"• {level}: {count} ({count/len(df)*100:.1f}%)\n"
                        
                        data = df
                        break
        
        elif any(word in query_lower for word in ['امتثال', 'compliance']):
            total_open = 0
            total_closed = 0
            compliance_data = {}
            
            for data_type, df in self.unified_data.items():
                if df.empty:
                    continue
                
                status_col = next((col for col in df.columns 
                                 if any(x in str(col).lower() for x in ['حالة', 'status'])), None)
                
                if status_col:
                    closed = df[status_col].str.contains('مغلق|closed', case=False, na=False).sum()
                    opened = len(df) - closed
                    total_closed += closed
                    total_open += opened
                    compliance_data[data_type] = {'مغلق': closed, 'مفتوح': opened}
            
            if compliance_data:
                fig = go.Figure()
                for status in ['مغلق', 'مفتوح']:
                    values = [data[status] for data in compliance_data.values()]
                    fig.add_trace(go.Bar(
                        name=status,
                        x=list(compliance_data.keys()),
                        y=values
                    ))
                
                fig.update_layout(
                    barmode='stack',
                    title="معدل الامتثال حسب نوع البيانات",
                    xaxis_title="نوع البيانات",
                    yaxis_title="عدد السجلات"
                )
                
                total = total_open + total_closed
                compliance_rate = (total_closed / total * 100) if total > 0 else 0
                
                response_text = "تحليل الامتثال:\n\n"
                response_text += f"📊 معدل الامتثال الإجمالي: {compliance_rate:.1f}%\n"
                response_text += f"✅ الحالات المغلقة: {total_closed}\n"
                response_text += f"⏳ الحالات المفتوحة: {total_open}\n\n"
                response_text += "التفصيل حسب نوع البيانات:\n"
                
                for data_type, counts in compliance_data.items():
                    total = counts['مغلق'] + counts['مفتوح']
                    rate = (counts['مغلق'] / total * 100) if total > 0 else 0
                    response_text += f"\n• {data_type}:"
                    response_text += f"\n  - معدل الامتثال: {rate:.1f}%"
                    response_text += f"\n  - مغلق: {counts['مغلق']}"
                    response_text += f"\n  - مفتوح: {counts['مفتوح']}"
        
        return {
            'text': response_text,
            'chart': fig,
            'data': data
        } if response_text else None
    
    def _generate_relevant_chart(self, query):
        """Generate a relevant chart based on the query context"""
        query_lower = query.lower()
        
        try:
            # For time-based queries
            if any(word in query_lower for word in ['متى', 'تاريخ', 'شهر', 'سنة', 'when', 'date', 'month', 'year']):
                relevant_data = None
                date_col = None
                
                # Find most relevant dataset with dates
                for data_type, df in self.unified_data.items():
                    if df.empty:
                        continue
                        
                    for col in df.columns:
                        if any(x in str(col).lower() for x in ['تاريخ', 'date']):
                            relevant_data = df
                            date_col = col
                            break
                    if relevant_data is not None:
                        break
                
                if relevant_data is not None and date_col:
                    try:
                        relevant_data[date_col] = pd.to_datetime(relevant_data[date_col], errors='coerce')
                        monthly_counts = relevant_data.groupby(relevant_data[date_col].dt.strftime('%Y-%m')).size()
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=monthly_counts.index,
                            y=monthly_counts.values,
                            mode='lines+markers',
                            name='التوزيع الشهري'
                        ))
                        
                        fig.update_layout(
                            title="التوزيع الزمني للبيانات",
                            xaxis_title="الشهر",
                            yaxis_title="العدد"
                        )
                        
                        return fig
                    except:
                        pass
            
            # For comparison queries
            elif any(word in query_lower for word in ['مقارنة', 'compare', 'versus', 'vs']):
                data_counts = {data_type: len(df) for data_type, df in self.unified_data.items() if not df.empty}
                
                if data_counts:
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=list(data_counts.keys()),
                        y=list(data_counts.values())
                    ))
                    
                    fig.update_layout(
                        title="مقارنة حجم البيانات",
                        xaxis_title="نوع البيانات",
                        yaxis_title="عدد السجلات"
                    )
                    
                    return fig
            
            # For distribution queries
            elif any(word in query_lower for word in ['توزيع', 'distribution']):
                for data_type, df in self.unified_data.items():
                    if df.empty:
                        continue
                    
                    categorical_cols = df.select_dtypes(include=['object']).columns
                    for col in categorical_cols:
                        if len(df[col].unique()) <= 10:  # Only for columns with reasonable number of categories
                            value_counts = df[col].value_counts()
                            
                            fig = px.pie(
                                values=value_counts.values,
                                names=value_counts.index,
                                title=f"توزيع {col}"
                            )
                            
                            return fig
                            break
                    break
        
        except Exception:
            pass
        
        return None
    
    def _classify_query(self, query):
        """Classify user query into categories"""
        query_lower = query.lower()
        
        # Initial classification from query patterns
        for category, patterns in self.query_patterns.items():
            for pattern in patterns:
                if pattern.lower() in query_lower:
                    return category
        
        # Enhanced classification based on topic analysis
        if any(word in query_lower for word in ['حوادث', 'حادث', 'incident', 'accidents']):
            return 'total_incidents'
        elif any(word in query_lower for word in ['مفتوح', 'جاري', 'قيد التنفيذ', 'open', 'pending']):
            return 'open_cases'
        elif any(word in query_lower for word in ['مغلق', 'منتهي', 'تم', 'closed', 'done']):
            return 'closed_cases'
        elif any(word in query_lower for word in ['قطاع', 'إدارة', 'أداء', 'department', 'performance']):
            return 'department_performance'
        elif any(word in query_lower for word in ['مخاطر', 'خطر', 'risk', 'hazard']):
            return 'risk_assessment'
        elif any(word in query_lower for word in ['امتثال', 'التزام', 'compliance']):
            return 'compliance_rate'
        elif any(word in query_lower for word in ['اتجاه', 'تطور', 'trend', 'progress']):
            return 'trends'
        elif any(word in query_lower for word in ['إحصاء', 'عدد', 'كم', 'statistics', 'count']):
            return 'statistics'
        
        # Fallback classification
        return 'general'
    
    def _generate_response(self, query_type, user_query):
        """Generate response based on query type"""
        try:
            if query_type == 'total_incidents':
                return self._get_incidents_summary()
            elif query_type == 'open_cases':
                return self._get_open_cases_summary()
            elif query_type == 'closed_cases':
                return self._get_closed_cases_summary()
            elif query_type == 'department_performance':
                return self._get_department_performance()
            elif query_type == 'risk_assessment':
                return self._get_risk_assessment_summary()
            elif query_type == 'compliance_rate':
                return self._get_compliance_summary()
            elif query_type == 'trends':
                return self._get_trends_summary()
            elif query_type == 'statistics':
                return self._get_general_statistics()
            else:
                return self._get_general_response(user_query)
        except Exception as e:
            return {
                'text': f"عذراً، حدث خطأ في معالجة استفسارك: {str(e)}",
                'chart': None,
                'data': None
            }
    
    def _get_incidents_summary(self):
        """Get incidents summary"""
        # Find incidents data in any of the datasets
        incidents_data = None
        for data_type, df in self.unified_data.items():
            if any(x in str(data_type).lower() for x in ['حوادث', 'incidents']) and not df.empty:
                incidents_data = df
                break
                
        if incidents_data is None:
            return {
                'text': "لا توجد بيانات حوادث متاحة في النظام حالياً.",
                'charts': None,
                'data': None
            }
        
        incidents_df = self.unified_data['incidents']
        total_incidents = len(incidents_df)
        
        # Get status distribution
        status_dist = {}
        for col in incidents_df.columns:
            if any(keyword in col.lower() for keyword in ['حالة', 'status']):
                status_dist = incidents_df[col].value_counts().to_dict()
                break
        
        # Create chart
        if status_dist:
            chart_data = pd.DataFrame([
                {'الحالة': status, 'العدد': count}
                for status, count in status_dist.items()
            ])
            
            fig = px.pie(
                chart_data,
                values='العدد',
                names='الحالة',
                title="توزيع حالات الحوادث"
            )
        else:
            fig = None
        
        text = f"إجمالي الحوادث المسجلة: {total_incidents:,} حادث\n"
        if status_dist:
            text += "توزيع الحالات:\n"
            for status, count in status_dist.items():
                text += f"• {status}: {count:,} حادث\n"
        
        return {
            'text': text,
            'chart': fig,
            'data': incidents_df.head(10)
        }
    
    def _get_open_cases_summary(self):
        """Get open cases summary"""
        open_cases = {}
        total_open = 0
        
        for data_type, df in self.unified_data.items():
            if df.empty:
                continue
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['حالة', 'status']):
                    open_count = len(df[df[col].str.contains('مفتوح', na=False)])
                    if open_count > 0:
                        open_cases[data_type] = open_count
                        total_open += open_count
                    break
        
        if not open_cases:
            return {
                'text': "لا توجد حالات مفتوحة في النظام حالياً.",
                'chart': None,
                'data': None
            }
        
        # Create chart
        chart_data = pd.DataFrame([
            {'نوع البيانات': data_type, 'الحالات المفتوحة': count}
            for data_type, count in open_cases.items()
        ])
        
        fig = px.bar(
            chart_data,
            x='نوع البيانات',
            y='الحالات المفتوحة',
            title="الحالات المفتوحة حسب نوع البيانات"
        )
        
        text = f"إجمالي الحالات المفتوحة: {total_open:,}\n"
        text += "التوزيع حسب نوع البيانات:\n"
        for data_type, count in open_cases.items():
            text += f"• {data_type}: {count:,} حالة مفتوحة\n"
        
        return {
            'text': text,
            'chart': fig,
            'data': chart_data
        }
    
    def _get_closed_cases_summary(self):
        """Get closed cases summary"""
        closed_cases = {}
        total_closed = 0
        
        for data_type, df in self.unified_data.items():
            if df.empty:
                continue
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['حالة', 'status']):
                    closed_count = len(df[df[col].str.contains('مغلق', na=False)])
                    if closed_count > 0:
                        closed_cases[data_type] = closed_count
                        total_closed += closed_count
                    break
        
        if not closed_cases:
            return {
                'text': "لا توجد حالات مغلقة في النظام حالياً.",
                'chart': None,
                'data': None
            }
        
        # Create chart
        chart_data = pd.DataFrame([
            {'نوع البيانات': data_type, 'الحالات المغلقة': count}
            for data_type, count in closed_cases.items()
        ])
        
        fig = px.bar(
            chart_data,
            x='نوع البيانات',
            y='الحالات المغلقة',
            title="الحالات المغلقة حسب نوع البيانات",
            color_discrete_sequence=['#2ca02c']
        )
        
        text = f"إجمالي الحالات المغلقة: {total_closed:,}\n"
        text += "التوزيع حسب نوع البيانات:\n"
        for data_type, count in closed_cases.items():
            text += f"• {data_type}: {count:,} حالة مغلقة\n"
        
        return {
            'text': text,
            'chart': fig,
            'data': chart_data
        }
    
    def _get_department_performance(self):
        """Get department performance analysis"""
        dept_performance = {}
        
        for data_type, df in self.unified_data.items():
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
                        dept_performance[dept] = {'total': 0, 'closed': 0, 'rates': []}
                    
                    dept_performance[dept]['total'] += total
                    dept_performance[dept]['closed'] += closed
                    dept_performance[dept]['rates'].append(compliance_rate)
        
        if not dept_performance:
            return {
                'text': "لا توجد بيانات أداء القطاعات متاحة.",
                'chart': None,
                'data': None
            }
        
        # Calculate average performance
        performance_data = []
        for dept, data in dept_performance.items():
            avg_rate = np.mean(data['rates']) if data['rates'] else 0
            performance_data.append({
                'القطاع': dept,
                'معدل الامتثال': avg_rate,
                'إجمالي الحالات': data['total'],
                'الحالات المغلقة': data['closed']
            })
        
        performance_df = pd.DataFrame(performance_data)
        performance_df = performance_df.sort_values('معدل الامتثال', ascending=False)
        
        # Create chart
        fig = px.bar(
            performance_df.head(10),
            x='القطاع',
            y='معدل الامتثال',
            title="أداء القطاعات - معدل الامتثال",
            color='معدل الامتثال',
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(xaxis_tickangle=-45)
        
        # Generate text summary
        best_dept = performance_df.iloc[0]
        worst_dept = performance_df.iloc[-1]
        
        text = f"تحليل أداء القطاعات:\n\n"
        text += f"أفضل قطاع: {best_dept['القطاع']} بمعدل امتثال {best_dept['معدل الامتثال']:.1f}%\n"
        text += f"أضعف قطاع: {worst_dept['القطاع']} بمعدل امتثال {worst_dept['معدل الامتثال']:.1f}%\n\n"
        text += f"متوسط معدل الامتثال العام: {performance_df['معدل الامتثال'].mean():.1f}%"
        
        return {
            'text': text,
            'chart': fig,
            'data': performance_df
        }
    
    def _get_risk_assessment_summary(self):
        """Get risk assessment summary"""
        if 'risk_assessments' not in self.unified_data or self.unified_data['risk_assessments'].empty:
            return {
                'text': "لا توجد بيانات تقييم المخاطر متاحة في النظام حالياً.",
                'chart': None,
                'data': None
            }
        
        risk_df = self.unified_data['risk_assessments']
        total_assessments = len(risk_df)
        
        # Get risk level distribution
        risk_levels = {'عالي': 0, 'متوسط': 0, 'منخفض': 0}
        
        for col in risk_df.columns:
            if any(keyword in col.lower() for keyword in ['تصنيف', 'مخاطر', 'risk']):
                level_counts = risk_df[col].value_counts()
                for level, count in level_counts.items():
                    level_str = str(level).lower()
                    if 'عالي' in level_str or 'high' in level_str:
                        risk_levels['عالي'] += count
                    elif 'متوسط' in level_str or 'medium' in level_str:
                        risk_levels['متوسط'] += count
                    elif 'منخفض' in level_str or 'low' in level_str:
                        risk_levels['منخفض'] += count
                break
        
        # Create chart
        chart_data = pd.DataFrame([
            {'مستوى المخاطر': level, 'العدد': count}
            for level, count in risk_levels.items() if count > 0
        ])
        
        if not chart_data.empty:
            fig = px.pie(
                chart_data,
                values='العدد',
                names='مستوى المخاطر',
                title="توزيع مستويات المخاطر",
                color_discrete_map={
                    'عالي': '#d62728',
                    'متوسط': '#ff7f0e',
                    'منخفض': '#2ca02c'
                }
            )
        else:
            fig = None
        
        text = f"ملخص تقييم المخاطر:\n\n"
        text += f"إجمالي التقييمات: {total_assessments:,}\n"
        if any(risk_levels.values()):
            text += "توزيع مستويات المخاطر:\n"
            for level, count in risk_levels.items():
                if count > 0:
                    percentage = (count / sum(risk_levels.values())) * 100
                    text += f"• {level}: {count:,} ({percentage:.1f}%)\n"
        
        return {
            'text': text,
            'chart': fig,
            'data': risk_df.head(10)
        }
    
    def _get_compliance_summary(self):
        """Get overall compliance summary"""
        total_open = 0
        total_closed = 0
        compliance_by_type = {}
        
        for data_type, df in self.unified_data.items():
            if df.empty:
                continue
            
            type_open = 0
            type_closed = 0
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['حالة', 'status']):
                    status_counts = df[col].value_counts()
                    for status, count in status_counts.items():
                        if 'مفتوح' in str(status):
                            type_open += count
                            total_open += count
                        elif 'مغلق' in str(status):
                            type_closed += count
                            total_closed += count
                    break
            
            if type_open + type_closed > 0:
                compliance_rate = (type_closed / (type_open + type_closed)) * 100
                compliance_by_type[data_type] = {
                    'rate': compliance_rate,
                    'closed': type_closed,
                    'total': type_open + type_closed
                }
        
        if total_open + total_closed == 0:
            return {
                'text': "لا توجد بيانات كافية لحساب معدل الامتثال.",
                'chart': None,
                'data': None
            }
        
        overall_compliance = (total_closed / (total_open + total_closed)) * 100
        
        # Create chart
        chart_data = pd.DataFrame([
            {'نوع البيانات': data_type, 'معدل الامتثال': data['rate']}
            for data_type, data in compliance_by_type.items()
        ])
        
        fig = px.bar(
            chart_data,
            x='نوع البيانات',
            y='معدل الامتثال',
            title="معدل الامتثال حسب نوع البيانات",
            color='معدل الامتثال',
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(xaxis_tickangle=-45)
        
        text = f"ملخص الامتثال العام:\n\n"
        text += f"معدل الامتثال الإجمالي: {overall_compliance:.1f}%\n"
        text += f"إجمالي الحالات: {total_open + total_closed:,}\n"
        text += f"الحالات المغلقة: {total_closed:,}\n"
        text += f"الحالات المفتوحة: {total_open:,}\n\n"
        text += "معدل الامتثال حسب نوع البيانات:\n"
        
        for data_type, data in compliance_by_type.items():
            text += f"• {data_type}: {data['rate']:.1f}% ({data['closed']}/{data['total']})\n"
        
        return {
            'text': text,
            'chart': fig,
            'data': chart_data
        }
    
    def _get_trends_summary(self):
        """Get trends analysis"""
        trends_data = {}
        
        for data_type, df in self.unified_data.items():
            if df.empty:
                continue
            
            date_col = None
            for col in df.columns:
                if df[col].dtype == 'datetime64[ns]':
                    date_col = col
                    break
            
            if date_col:
                monthly_trend = df.groupby(pd.Grouper(key=date_col, freq='M')).size()
                if len(monthly_trend) > 1:
                    trends_data[data_type] = monthly_trend
        
        if not trends_data:
            return {
                'text': "لا توجد بيانات كافية لتحليل الاتجاهات الزمنية.",
                'chart': None,
                'data': None
            }
        
        # Create combined trends chart
        fig = go.Figure()
        
        for data_type, trend in trends_data.items():
            fig.add_trace(go.Scatter(
                x=trend.index,
                y=trend.values,
                mode='lines+markers',
                name=data_type,
                line=dict(width=2)
            ))
        
        fig.update_layout(
            title="الاتجاهات الزمنية للبيانات",
            xaxis_title="التاريخ",
            yaxis_title="عدد السجلات",
            hovermode='x unified'
        )
        
        text = "تحليل الاتجاهات الزمنية:\n\n"
        
        for data_type, trend in trends_data.items():
            latest_value = trend.iloc[-1]
            previous_value = trend.iloc[-2] if len(trend) > 1 else latest_value
            change = ((latest_value - previous_value) / previous_value * 100) if previous_value != 0 else 0
            
            text += f"• {data_type}:\n"
            text += f"  - القيمة الحالية: {latest_value:,}\n"
            text += f"  - التغيير: {change:+.1f}% من الشهر السابق\n\n"
        
        return {
            'text': text,
            'chart': fig,
            'data': None
        }
    
    def _get_general_statistics(self):
        """Get general statistics"""
        stats = {
            'total_records': 0,
            'data_types': len(self.unified_data),
            'date_ranges': {},
            'top_departments': {},
            'status_summary': {'مفتوح': 0, 'مغلق': 0}
        }
        
        for data_type, df in self.unified_data.items():
            if df.empty:
                continue
            
            stats['total_records'] += len(df)
            
            # Get date range
            date_range = self._get_date_range(df)
            if date_range:
                stats['date_ranges'][data_type] = date_range
            
            # Get department info
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['إدارة', 'قطاع', 'department']):
                    dept_counts = df[col].value_counts().head(3)
                    stats['top_departments'][data_type] = dept_counts.to_dict()
                    break
            
            # Get status info
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['حالة', 'status']):
                    status_counts = df[col].value_counts()
                    for status, count in status_counts.items():
                        if 'مفتوح' in str(status):
                            stats['status_summary']['مفتوح'] += count
                        elif 'مغلق' in str(status):
                            stats['status_summary']['مغلق'] += count
                    break
        
        text = f"الإحصائيات العامة للنظام:\n\n"
        text += f"إجمالي السجلات: {stats['total_records']:,}\n"
        text += f"أنواع البيانات: {stats['data_types']}\n"
        text += f"الحالات المفتوحة: {stats['status_summary']['مفتوح']:,}\n"
        text += f"الحالات المغلقة: {stats['status_summary']['مغلق']:,}\n\n"
        
        if stats['date_ranges']:
            text += "النطاقات الزمنية:\n"
            for data_type, date_range in stats['date_ranges'].items():
                text += f"• {data_type}: من {date_range['start']} إلى {date_range['end']} ({date_range['days']} يوم)\n"
        
        return {
            'text': text,
            'chart': None,
            'data': None
        }
    
    def _get_general_response(self, user_query):
        """Get general response for unclassified queries"""
        query_lower = user_query.lower()
        
        # If it's a general overview query
        if any(word in query_lower for word in ['تصور', 'عام', 'نظرة', 'overview']):
            # Initialize data summaries
            data_summary = {
                'total_records': 0,
                'open_cases': 0,
                'closed_cases': 0,
                'data_types': {},
                'departments': {}
            }
            
            # Process each dataset
            for data_type, df in self.unified_data.items():
                if isinstance(df, pd.DataFrame) and not df.empty:
                    # Count records
                    data_summary['data_types'][data_type] = len(df)
                    data_summary['total_records'] += len(df)
                    
                    # Process status
                    status_col = next((col for col in df.columns 
                                     if any(x in str(col).lower() for x in ['حالة', 'status'])), None)
                    if status_col:
                        closed = df[status_col].str.contains('مغلق|closed', case=False, na=False).sum()
                        data_summary['closed_cases'] += closed
                        data_summary['open_cases'] += len(df) - closed
                    
                    # Process departments
                    dept_col = next((col for col in df.columns 
                                   if any(x in str(col).lower() for x in ['إدارة', 'قطاع', 'department'])), None)
                    if dept_col:
                        for dept, count in df[dept_col].value_counts().items():
                            data_summary['departments'][dept] = data_summary['departments'].get(dept, 0) + count
            
            # Create visualizations
            charts = []
            
            # Data types distribution
            if data_summary['data_types']:
                fig1 = go.Figure(data=[
                    go.Bar(
                        x=list(data_summary['data_types'].keys()),
                        y=list(data_summary['data_types'].values()),
                        text=list(data_summary['data_types'].values()),
                        textposition='auto',
                    )
                ])
                fig1.update_layout(
                    title="توزيع البيانات حسب النوع",
                    xaxis_title="نوع البيانات",
                    yaxis_title="عدد السجلات",
                    template="plotly_white"
                )
                charts.append(fig1)
            
            # Cases status
            if data_summary['open_cases'] + data_summary['closed_cases'] > 0:
                fig2 = go.Figure(data=[
                    go.Pie(
                        labels=['مفتوح', 'مغلق'],
                        values=[data_summary['open_cases'], data_summary['closed_cases']],
                        hole=.3
                    )
                ])
                fig2.update_layout(
                    title="توزيع حالة الملفات",
                    template="plotly_white"
                )
                charts.append(fig2)
            
            # Generate response text
            total_cases = data_summary['open_cases'] + data_summary['closed_cases']
            compliance_rate = (data_summary['closed_cases'] / total_cases * 100) if total_cases > 0 else 0
            
            # Find top department
            top_dept = max(data_summary['departments'].items(), key=lambda x: x[1]) if data_summary['departments'] else None
            
            text = "نظرة عامة على البيانات:\n\n"
            text += f"• يحتوي النظام على إجمالي {data_summary['total_records']:,} سجل عبر جميع أنواع البيانات\n"
            
            if total_cases > 0:
                text += f"• معدل الامتثال الإجمالي هو {compliance_rate:.1f}% ({data_summary['closed_cases']:,} مغلق من أصل {total_cases:,})\n"
            
            if top_dept:
                text += f"• القطاع الأكثر نشاطاً هو {top_dept[0]} بـ {top_dept[1]:,} سجل\n"
            
                # Create detailed data for display
                display_data = pd.DataFrame({
                    'نوع البيانات': list(data_summary['data_types'].keys()),
                    'عدد السجلات': list(data_summary['data_types'].values()),
                    'النسبة': [f"{(v/data_summary['total_records'])*100:.1f}%" 
                          for v in data_summary['data_types'].values()]
                })
                
                # Generate additional analysis based on available columns
                extra_charts = []
                for data_type, df in self.unified_data.items():
                    if isinstance(df, pd.DataFrame) and not df.empty:
                        # Analyze columns
                        columns = self._analyze_columns(df)
                        
                        # Add relevant visualizations
                        if columns['numeric_columns'] and len(columns['numeric_columns']) >= 2:
                            # Create correlation heatmap for numeric columns
                            numeric_data = df[columns['numeric_columns']].corr()
                            fig = go.Figure(data=go.Heatmap(
                                z=numeric_data.values,
                                x=numeric_data.columns,
                                y=numeric_data.columns,
                                colorscale='RdBu'
                            ))
                            fig.update_layout(
                                title=f"مصفوفة الارتباط - {data_type}",
                                template="plotly_white"
                            )
                            extra_charts.append(fig)
                        
                        if columns['date_columns'] and columns['numeric_columns']:
                            # Create time series analysis
                            date_col = columns['date_columns'][0]
                            metric_col = columns['numeric_columns'][0]
                            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                            monthly_data = df.groupby(df[date_col].dt.strftime('%Y-%m'))[metric_col].mean()
                            
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=monthly_data.index,
                                y=monthly_data.values,
                                mode='lines+markers',
                                name=metric_col
                            ))
                            fig.update_layout(
                                title=f"تطور {metric_col} عبر الزمن - {data_type}",
                                xaxis_title="الشهر",
                                yaxis_title=metric_col,
                                template="plotly_white"
                            )
                            extra_charts.append(fig)
                
                if extra_charts:
                    charts.extend(extra_charts)
            
            return {
                'text': text,
                'charts': charts if charts else None,
                'data': display_data
            }        # For help queries
        elif any(word in query_lower for word in ['مساعدة', 'help']):
            return {
                'text': """يمكنني مساعدتك في الاستفسار عن:

• إجمالي الحوادث والملاحظات
• الحالات المفتوحة والمغلقة
• أداء القطاعات المختلفة
• تقييمات المخاطر
• معدلات الامتثال
• الاتجاهات الزمنية
• الإحصائيات العامة

مثال على الأسئلة:
- "كم عدد الحوادث المفتوحة؟"
- "ما هو أداء قطاع المشاريع؟"
- "أظهر لي اتجاه الملاحظات"
- "ما هو معدل الامتثال؟"
""",
                'charts': None,
                'data': None
            }
        
        # Default response
        else:
            # Provide insights from knowledge base
            insights_text = "إليك بعض الرؤى من البيانات:\n\n"
            for insight in self.knowledge_base['insights'][:3]:
                insights_text += f"• {insight}\n"
            
            insights_text += "\nيمكنك طرح أسئلة أكثر تحديداً للحصول على تحليل مفصل."
            
            return {
                'text': insights_text,
                'charts': None,
                'data': None
            }
    
    def get_conversation_history(self):
        """Get conversation history"""
        return self.conversation_history
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def export_conversation(self):
        """Export conversation history"""
        if not self.conversation_history:
            return None
        
        conversation_data = []
        for entry in self.conversation_history:
            conversation_data.append({
                'timestamp': entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'user_query': entry['user_query'],
                'response_text': entry['response']['text'] if entry['response'] else None
            })
        
        return pd.DataFrame(conversation_data)

def create_chatbot_interface(unified_data, kpi_data):
    """Create interactive chatbot interface in Streamlit"""
    # Apply custom CSS for better visual presentation
    st.markdown("""
    <style>
    .chat-container { 
        padding: 1rem; 
        border-radius: 0.5rem; 
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .user-message { 
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .bot-message { 
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .chat-meta { 
        font-size: 0.8rem; 
        color: #666;
        margin-top: 0.25rem;
    }
    div[data-testid="stPlotlyChart"] {
        margin: 1rem 0;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        background-color: white;
        padding: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.subheader("🤖 مساعد الذكاء الاصطناعي")
    
    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = GeminiChatbot(unified_data, kpi_data)
    
    # Initialize chat interface
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        
        # Add enhanced welcome message
        welcome_message = {
            "role": "assistant",
            "content": """مرحباً! أنا مساعدك الذكي لتحليل بيانات السلامة والامتثال. يمكنني مساعدتك في:

• تحليل الحوادث وآخر المستجدات
• مراقبة معدلات الامتثال والإغلاق
• تقييم المخاطر وتوزيعها
• إنشاء تقارير إحصائية
• عرض الرسوم البيانية والتوزيعات

ما الذي تريد تحليله اليوم؟""",
            "chart": None,
            "data": None
        }
        st.session_state.messages.append(welcome_message)
    
    # Display chat messages with enhanced visualization handling
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Display message content
            st.markdown(message["content"])
            
            # Handle chart display with error checking
            if message.get("charts") is not None:
                try:
                    charts = message["charts"]
                    if isinstance(charts, list) and len(charts) > 0:
                        for chart in charts:
                            if isinstance(chart, go.Figure):
                                # Update layout for better visibility
                                chart.update_layout(
                                    template="plotly_white",
                                    paper_bgcolor="rgba(0,0,0,0)",
                                    plot_bgcolor="rgba(0,0,0,0)",
                                    margin=dict(l=20, r=20, t=40, b=20),
                                )
                                # Display chart
                                st.plotly_chart(chart, use_container_width=True, config={'displayModeBar': True})
                except Exception as e:
                    st.error(f"عذراً، حدث خطأ في عرض الرسم البياني: {str(e)}")
            # For backward compatibility
            elif message.get("chart") is not None:
                try:
                    chart = message["chart"]
                    if isinstance(chart, go.Figure):
                        chart.update_layout(
                            template="plotly_white",
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            margin=dict(l=20, r=20, t=40, b=20),
                        )
                        st.plotly_chart(chart, use_container_width=True, config={'displayModeBar': True})
                except Exception as e:
                    st.error(f"عذراً، حدث خطأ في عرض الرسم البياني: {str(e)}")
            
            # Handle data display with error checking
            if message.get("data") is not None:
                try:
                    with st.expander("📊 عرض البيانات التفصيلية"):
                        st.dataframe(
                            message["data"],
                            use_container_width=True,
                            height=300,
                            hide_index=True
                        )
                except Exception as e:
                    st.error(f"عذراً، حدث خطأ في عرض البيانات: {str(e)}")
    
    # Chat input
    if prompt := st.chat_input("اسألني عن تحليل البيانات..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("جاري تحليل البيانات..."):
                response = st.session_state.chatbot.process_query(prompt)
            
            st.markdown(response['text'])
            
            # Handle charts display
            if 'charts' in response and response['charts']:
                for chart in response['charts']:
                    if isinstance(chart, go.Figure):
                        st.plotly_chart(chart, use_container_width=True)
            elif 'chart' in response and response['chart']:
                if isinstance(response['chart'], go.Figure):
                    st.plotly_chart(response['chart'], use_container_width=True)
            
            # Handle data display
            if response.get('data') is not None:
                with st.expander("عرض البيانات التفصيلية"):
                    st.dataframe(response['data'])
            
            # Add assistant response to chat history
            message = {
                "role": "assistant",
                "content": response['text'],
                "data": response.get('data')
            }
            
            # Handle charts in message
            if 'charts' in response and response['charts']:
                message['charts'] = response['charts']
            elif 'chart' in response and response['chart']:
                message['chart'] = response['chart']
            
            # Add message to chat history
            st.session_state.messages.append(message)    
            
            # Sidebar controls
    with st.sidebar:
        st.markdown("### ⚙️ إعدادات المحادثة")
        
        if st.button("🗑️ مسح المحادثة"):
            st.session_state.messages = []
            st.session_state.chatbot.conversation_history = []
            st.rerun()
        
        st.markdown("### 💡 اقتراحات للتحليل")
        suggestions = [
            "آخر الحوادث المسجلة",
            "تحليل معدل الامتثال",
            "توزيع المخاطر",
            "الإحصائيات العامة"
        ]
        
        for suggestion in suggestions:
            if st.button(suggestion, key=f"suggest_{suggestion}"):
                # Simulate clicking the suggestion
                st.session_state.messages.append({"role": "user", "content": suggestion})
                
                with st.spinner("جاري التحليل..."):
                    response = st.session_state.chatbot.process_query(suggestion)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response['text'],
                    "chart": response['chart'],
                    "data": response['data']
                })
                st.rerun()