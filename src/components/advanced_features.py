"""
Advanced Features for Safety & Compliance Dashboard
Includes notifications, user management, export features, and more
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import io
import base64
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import warnings
warnings.filterwarnings('ignore')

class AdvancedFeatures:
    """Advanced features for the dashboard"""
    
    def __init__(self):
        self.notification_types = {
            'success': {'icon': '✅', 'color': '#28a745'},
            'warning': {'icon': '⚠️', 'color': '#ffc107'},
            'error': {'icon': '❌', 'color': '#dc3545'},
            'info': {'icon': 'ℹ️', 'color': '#17a2b8'}
        }
        
        # Initialize session state for notifications
        if 'notifications' not in st.session_state:
            st.session_state.notifications = []
        
        if 'user_preferences' not in st.session_state:
            st.session_state.user_preferences = {
                'language': 'ar',
                'timezone': 'Asia/Riyadh',
                'notifications_enabled': True,
                'auto_refresh': False,
                'export_format': 'xlsx'
            }
    
    def add_notification(self, message, notification_type='info', duration=5):
        """Add a notification to the system"""
        notification = {
            'id': len(st.session_state.notifications),
            'message': message,
            'type': notification_type,
            'timestamp': datetime.now(),
            'duration': duration,
            'read': False
        }
        st.session_state.notifications.append(notification)
    
    def show_notifications(self):
        """Display notifications"""
        if st.session_state.notifications:
            st.sidebar.markdown("### 🔔 الإشعارات")
            
            unread_count = len([n for n in st.session_state.notifications if not n['read']])
            if unread_count > 0:
                st.sidebar.markdown(f"**{unread_count} إشعار جديد**")
            
            for notification in st.session_state.notifications[-5:]:  # Show last 5
                icon = self.notification_types[notification['type']]['icon']
                color = self.notification_types[notification['type']]['color']
                
                time_diff = datetime.now() - notification['timestamp']
                time_str = f"{time_diff.seconds // 60}م" if time_diff.seconds < 3600 else f"{time_diff.seconds // 3600}س"
                
                st.sidebar.markdown(f"""
                <div style="
                    background-color: {color}20;
                    border-left: 4px solid {color};
                    padding: 0.5rem;
                    margin: 0.5rem 0;
                    border-radius: 0.25rem;
                    font-size: 0.8rem;
                ">
                    {icon} {notification['message']}<br>
                    <small style="opacity: 0.7;">{time_str}</small>
                </div>
                """, unsafe_allow_html=True)
            
            if st.sidebar.button("مسح الإشعارات"):
                st.session_state.notifications = []
                st.rerun()
    
    def create_user_profile_section(self):
        """Create user profile and preferences section"""
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 الملف الشخصي")
        
        # User info (in a real app, this would come from authentication)
        user_name = st.sidebar.text_input("اسم المستخدم", value="مدير السلامة")
        user_role = st.sidebar.selectbox("الدور", ["مدير السلامة", "مشرف", "محلل", "مراجع"])
        
        # User preferences
        with st.sidebar.expander("⚙️ الإعدادات"):
            st.session_state.user_preferences['language'] = st.selectbox(
                "اللغة", ["العربية", "English"], 
                index=0 if st.session_state.user_preferences['language'] == 'ar' else 1
            )
            
            st.session_state.user_preferences['notifications_enabled'] = st.checkbox(
                "تفعيل الإشعارات", 
                value=st.session_state.user_preferences['notifications_enabled']
            )
            
            st.session_state.user_preferences['auto_refresh'] = st.checkbox(
                "التحديث التلقائي", 
                value=st.session_state.user_preferences['auto_refresh']
            )
            
            st.session_state.user_preferences['export_format'] = st.selectbox(
                "تنسيق التصدير الافتراضي",
                ["xlsx", "csv", "pdf"],
                index=["xlsx", "csv", "pdf"].index(st.session_state.user_preferences['export_format'])
            )
        
        return {
            'name': user_name,
            'role': user_role,
            'preferences': st.session_state.user_preferences
        }
    
    def create_search_functionality(self, unified_data):
        """Create advanced search functionality"""
        st.sidebar.markdown("### 🔍 البحث المتقدم")
        
        search_query = st.sidebar.text_input("البحث في البيانات", placeholder="ابحث عن...")
        search_type = st.sidebar.selectbox("نوع البحث", ["الكل", "النص", "التاريخ", "الرقم"])
        
        if search_query:
            search_results = self.perform_search(unified_data, search_query, search_type)
            
            if search_results:
                st.sidebar.markdown(f"**النتائج: {len(search_results)} عنصر**")
                
                # Show search results in main area
                if st.sidebar.button("عرض النتائج"):
                    st.session_state.search_results = search_results
                    st.session_state.show_search_results = True
            else:
                st.sidebar.markdown("لا توجد نتائج")
        
        return search_query
    
    def perform_search(self, unified_data, query, search_type):
        """Perform search across all data"""
        results = []
        
        for data_type, df in unified_data.items():
            if df.empty:
                continue
            
            # Search in text columns
            text_columns = df.select_dtypes(include=['object']).columns
            
            for col in text_columns:
                mask = df[col].astype(str).str.contains(query, case=False, na=False)
                if mask.any():
                    matching_rows = df[mask]
                    for idx, row in matching_rows.iterrows():
                        results.append({
                            'data_type': data_type,
                            'column': col,
                            'value': row[col],
                            'row_data': row.to_dict()
                        })
        
        return results
    
    def show_search_results(self):
        """Display search results"""
        if st.session_state.get('show_search_results', False) and 'search_results' in st.session_state:
            st.markdown("### 🔍 نتائج البحث")
            
            results = st.session_state.search_results
            
            # Group results by data type
            grouped_results = {}
            for result in results:
                data_type = result['data_type']
                if data_type not in grouped_results:
                    grouped_results[data_type] = []
                grouped_results[data_type].append(result)
            
            # Display results in tabs
            if grouped_results:
                tabs = st.tabs(list(grouped_results.keys()))
                
                for i, (data_type, type_results) in enumerate(grouped_results.items()):
                    with tabs[i]:
                        st.markdown(f"**{len(type_results)} نتيجة في {data_type}**")
                        
                        for result in type_results[:10]:  # Show first 10 results
                            with st.expander(f"النتيجة: {result['column']} = {result['value']}"):
                                st.json(result['row_data'])
            
            if st.button("إغلاق النتائج"):
                st.session_state.show_search_results = False
                st.rerun()
    
    def create_export_center(self, unified_data, kpi_data):
        """Create comprehensive export center"""
        st.markdown("### 📤 مركز التصدير")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📊 تصدير البيانات")
            
            # Data export options
            export_data_type = st.selectbox(
                "نوع البيانات",
                ["الكل"] + list(unified_data.keys())
            )
            
            export_format = st.selectbox(
                "تنسيق التصدير",
                ["Excel (.xlsx)", "CSV (.csv)", "JSON (.json)"]
            )
            
            if st.button("تصدير البيانات"):
                self.export_data(unified_data, export_data_type, export_format)
        
        with col2:
            st.markdown("#### 📈 تنزيل البيانات")
            
            download_format = st.selectbox(
                "تنسيق التحميل",
                ["Excel (.xlsx)", "CSV (.csv)"]
            )
            
            if st.button("تحميل البيانات"):
                if download_format == "Excel (.xlsx)":
                    self.export_data(unified_data, "الكل", "Excel (.xlsx)")
                else:
                    self.export_data(unified_data, "الكل", "CSV (.csv)")
        
        with col3:
            st.markdown("#### 📧 إرسال التقارير")
            
            email_recipient = st.text_input("البريد الإلكتروني للمستلم")
            email_subject = st.text_input("موضوع الرسالة", value="تقرير السلامة والامتثال")
            
            schedule_type = st.selectbox(
                "جدولة الإرسال",
                ["الآن", "يومي", "أسبوعي", "شهري"]
            )
            
            if st.button("إرسال التقرير"):
                if email_recipient:
                    self.schedule_email_report(email_recipient, email_subject, schedule_type)
                else:
                    st.error("يرجى إدخال البريد الإلكتروني")
    
    def export_data(self, unified_data, data_type, format_type):
        """Export data in specified format"""
        try:
            if data_type == "الكل":
                data_to_export = unified_data
            else:
                data_to_export = {data_type: unified_data[data_type]}
            
            if "Excel" in format_type:
                # Create Excel file
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    for sheet_name, df in data_to_export.items():
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                output.seek(0)
                
                st.download_button(
                    label="تحميل ملف Excel",
                    data=output.getvalue(),
                    file_name=f"safety_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            elif "CSV" in format_type:
                if len(data_to_export) == 1:
                    df = list(data_to_export.values())[0]
                    csv = df.to_csv(index=False)
                    
                    st.download_button(
                        label="تحميل ملف CSV",
                        data=csv,
                        file_name=f"safety_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("يرجى اختيار نوع بيانات واحد لتصدير CSV")
            
            elif "JSON" in format_type:
                json_data = {}
                for name, df in data_to_export.items():
                    json_data[name] = df.to_dict('records')
                
                json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
                
                st.download_button(
                    label="تحميل ملف JSON",
                    data=json_str,
                    file_name=f"safety_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            self.add_notification("تم تصدير البيانات بنجاح", "success")
            
        except Exception as e:
            st.error(f"خطأ في تصدير البيانات: {str(e)}")
            self.add_notification(f"فشل في تصدير البيانات: {str(e)}", "error")
    
    def generate_report(self, unified_data, kpi_data, report_type, format_type):
        """Generate comprehensive reports"""
        try:
            if format_type == "PDF":
                pdf_buffer = self.create_pdf_report(unified_data, kpi_data, report_type)
                
                st.download_button(
                    label="تحميل تقرير PDF",
                    data=pdf_buffer.getvalue(),
                    file_name=f"safety_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
            
            self.add_notification("تم إنشاء التقرير بنجاح", "success")
            
        except Exception as e:
            st.error(f"خطأ في إنشاء التقرير: {str(e)}")
            self.add_notification(f"فشل في إنشاء التقرير: {str(e)}", "error")
    
    def create_pdf_report(self, unified_data, kpi_data, report_type):
        """Create PDF report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        story.append(Paragraph("تقرير السلامة والامتثال", title_style))
        story.append(Spacer(1, 12))
        
        # Date
        story.append(Paragraph(f"تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # KPI Summary
        story.append(Paragraph("ملخص المؤشرات الرئيسية", styles['Heading2']))
        
        kpi_data_list = []
        for key, data in kpi_data.items():
            if isinstance(data, dict) and 'total_records' in data:
                kpi_data_list.append([key, str(data['total_records'])])
        
        if kpi_data_list:
            kpi_table = Table(kpi_data_list, colWidths=[3*inch, 1*inch])
            kpi_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(kpi_table)
        
        story.append(Spacer(1, 12))
        
        # Data Summary
        story.append(Paragraph("ملخص البيانات", styles['Heading2']))
        
        for data_type, df in unified_data.items():
            if not df.empty:
                story.append(Paragraph(f"{data_type}: {len(df)} سجل", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def schedule_email_report(self, recipient, subject, schedule_type):
        """Schedule email reports"""
        # In a real application, this would integrate with a task scheduler
        # For now, we'll just show a success message
        
        schedule_info = {
            'recipient': recipient,
            'subject': subject,
            'schedule_type': schedule_type,
            'created_at': datetime.now(),
            'status': 'scheduled'
        }
        
        # Store in session state (in real app, store in database)
        if 'scheduled_reports' not in st.session_state:
            st.session_state.scheduled_reports = []
        
        st.session_state.scheduled_reports.append(schedule_info)
        
        st.success(f"تم جدولة التقرير للإرسال إلى {recipient}")
        self.add_notification(f"تم جدولة تقرير {schedule_type} إلى {recipient}", "success")
    
    def create_analytics_insights(self, unified_data):
        """Create AI-powered analytics insights"""
        st.markdown("### 🧠 رؤى ذكية")
        
        insights = self.generate_insights(unified_data)
        
        for i, insight in enumerate(insights):
            with st.expander(f"💡 رؤية {i+1}: {insight['title']}"):
                st.markdown(f"**الوصف:** {insight['description']}")
                st.markdown(f"**التوصية:** {insight['recommendation']}")
                st.markdown(f"**الأولوية:** {insight['priority']}")
                
                if insight.get('chart'):
                    st.plotly_chart(insight['chart'], use_container_width=True)
    
    def generate_insights(self, unified_data):
        """Generate AI-powered insights"""
        insights = []
        
        # Insight 1: Data completeness
        total_records = sum(len(df) for df in unified_data.values() if not df.empty)
        if total_records > 0:
            insights.append({
                'title': 'اكتمال البيانات',
                'description': f'يحتوي النظام على {total_records:,} سجل عبر {len(unified_data)} مجموعة بيانات',
                'recommendation': 'تأكد من تحديث البيانات بانتظام للحصول على رؤى دقيقة',
                'priority': 'متوسط'
            })
        
        # Insight 2: Status distribution
        total_open = 0
        total_closed = 0
        
        for data_type, df in unified_data.items():
            if df.empty:
                continue
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['حالة', 'status']):
                    status_counts = df[col].value_counts()
                    for status, count in status_counts.items():
                        if any(keyword in str(status).lower() for keyword in ['مفتوح', 'open']):
                            total_open += count
                        elif any(keyword in str(status).lower() for keyword in ['مغلق', 'closed']):
                            total_closed += count
        
        if total_open + total_closed > 0:
            compliance_rate = (total_closed / (total_open + total_closed)) * 100
            
            if compliance_rate < 70:
                priority = 'عالي'
                recommendation = 'معدل الامتثال منخفض. يجب التركيز على إغلاق الحالات المفتوحة'
            elif compliance_rate < 85:
                priority = 'متوسط'
                recommendation = 'معدل الامتثال جيد ولكن يمكن تحسينه'
            else:
                priority = 'منخفض'
                recommendation = 'معدل الامتثال ممتاز. حافظ على هذا الأداء'
            
            insights.append({
                'title': 'معدل الامتثال',
                'description': f'معدل الامتثال الحالي هو {compliance_rate:.1f}%',
                'recommendation': recommendation,
                'priority': priority
            })
        
        # Insight 3: Activity analysis
        activity_counts = {}
        for data_type, df in unified_data.items():
            if df.empty:
                continue
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['نشاط', 'activity']):
                    activities = df[col].dropna()
                    for activity in activities:
                        clean_activity = str(activity).split('\n')[0]
                        activity_counts[clean_activity] = activity_counts.get(clean_activity, 0) + 1
        
        if activity_counts:
            top_activity = max(activity_counts, key=activity_counts.get)
            insights.append({
                'title': 'النشاط الأكثر تكراراً',
                'description': f'النشاط الأكثر تكراراً هو "{top_activity}" بـ {activity_counts[top_activity]} حالة',
                'recommendation': 'راجع إجراءات السلامة لهذا النشاط وتأكد من تطبيقها بشكل صحيح',
                'priority': 'متوسط'
            })
        
        return insights
    
    def create_real_time_monitoring(self, unified_data):
        """Create real-time monitoring dashboard"""
        st.markdown("### 📡 المراقبة في الوقت الفعلي")
        
        # Auto-refresh option
        auto_refresh = st.checkbox("التحديث التلقائي (كل 30 ثانية)")
        
        if auto_refresh:
            # In a real application, this would fetch new data
            st.info("🔄 التحديث التلقائي مفعل")
            
            # Simulate real-time data
            import time
            placeholder = st.empty()
            
            for i in range(5):
                with placeholder.container():
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("الحالات الجديدة", np.random.randint(0, 10))
                    
                    with col2:
                        st.metric("التحديثات", np.random.randint(0, 5))
                    
                    with col3:
                        st.metric("التنبيهات", np.random.randint(0, 3))
                
                time.sleep(1)  # Update every second for demo
        
        # Recent activity feed
        st.markdown("#### 📋 النشاط الأخير")
        
        recent_activities = [
            {"time": "منذ 5 دقائق", "action": "تم إغلاق حالة تفتيش", "user": "أحمد محمد"},
            {"time": "منذ 15 دقيقة", "action": "تم إضافة تقييم مخاطر جديد", "user": "فاطمة علي"},
            {"time": "منذ 30 دقيقة", "action": "تم تحديث حالة حادث", "user": "محمد سالم"},
            {"time": "منذ ساعة", "action": "تم إنشاء تقرير تدقيق", "user": "سارة أحمد"},
        ]
        
        for activity in recent_activities:
            st.markdown(f"""
            <div style="
                background-color: #f8f9fa;
                padding: 0.5rem;
                margin: 0.5rem 0;
                border-radius: 0.25rem;
                border-left: 3px solid #007bff;
            ">
                <strong>{activity['action']}</strong><br>
                <small>بواسطة {activity['user']} • {activity['time']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    def create_collaboration_features(self):
        """Create collaboration and sharing features"""
        st.markdown("### 👥 التعاون والمشاركة")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💬 التعليقات")
            
            # Comments system
            if 'comments' not in st.session_state:
                st.session_state.comments = []
            
            new_comment = st.text_area("إضافة تعليق")
            if st.button("إضافة التعليق"):
                if new_comment:
                    comment = {
                        'id': len(st.session_state.comments),
                        'text': new_comment,
                        'author': 'المستخدم الحالي',
                        'timestamp': datetime.now(),
                        'replies': []
                    }
                    st.session_state.comments.append(comment)
                    st.success("تم إضافة التعليق")
                    st.rerun()
            
            # Display comments
            for comment in st.session_state.comments[-5:]:
                with st.expander(f"تعليق من {comment['author']}"):
                    st.write(comment['text'])
                    st.caption(f"في {comment['timestamp'].strftime('%Y-%m-%d %H:%M')}")
        
        with col2:
            st.markdown("#### 🔗 المشاركة")
            
            # Share dashboard
            share_url = "https://your-dashboard-url.com/shared/12345"
            st.text_input("رابط المشاركة", value=share_url)
            
            if st.button("نسخ الرابط"):
                st.success("تم نسخ الرابط!")
            
            # Share via email
            st.markdown("**مشاركة عبر البريد الإلكتروني:**")
            share_email = st.text_input("البريد الإلكتروني")
            share_message = st.text_area("رسالة إضافية")
            
            if st.button("إرسال الدعوة"):
                if share_email:
                    st.success(f"تم إرسال دعوة إلى {share_email}")
                    self.add_notification(f"تم إرسال دعوة مشاركة إلى {share_email}", "success")
    
    def create_help_system(self):
        """Create comprehensive help system"""
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ❓ المساعدة")
        
        help_topics = {
            "البدء السريع": "كيفية استخدام لوحة المعلومات",
            "المرشحات": "كيفية استخدام المرشحات المتقدمة",
            "التصدير": "كيفية تصدير البيانات والتقارير",
            "المظاهر": "كيفية تغيير مظهر التطبيق",
            "الإشعارات": "إدارة الإشعارات والتنبيهات"
        }
        
        selected_topic = st.sidebar.selectbox("اختر موضوع المساعدة", list(help_topics.keys()))
        
        if st.sidebar.button("عرض المساعدة"):
            st.session_state.show_help = True
            st.session_state.help_topic = selected_topic
        
        # Show help in main area
        if st.session_state.get('show_help', False):
            self.show_help_content(st.session_state.get('help_topic', 'البدء السريع'))
    
    def show_help_content(self, topic):
        """Show help content for selected topic"""
        st.markdown("### ❓ المساعدة والدعم")
        
        help_content = {
            "البدء السريع": """
            ## 🚀 البدء السريع
            
            مرحباً بك في لوحة معلومات السلامة والامتثال!
            
            ### الخطوات الأولى:
            1. **استكشف البيانات**: ابدأ بمراجعة المؤشرات الرئيسية في الصفحة الرئيسية
            2. **استخدم المرشحات**: استخدم المرشحات في الشريط الجانبي لتخصيص العرض
            3. **تفاعل مع الرسوم البيانية**: انقر على الرسوم البيانية للحصول على تفاصيل أكثر
            4. **صدّر البيانات**: استخدم مركز التصدير لحفظ التقارير
            
            ### نصائح مفيدة:
            - استخدم البحث المتقدم للعثور على بيانات محددة
            - فعّل الإشعارات لتلقي التحديثات المهمة
            - جرب المظاهر المختلفة لتخصيص التجربة
            """,
            
            "المرشحات": """
            ## 🔍 استخدام المرشحات
            
            ### أنواع المرشحات المتاحة:
            
            #### 📅 مرشح التاريخ
            - اختر نطاق زمني محدد لعرض البيانات
            - يمكن تحديد تاريخ البداية والنهاية
            
            #### 🏢 مرشح القطاعات
            - اختر قطاع واحد أو أكثر
            - يؤثر على جميع الرسوم البيانية والجداول
            
            #### 📊 مرشح الحالة
            - فلترة حسب الحالة (مفتوح/مغلق)
            - مفيد لتتبع الامتثال
            
            #### 🎯 مرشح النشاط
            - اختر أنواع الأنشطة المحددة
            - يساعد في التحليل المتخصص
            
            ### نصائح للاستخدام:
            - استخدم عدة مرشحات معاً للحصول على رؤى دقيقة
            - احفظ إعدادات المرشحات المفضلة لديك
            - استخدم "مسح المرشحات" للعودة للعرض الكامل
            """,
            
            "التصدير": """
            ## 📤 تصدير البيانات والتقارير
            
            ### أنواع التصدير المتاحة:
            
            #### 📊 تصدير البيانات
            - **Excel**: ملف شامل مع عدة أوراق عمل
            - **CSV**: ملف نصي بسيط للتحليل الخارجي
            - **JSON**: تنسيق برمجي للتطبيقات الأخرى
            
            #### 📈 تصدير التقارير
            - **PDF**: تقرير مصمم للطباعة والمشاركة
            - **Word**: تقرير قابل للتعديل
            - **PowerPoint**: عرض تقديمي جاهز
            
            #### 📧 الإرسال التلقائي
            - جدولة التقارير اليومية/الأسبوعية/الشهرية
            - إرسال تلقائي عبر البريد الإلكتروني
            - تخصيص المحتوى والمستلمين
            
            ### خطوات التصدير:
            1. اذهب إلى "مركز التصدير"
            2. اختر نوع البيانات أو التقرير
            3. حدد التنسيق المطلوب
            4. انقر "تصدير" أو "إنشاء التقرير"
            5. احفظ الملف أو شاركه
            """,
            
            "المظاهر": """
            ## 🎨 تخصيص المظهر
            
            ### المظاهر المتاحة:
            
            #### ☀️ المظهر الفاتح
            - مناسب للاستخدام النهاري
            - ألوان هادئة ومريحة للعين
            - خلفية بيضاء مع نصوص داكنة
            
            #### 🌙 المظهر الداكن
            - مثالي للاستخدام الليلي
            - يقلل إجهاد العين في الإضاءة المنخفضة
            - خلفية داكنة مع نصوص فاتحة
            
            #### 🌊 المظهر الأزرق
            - مظهر مهني بألوان البحر
            - مناسب للعروض التقديمية
            - يركز على الثقة والاستقرار
            
            #### 🌿 المظهر الأخضر
            - مظهر طبيعي ومريح
            - يرمز للنمو والتطور
            - مناسب للاستخدام طويل المدى
            
            ### كيفية تغيير المظهر:
            1. اذهب إلى الشريط الجانبي
            2. ابحث عن قسم "اختيار المظهر"
            3. اختر المظهر المفضل
            4. سيتم تطبيق التغيير فوراً
            
            ### حفظ التفضيلات:
            - يتم حفظ اختيار المظهر تلقائياً
            - سيتم استخدام نفس المظهر في الزيارات القادمة
            """,
            
            "الإشعارات": """
            ## 🔔 إدارة الإشعارات
            
            ### أنواع الإشعارات:
            
            #### ✅ إشعارات النجاح
            - تأكيد العمليات المكتملة
            - نجاح التصدير أو الحفظ
            - إتمام المهام بنجاح
            
            #### ⚠️ إشعارات التحذير
            - تنبيهات مهمة تحتاج انتباه
            - بيانات ناقصة أو غير مكتملة
            - توصيات للتحسين
            
            #### ❌ إشعارات الخطأ
            - مشاكل تقنية أو أخطاء
            - فشل في العمليات
            - مشاكل في الاتصال
            
            #### ℹ️ إشعارات المعلومات
            - معلومات عامة ونصائح
            - تحديثات النظام
            - إرشادات الاستخدام
            
            ### إعدادات الإشعارات:
            - تفعيل/إلغاء الإشعارات من الملف الشخصي
            - تخصيص أنواع الإشعارات المطلوبة
            - تحديد طريقة العرض والمدة
            
            ### إدارة الإشعارات:
            - عرض الإشعارات الحديثة في الشريط الجانبي
            - مسح الإشعارات القديمة
            - تصدير سجل الإشعارات
            """
        }
        
        content = help_content.get(topic, "المحتوى غير متاح")
        st.markdown(content)
        
        if st.button("إغلاق المساعدة"):
            st.session_state.show_help = False
            st.rerun()
    
    def create_performance_monitor(self):
        """Create performance monitoring section"""
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ⚡ الأداء")
        
        # Simulate performance metrics
        load_time = np.random.uniform(0.5, 2.0)
        memory_usage = np.random.uniform(50, 200)
        
        st.sidebar.metric("وقت التحميل", f"{load_time:.1f}s")
        st.sidebar.metric("استخدام الذاكرة", f"{memory_usage:.0f}MB")
        
        # Performance status
        if load_time < 1.0:
            st.sidebar.success("الأداء ممتاز")
        elif load_time < 2.0:
            st.sidebar.warning("الأداء جيد")
        else:
            st.sidebar.error("الأداء بطيء")
    
    def cleanup_old_notifications(self):
        """Clean up old notifications"""
        if st.session_state.notifications:
            # Keep only notifications from last 24 hours
            cutoff_time = datetime.now() - timedelta(hours=24)
            st.session_state.notifications = [
                n for n in st.session_state.notifications 
                if n['timestamp'] > cutoff_time
            ]
    
    def create_manual_upload_section(self):
        """Create manual data upload section"""
        st.title("📤 رفع البيانات اليدوي")
        st.markdown("---")
        
        # Upload options
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 رفع ملفات Excel")
            uploaded_excel = st.file_uploader(
                "اختر ملفات Excel",
                type=['xlsx', 'xls'],
                accept_multiple_files=True,
                key="excel_uploader"
            )
            
            if uploaded_excel:
                st.success(f"تم رفع {len(uploaded_excel)} ملف Excel")
                for file in uploaded_excel:
                    st.write(f"📄 {file.name}")
                    
                    # Process Excel file
                    try:
                        df = pd.read_excel(file)
                        st.write(f"الأبعاد: {df.shape[0]} صف × {df.shape[1]} عمود")
                        
                        # Show preview
                        if st.checkbox(f"معاينة {file.name}", key=f"preview_excel_{file.name}"):
                            st.dataframe(df.head())
                            
                    except Exception as e:
                        st.error(f"خطأ في قراءة الملف: {str(e)}")
        
        with col2:
            st.subheader("📄 رفع ملفات CSV")
            uploaded_csv = st.file_uploader(
                "اختر ملفات CSV",
                type=['csv'],
                accept_multiple_files=True,
                key="csv_uploader"
            )
            
            if uploaded_csv:
                st.success(f"تم رفع {len(uploaded_csv)} ملف CSV")
                for file in uploaded_csv:
                    st.write(f"📄 {file.name}")
                    
                    # Process CSV file
                    try:
                        df = pd.read_csv(file)
                        st.write(f"الأبعاد: {df.shape[0]} صف × {df.shape[1]} عمود")
                        
                        # Show preview
                        if st.checkbox(f"معاينة {file.name}", key=f"preview_csv_{file.name}"):
                            st.dataframe(df.head())
                            
                    except Exception as e:
                        st.error(f"خطأ في قراءة الملف: {str(e)}")
        
        # Data processing options
        st.markdown("---")
        st.subheader("⚙️ خيارات المعالجة")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            clean_data = st.checkbox("تنظيف البيانات تلقائياً", value=True)
            
        with col2:
            validate_data = st.checkbox("التحقق من جودة البيانات", value=True)
            
        with col3:
            merge_data = st.checkbox("دمج البيانات مع الموجود", value=False)
        
        # Process button
        if st.button("🚀 معالجة البيانات", type="primary"):
            if uploaded_excel or uploaded_csv:
                with st.spinner("جاري معالجة البيانات..."):
                    # Simulate processing
                    import time
                    time.sleep(2)
                    
                    st.success("✅ تم معالجة البيانات بنجاح!")
                    self.add_notification("تم رفع ومعالجة البيانات الجديدة", "success")
                    
                    # Show processing results
                    st.subheader("📊 نتائج المعالجة")
                    
                    results_col1, results_col2, results_col3 = st.columns(3)
                    
                    with results_col1:
                        st.metric("الملفات المعالجة", len(uploaded_excel or []) + len(uploaded_csv or []))
                    
                    with results_col2:
                        st.metric("الأخطاء المكتشفة", np.random.randint(0, 5))
                    
                    with results_col3:
                        st.metric("البيانات المضافة", f"{np.random.randint(100, 1000)} صف")
                        
            else:
                st.warning("⚠️ يرجى رفع ملف واحد على الأقل")
        
        # Data quality report
        st.markdown("---")
        st.subheader("📋 تقرير جودة البيانات")
        
        if st.button("إنشاء تقرير الجودة"):
            with st.spinner("جاري إنشاء التقرير..."):
                time.sleep(1)
                
                # Simulate quality report
                quality_data = {
                    'المقياس': ['اكتمال البيانات', 'دقة البيانات', 'اتساق البيانات', 'صحة التنسيق'],
                    'النتيجة': [95, 88, 92, 97],
                    'الحالة': ['ممتاز', 'جيد', 'جيد جداً', 'ممتاز']
                }
                
                quality_df = pd.DataFrame(quality_data)
                st.dataframe(quality_df, use_container_width=True)
                
                # Quality visualization
                fig = px.bar(
                    quality_df, 
                    x='المقياس', 
                    y='النتيجة',
                    title='مؤشرات جودة البيانات',
                    color='النتيجة',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)