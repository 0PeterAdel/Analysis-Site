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
import warnings
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
warnings.filterwarnings('ignore')

# Import settings for colors and other configurations
from src.config.settings import COLORS, APP_TITLE, RISK_ACTIVITIES_METADATA

# For PDF generation (requires ReportLab, which might need installation)
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    st.warning("ReportLab library not found. PDF export will be disabled. Please install it: pip install reportlab")
    REPORTLAB_AVAILABLE = False

# For email functionality (requires SMTP server configuration)
# This is a placeholder for demonstration.
# In a real app, you'd use a secure way to handle credentials and an actual SMTP server.
SMTP_CONFIG = {
    "ENABLED": False, # Set to True to enable actual email sending (requires proper setup)
    "HOST": "smtp.your-email.com",
    "PORT": 587,
    "USERNAME": "your_email@example.com",
    "PASSWORD": "your_email_password",
    "SENDER_EMAIL": "noreply@example.com"
}

class AdvancedFeatures:
    """Advanced features for the dashboard"""
    
    def __init__(self):
        self.notification_types = {
            'success': {'icon': '✅', 'color': COLORS['success']},
            'warning': {'icon': '⚠️', 'color': COLORS['warning']},
            'error': {'icon': '❌', 'color': COLORS['danger']},
            'info': {'icon': 'ℹ️', 'color': COLORS['info']}
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
                'export_format': 'xlsx' # Default export format
            }
        # Initialize for help system
        if 'show_help' not in st.session_state:
            st.session_state.show_help = False
        if 'help_topic' not in st.session_state:
            st.session_state.help_topic = 'البدء السريع'

    def add_notification(self, message: str, notification_type: str = 'info', duration: int = 5):
        """Add a notification to the system's session state."""
        if st.session_state.user_preferences.get('notifications_enabled', True):
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
        """Display notifications in the sidebar."""
        if st.session_state.notifications and st.session_state.user_preferences.get('notifications_enabled', True):
            st.sidebar.markdown("### 🔔 الإشعارات")
            
            unread_count = len([n for n in st.session_state.notifications if not n['read']])
            if unread_count > 0:
                st.sidebar.markdown(f"**{unread_count} إشعار جديد**")
            
            # Display recent notifications (last 5)
            for notification in st.session_state.notifications[-5:]:
                icon = self.notification_types.get(notification['type'], {'icon': 'ℹ️', 'color': COLORS['info']})['icon']
                color = self.notification_types.get(notification['type'], {'icon': 'ℹ️', 'color': COLORS['info']})['color']
                
                time_diff = datetime.now() - notification['timestamp']
                # Format time difference for display
                if time_diff.total_seconds() < 60:
                    time_str = f"{int(time_diff.total_seconds())}ث"
                elif time_diff.total_seconds() < 3600:
                    time_str = f"{int(time_diff.total_seconds() // 60)}د"
                elif time_diff.total_seconds() < 86400:
                    time_str = f"{int(time_diff.total_seconds() // 3600)}س"
                else:
                    time_str = f"{int(time_diff.total_seconds() // 86400)}ي"
                
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
                    <small style="opacity: 0.7;">{time_str} مضت</small>
                </div>
                """, unsafe_allow_html=True)
            
            if st.sidebar.button("مسح الإشعارات", key="clear_notifications_btn"):
                st.session_state.notifications = []
                st.rerun()
    
    def create_user_profile_section(self):
        """Create user profile and preferences section in the sidebar."""
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 الملف الشخصي")
        
        # User info (placeholder, would come from authentication in a real app)
        user_name = st.sidebar.text_input("اسم المستخدم", value="مدير السلامة", key="user_name_input")
        user_role = st.sidebar.selectbox("الدور", ["مدير السلامة", "مشرف", "محلل", "مراجع"], key="user_role_select")
        
        # User preferences
        with st.sidebar.expander("⚙️ الإعدادات"):
            # Language preference
            lang_options = ["العربية", "English"]
            current_lang_index = lang_options.index(st.session_state.user_preferences['language']) if st.session_state.user_preferences['language'] in lang_options else 0
            st.session_state.user_preferences['language'] = st.selectbox(
                "اللغة", lang_options, 
                index=current_lang_index, key="lang_select"
            )
            
            # Notifications toggle
            st.session_state.user_preferences['notifications_enabled'] = st.checkbox(
                "تفعيل الإشعارات", 
                value=st.session_state.user_preferences['notifications_enabled'], key="notifications_toggle"
            )
            
            # Auto-refresh toggle
            st.session_state.user_preferences['auto_refresh'] = st.checkbox(
                "التحديث التلقائي (تجريبي)", # Added (تجريبي) as it's a demo
                value=st.session_state.user_preferences['auto_refresh'], key="auto_refresh_toggle"
            )
            
            # Default export format
            export_formats = ["xlsx", "csv", "pdf"]
            current_export_index = export_formats.index(st.session_state.user_preferences['export_format']) if st.session_state.user_preferences['export_format'] in export_formats else 0
            st.session_state.user_preferences['export_format'] = st.selectbox(
                "تنسيق التصدير الافتراضي",
                export_formats,
                index=current_export_index, key="export_format_select"
            )
        
        return {
            'name': user_name,
            'role': user_role,
            'preferences': st.session_state.user_preferences
        }
    
    # Removed create_search_functionality and perform_search as this is now handled by AdvancedFilters and DashboardAnalyzer

    def create_export_center(self, unified_data: dict, kpi_data: dict):
        """Create comprehensive export center in the main content area."""
        st.markdown("### 📤 مركز التصدير")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📊 تصدير البيانات")
            
            # Data export options
            data_types_for_export = ["الكل"] + list(unified_data.keys())
            export_data_type = st.selectbox(
                "نوع البيانات",
                data_types_for_export, key="export_data_type_select"
            )
            
            export_format_options = ["Excel (.xlsx)", "CSV (.csv)", "JSON (.json)"]
            selected_export_format = st.selectbox(
                "تنسيق التصدير",
                export_format_options,
                index=export_format_options.index(f"Excel (.xlsx)") if "xlsx" in st.session_state.user_preferences['export_format'] else 0, # Use user preference
                key="export_format_select_main"
            )
            
            if st.button("تصدير البيانات", key="export_data_button"):
                self.export_data(unified_data, export_data_type, selected_export_format)
        
        with col2:
            st.markdown("#### 📄 تنزيل التقارير (PDF)")
            
            report_type_options = ["ملخص عام", "تقرير الامتثال", "تقرير المخاطر", "تقرير الحوادث"]
            selected_report_type = st.selectbox(
                "نوع التقرير",
                report_type_options, key="report_type_select"
            )
            
            if st.button("إنشاء وتنزيل تقرير PDF", key="download_pdf_report_button"):
                if REPORTLAB_AVAILABLE:
                    # Pass unified_data and kpi_data to generate the report
                    self.generate_report(unified_data, kpi_data, selected_report_type, "PDF")
                else:
                    st.error("مكتبة ReportLab غير متاحة. لا يمكن إنشاء تقارير PDF.")
                    self.add_notification("مكتبة ReportLab غير متاحة لإنشاء PDF", "error")
        
        with col3:
            st.markdown("#### 📧 إرسال التقارير عبر البريد")
            
            email_recipient = st.text_input("البريد الإلكتروني للمستلم", key="email_recipient_input")
            email_subject = st.text_input("موضوع الرسالة", value=f"تقرير السلامة والامتثال من {APP_TITLE}", key="email_subject_input")
            
            schedule_type = st.selectbox(
                "جدولة الإرسال",
                ["الآن", "يومي", "أسبوعي", "شهري"], key="schedule_type_select"
            )
            
            if st.button("إرسال التقرير", key="send_report_button"):
                if email_recipient:
                    if SMTP_CONFIG["ENABLED"]:
                        self.schedule_email_report(email_recipient, email_subject, schedule_type)
                    else:
                        st.warning("وظيفة إرسال البريد الإلكتروني معطلة في الإعدادات (SMTP_CONFIG).")
                        self.add_notification("وظيفة إرسال البريد الإلكتروني معطلة.", "warning")
                else:
                    st.error("يرجى إدخال البريد الإلكتروني للمستلم.")
                    self.add_notification("يرجى إدخال البريد الإلكتروني للمستلم.", "error")
    
    def export_data(self, unified_data: dict, data_type: str, format_type: str):
        """Export data in specified format and provide download button."""
        try:
            data_to_process = {}
            if data_type == "الكل":
                data_to_process = unified_data
            else:
                if data_type in unified_data:
                    data_to_process = {data_type: unified_data[data_type]}
                else:
                    st.warning(f"نوع البيانات '{data_type}' غير موجود للتصدير.")
                    self.add_notification(f"نوع البيانات '{data_type}' غير موجود للتصدير.", "warning")
                    return
            
            if not data_to_process:
                st.info("لا توجد بيانات لتصديرها.")
                self.add_notification("لا توجد بيانات لتصديرها.", "info")
                return

            output_filename_base = f"safety_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            if "Excel" in format_type:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    for sheet_name, df in data_to_process.items():
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                output.seek(0)
                
                st.download_button(
                    label="تحميل ملف Excel",
                    data=output.getvalue(),
                    file_name=f"{output_filename_base}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_excel_btn"
                )
            
            elif "CSV" in format_type:
                if len(data_to_process) == 1:
                    df = list(data_to_process.values())[0]
                    csv_string = df.to_csv(index=False, encoding='utf-8-sig') # Use utf-8-sig for proper Arabic in CSV
                    
                    st.download_button(
                        label="تحميل ملف CSV",
                        data=csv_string,
                        file_name=f"{output_filename_base}.csv",
                        mime="text/csv",
                        key="download_csv_btn"
                    )
                else:
                    st.warning("يرجى اختيار نوع بيانات واحد لتصدير CSV (أو قم بتصدير Excel).")
                    self.add_notification("يرجى اختيار نوع بيانات واحد لتصدير CSV.", "warning")
            
            elif "JSON" in format_type:
                json_data_output = {}
                for name, df in data_to_process.items():
                    # Convert datetime objects to string for JSON serialization
                    df_copy = df.copy()
                    for col in df_copy.select_dtypes(include=['datetime64']).columns:
                        df_copy[col] = df_copy[col].dt.isoformat()
                    json_data_output[name] = df_copy.to_dict('records')
                
                json_str = json.dumps(json_data_output, ensure_ascii=False, indent=2)
                
                st.download_button(
                    label="تحميل ملف JSON",
                    data=json_str,
                    file_name=f"{output_filename_base}.json",
                    mime="application/json",
                    key="download_json_btn"
                )
            
            self.add_notification("تم تصدير البيانات بنجاح", "success")
            
        except Exception as e:
            st.error(f"خطأ في تصدير البيانات: {str(e)}")
            self.add_notification(f"فشل في تصدير البيانات: {str(e)}", "error")
    
    def generate_report(self, unified_data: dict, kpi_data: dict, report_type: str, format_type: str):
        """Generate comprehensive reports in specified format."""
        if not REPORTLAB_AVAILABLE:
            st.error("مكتبة ReportLab غير متاحة. لا يمكن إنشاء تقارير PDF.")
            self.add_notification("مكتبة ReportLab غير متاحة لإنشاء PDF", "error")
            return

        try:
            if format_type == "PDF":
                pdf_buffer = self.create_pdf_report(unified_data, kpi_data, report_type)
                
                st.download_button(
                    label=f"تحميل تقرير {report_type} PDF",
                    data=pdf_buffer.getvalue(),
                    file_name=f"safety_report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    key=f"download_pdf_report_{report_type}_btn"
                )
            
            self.add_notification(f"تم إنشاء تقرير {report_type} بنجاح", "success")
            
        except Exception as e:
            st.error(f"خطأ في إنشاء التقرير: {str(e)}")
            self.add_notification(f"فشل في إنشاء التقرير: {str(e)}", "error")
    
    def create_pdf_report(self, unified_data: dict, kpi_data: dict, report_type: str):
        """
        Creates a PDF report using ReportLab.
        This is a basic example; a full report would require more complex layout and data.
        """
        from .fonts import register_fonts, get_font_config
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, 
                              topMargin=30, bottomMargin=30)
        styles = getSampleStyleSheet()
        story = []

        # Register and configure Arabic fonts
        fonts_registered = register_fonts()
        font_config = get_font_config()

        # Configure styles with Arabic fonts
        if fonts_registered:
            styles['Normal'].fontName = font_config['normal']
            styles['Heading1'].fontName = font_config['bold']
            styles['Heading2'].fontName = font_config['bold']
            styles['Heading3'].fontName = font_config['bold']

            # Title style with Arabic font
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=font_config['title_size'],
                spaceAfter=30,
                alignment=1,  # Center alignment
                fontName=font_config['bold'],
                leading=font_config['title_size'] * 1.2  # Increased line height for Arabic text
            )
        else:
            # Fallback to basic fonts if Arabic fonts are not available
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1,
                fontName='Helvetica-Bold'
            )
        
        # Create custom styles for Arabic text with proper line height
        if fonts_registered:
            arabic_normal = ParagraphStyle(
                'ArabicNormal',
                parent=styles['Normal'],
                fontName=font_config['normal'],
                fontSize=font_config['default_size'],
                leading=font_config['default_size'] * 1.5,  # Increased line height for Arabic
                alignment=1  # Center alignment for Arabic
            )
            
            arabic_heading = ParagraphStyle(
                'ArabicHeading',
                parent=styles['Heading2'],
                fontName=font_config['bold'],
                fontSize=font_config['heading_size'],
                leading=font_config['heading_size'] * 1.5,
                alignment=1
            )
        else:
            arabic_normal = styles['Normal']
            arabic_heading = styles['Heading2']

        # Add report title with proper Arabic styling
        story.append(Paragraph(f"تقرير {report_type} - {APP_TITLE}", title_style))
        story.append(Spacer(1, 12))
        
        # Date with Arabic styling
        story.append(Paragraph(f"تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')}", arabic_normal))
        story.append(Spacer(1, 12))
        
        # General KPI Summary with Arabic styling
        story.append(Paragraph("ملخص المؤشرات الرئيسية", arabic_heading))
        
        kpi_summary_data = [["المؤشر", "القيمة"]]
        # Aggregate overall KPIs from kpi_data (which is from DataProcessor)
        total_records_overall = sum([data.get('total_records', 0) for data in kpi_data.values()])
        open_count_overall = sum([data.get('status_distribution', {}).get('مفتوح', 0) for data in kpi_data.values()])
        closed_count_overall = sum([data.get('status_distribution', {}).get('مغلق', 0) for data in kpi_data.values()])
        closure_rate_overall = (closed_count_overall / (open_count_overall + closed_count_overall) * 100) if (open_count_overall + closed_count_overall) > 0 else 0

        kpi_summary_data.append(["إجمالي السجلات", f"{total_records_overall:,}"])
        kpi_summary_data.append(["الحالات المفتوحة", f"{open_count_overall:,}"])
        kpi_summary_data.append(["الحالات المغلقة", f"{closed_count_overall:,}"])
        kpi_summary_data.append(["نسبة الإغلاق", f"{closure_rate_overall:.1f}%"])

        kpi_table = Table(kpi_summary_data, colWidths=[3*inch, 2*inch])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['primary'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor(COLORS['light'])),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'), # Placeholder
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 24))

        # Add specific report content based on report_type
        if report_type == "تقرير الامتثال":
            story.append(Paragraph("تفاصيل تقرير الامتثال", styles['Heading2']))
            compliance_df = st.session_state.dashboard_analyzer.get_compliance_summary(unified_data, filters={}) # Get full compliance data
            if not compliance_df.empty:
                # Select relevant columns for PDF table
                display_cols = ['القطاع', 'إجمالي السجلات', 'السجلات المغلقة', 'السجلات المفتوحة', 'نسبة الامتثال %', 'الأولوية', 'التوصية']
                pdf_table_data = [display_cols] + compliance_df[display_cols].values.tolist()
                
                # Convert percentages to string for display
                for row_idx in range(1, len(pdf_table_data)):
                    pdf_table_data[row_idx][4] = f"{pdf_table_data[row_idx][4]:.1f}%"

                compliance_table = Table(pdf_table_data, colWidths=[1.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1.0*inch, 0.8*inch, 1.5*inch])
                compliance_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['primary'])),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor(COLORS['light'])),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                ]))
                story.append(compliance_table)
            else:
                story.append(Paragraph("لا توجد بيانات امتثال مفصلة متاحة.", styles['Normal']))

        elif report_type == "تقرير المخاطر":
            story.append(Paragraph("تفاصيل تقرير المخاطر", styles['Heading2']))
            risk_summary_df = st.session_state.dashboard_analyzer.get_risk_activities_summary(unified_data, filters={})
            if not risk_summary_df.empty:
                display_cols = ['النشاط', 'إجمالي التقييمات', 'المخاطر العالية', 'مستوى المخاطر', 'نسبة المخاطر %', 'التوصية']
                pdf_table_data = [display_cols] + risk_summary_df[display_cols].values.tolist()
                
                risk_table = Table(pdf_table_data, colWidths=[1.5*inch, 1.0*inch, 1.0*inch, 1.0*inch, 1.0*inch, 1.5*inch])
                risk_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['primary'])),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor(COLORS['light'])),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                ]))
                story.append(risk_table)
            else:
                story.append(Paragraph("لا توجد بيانات مخاطر مفصلة متاحة.", styles['Normal']))

        elif report_type == "تقرير الحوادث":
            story.append(Paragraph("تفاصيل تقرير الحوادث", styles['Heading2']))
            incidents_summary_df = st.session_state.dashboard_analyzer.get_incidents_summary(unified_data, filters={})
            if not incidents_summary_df.empty:
                display_cols = ['القطاع', 'عدد الحوادث', 'عدد التوصيات', 'مغلق', 'مفتوح', 'نسبة الإغلاق %']
                pdf_table_data = [display_cols] + incidents_summary_df[display_cols].values.tolist()
                
                # Convert percentages to string for display
                for row_idx in range(1, len(pdf_table_data)):
                    pdf_table_data[row_idx][5] = f"{pdf_table_data[row_idx][5]:.1f}%"

                incidents_table = Table(pdf_table_data, colWidths=[1.5*inch, 1.0*inch, 1.0*inch, 0.8*inch, 0.8*inch, 1.0*inch])
                incidents_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['primary'])),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor(COLORS['light'])),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                ]))
                story.append(incidents_table)
            else:
                story.append(Paragraph("لا توجد بيانات حوادث مفصلة متاحة.", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def schedule_email_report(self, recipient: str, subject: str, schedule_type: str):
        """Schedule email reports (placeholder/demo)."""
        if not SMTP_CONFIG["ENABLED"]:
            st.error("وظيفة إرسال البريد الإلكتروني معطلة في الإعدادات (SMTP_CONFIG).")
            self.add_notification("وظيفة إرسال البريد الإلكتروني معطلة.", "warning")
            return

        try:
            # This is a simplified email sending example.
            # In a real application, you'd generate the report content (e.g., PDF)
            # and attach it to the email.
            msg = MIMEMultipart()
            msg['From'] = SMTP_CONFIG["SENDER_EMAIL"]
            msg['To'] = recipient
            msg['Subject'] = subject

            body = f"مرحباً،\n\nيرجى الاطلاع على تقرير السلامة والامتثال المجدول.\n\nنوع الجدولة: {schedule_type}\n\nمع خالص التحيات،\nفريق {APP_TITLE}"
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # Placeholder for attaching a report (e.g., PDF)
            # if report_content_buffer:
            #     part = MIMEBase('application', 'octet-stream')
            #     part.set_payload(report_content_buffer.getvalue())
            #     encoders.encode_base64(part)
            #     part.add_header('Content-Disposition', f"attachment; filename=safety_report.pdf")
            #     msg.attach(part)

            with smtplib.SMTP(SMTP_CONFIG["HOST"], SMTP_CONFIG["PORT"]) as server:
                server.starttls()
                server.login(SMTP_CONFIG["USERNAME"], SMTP_CONFIG["PASSWORD"])
                server.send_message(msg)

            st.success(f"تم جدولة التقرير للإرسال إلى {recipient} ({schedule_type}).")
            self.add_notification(f"تم جدولة تقرير {schedule_type} إلى {recipient}", "success")

        except Exception as e:
            st.error(f"خطأ في إرسال البريد الإلكتروني: {str(e)}")
            self.add_notification(f"فشل في إرسال التقرير عبر البريد: {str(e)}", "error")
    
    # Removed create_analytics_insights and generate_insights as this logic belongs to DashboardAnalyzer

    def create_real_time_monitoring(self, unified_data: dict):
        """Create real-time monitoring dashboard with simulated data."""
        st.markdown("### 📡 المراقبة في الوقت الفعلي")
        
        # Auto-refresh option (handled by app.py's main loop if enabled globally)
        st.info("🔄 هذه الميزة تقوم بمحاكاة التحديثات في الوقت الفعلي.")
        
        # Simulate real-time data
        # Using a simple loop that updates values
        col1, col2, col3 = st.columns(3)
        
        # Generate new random numbers on each rerun (which happens with auto-refresh)
        with col1:
            st.metric("الحالات الجديدة", np.random.randint(0, 10))
        
        with col2:
            st.metric("التحديثات", np.random.randint(0, 5))
        
        with col3:
            st.metric("التنبيهات", np.random.randint(0, 3))
        
        # Recent activity feed (static for demo)
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
                background-color: {COLORS['light']};
                padding: 0.5rem;
                margin: 0.5rem 0;
                border-radius: 0.25rem;
                border-left: 3px solid {COLORS['info']};
            ">
                <strong>{activity['action']}</strong><br>
                <small>بواسطة {activity['user']} • {activity['time']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    def create_collaboration_features(self):
        """Create collaboration and sharing features."""
        st.markdown("### 👥 التعاون والمشاركة")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💬 التعليقات")
            
            # Comments system
            if 'comments' not in st.session_state:
                st.session_state.comments = []
            
            new_comment = st.text_area("إضافة تعليق", key="new_comment_area")
            if st.button("إضافة التعليق", key="add_comment_button"):
                if new_comment:
                    comment = {
                        'id': len(st.session_state.comments),
                        'text': new_comment,
                        'author': st.session_state.user_preferences.get('name', 'المستخدم الحالي'), # Use user name if available
                        'timestamp': datetime.now(),
                        'replies': [] # Placeholder for future reply functionality
                    }
                    st.session_state.comments.append(comment)
                    self.add_notification("تم إضافة التعليق بنجاح", "success")
                    st.rerun() # Rerun to clear text area and show new comment
            
            # Display comments (most recent first)
            if st.session_state.comments:
                st.markdown("---")
                st.markdown("**التعليقات السابقة:**")
                for comment in reversed(st.session_state.comments[-5:]): # Show last 5, reversed for newest first
                    with st.expander(f"تعليق من {comment['author']} في {comment['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                        st.write(comment['text'])
                        # Could add reply button here in future
            else:
                st.info("لا توجد تعليقات حتى الآن.")
        
        with col2:
            st.markdown("#### 🔗 المشاركة")
            
            # Share dashboard URL (placeholder)
            share_url = "https://your-dashboard-url.com/shared/12345" # Replace with actual share URL
            st.text_input("رابط المشاركة", value=share_url, key="share_url_input", disabled=True) # Disabled as it's a placeholder
            
            if st.button("نسخ الرابط", key="copy_link_button"):
                st.code(share_url, language="text") # Display URL for manual copy
                st.success("تم نسخ الرابط إلى الحافظة!") # This is client-side, Streamlit doesn't directly copy to clipboard
                self.add_notification("تم نسخ رابط المشاركة", "info")
            
            # Share via email (requires SMTP_CONFIG to be enabled)
            st.markdown("**مشاركة عبر البريد الإلكتروني:**")
            share_email = st.text_input("البريد الإلكتروني", key="share_email_input")
            share_message = st.text_area("رسالة إضافية", key="share_message_area")
            
            if st.button("إرسال الدعوة", key="send_invite_button"):
                if share_email:
                    if SMTP_CONFIG["ENABLED"]:
                        # Simulate sending email with dashboard link
                        self._send_share_email(share_email, share_message, share_url)
                    else:
                        st.warning("وظيفة إرسال البريد الإلكتروني معطلة في الإعدادات (SMTP_CONFIG).")
                        self.add_notification("وظيفة إرسال البريد الإلكتروني معطلة.", "warning")
                else:
                    st.error("يرجى إدخال البريد الإلكتروني للمستلم.")
                    self.add_notification("يرجى إدخال البريد الإلكتروني للمستلم.", "error")

    def _send_share_email(self, recipient: str, message: str, share_url: str):
        """Internal function to send a share email."""
        try:
            msg = MIMEMultipart()
            msg['From'] = SMTP_CONFIG["SENDER_EMAIL"]
            msg['To'] = recipient
            msg['Subject'] = f"دعوة لمراجعة لوحة تحكم {APP_TITLE}"

            body = f"مرحباً،\n\nأود دعوتك لمراجعة لوحة تحكم السلامة والامتثال. يمكنك الوصول إليها عبر الرابط التالي:\n{share_url}\n\n{message}\n\nمع خالص التحيات،\n{st.session_state.user_preferences.get('name', 'المستخدم الحالي')}"
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            with smtplib.SMTP(SMTP_CONFIG["HOST"], SMTP_CONFIG["PORT"]) as server:
                server.starttls()
                server.login(SMTP_CONFIG["USERNAME"], SMTP_CONFIG["PASSWORD"])
                server.send_message(msg)

            st.success(f"تم إرسال دعوة إلى {recipient}.")
            self.add_notification(f"تم إرسال دعوة مشاركة إلى {recipient}", "success")
        except Exception as e:
            st.error(f"فشل إرسال الدعوة إلى {recipient}: {str(e)}")
            self.add_notification(f"فشل إرسال الدعوة: {str(e)}", "error")
    
    def create_help_system(self):
        """Create comprehensive help system in the sidebar."""
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ❓ المساعدة")
        
        help_topics = {
            "البدء السريع": "كيفية استخدام لوحة المعلومات",
            "المرشحات": "كيفية استخدام المرشحات المتقدمة",
            "التصدير": "كيفية تصدير البيانات والتقارير",
            "المظاهر": "كيفية تغيير مظهر التطبيق",
            "الإشعارات": "إدارة الإشعارات والتنبيهات"
        }
        
        selected_topic = st.sidebar.selectbox(
            "اختر موضوع المساعدة", 
            list(help_topics.keys()),
            index=list(help_topics.keys()).index(st.session_state.get('help_topic', 'البدء السريع')),
            key="help_topic_select"
        )
        
        if st.sidebar.button("عرض المساعدة", key="show_help_button_sidebar"):
            st.session_state.show_help = True
            st.session_state.help_topic = selected_topic
            # No rerun here, app.py will handle displaying help content based on session state
    
    def show_help_content(self):
        """Show help content for the selected topic in the main area."""
        if not st.session_state.get('show_help', False):
            return # Don't show if not requested

        topic = st.session_state.get('help_topic', 'البدء السريع')
        st.markdown("### ❓ المساعدة والدعم")
        
        help_content = {
            "البدء السريع": """
            ## 🚀 البدء السريع
            
            مرحباً بك في لوحة معلومات السلامة والامتثال!
            
            ### الخطوات الأولى:
            1. **استكشف البيانات**: ابدأ بمراجعة المؤشرات الرئيسية في الصفحة الرئيسية.
            2. **استخدم المرشحات**: استخدم المرشحات في الشريط الجانبي لتخصيص العرض.
            3. **تفاعل مع الرسوم البيانية**: انقر على الرسوم البيانية للحصول على تفاصيل أكثر.
            4. **صدّر البيانات**: استخدم مركز التصدير لحفظ التقارير.
            
            ### نصائح مفيدة:
            - استخدم البحث النصي في المرشحات للعثور على بيانات محددة.
            - فعّل الإشعارات لتلقي التحديثات المهمة.
            - جرب المظاهر المختلفة لتخصيص التجربة.
            """,
            
            "المرشحات": """
            ## 🔍 استخدام المرشحات
            
            ### أنواع المرشحات المتاحة:
            
            #### 📅 مرشح التاريخ
            - اختر نطاق زمني محدد لعرض البيانات.
            - يمكن تحديد تاريخ البداية والنهاية.
            
            #### 🏢 مرشح القطاعات
            - اختر قطاع واحد أو أكثر.
            - يؤثر على جميع الرسوم البيانية والجداول.
            
            #### 📊 مرشح الحالة
            - فلترة حسب الحالة (مفتوح/مغلق/قيد المراجعة/مكتمل).
            - مفيد لتتبع الامتثال.
            
            #### ⚡ مرشح الأولوية
            - فلترة حسب مستوى الأولوية (عالي/متوسط/منخفض).
            
            #### ⚠️ مرشح مستوى المخاطر
            - فلترة حسب مستوى المخاطر (مرتفع/متوسط/منخفض).
            
            #### 🔍 البحث النصي
            - ابحث عن كلمات أو عبارات محددة في الأعمدة النصية.
            
            ### نصائح للاستخدام:
            - استخدم عدة مرشحات معاً للحصول على رؤى دقيقة.
            - احفظ إعدادات المرشحات المفضلة لديك.
            - استخدم "مسح جميع المرشحات" للعودة للعرض الكامل.
            """,
            
            "التصدير": """
            ## 📤 تصدير البيانات والتقارير
            
            ### أنواع التصدير المتاحة:
            
            #### 📊 تصدير البيانات
            - **Excel (.xlsx)**: ملف شامل مع عدة أوراق عمل.
            - **CSV (.csv)**: ملف نصي بسيط للتحليل الخارجي (لجدول واحد).
            - **JSON (.json)**: تنسيق برمجي للتطبيقات الأخرى.
            
            #### 📄 تنزيل التقارير (PDF)
            - **PDF**: تقرير مصمم للطباعة والمشاركة (يتطلب مكتبة ReportLab).
            
            #### 📧 الإرسال التلقائي (تجريبي)
            - جدولة التقارير اليومية/الأسبوعية/الشهرية (ميزة تجريبية).
            - إرسال تلقائي عبر البريد الإلكتروني (يتطلب إعداد SMTP).
            
            ### خطوات التصدير:
            1. اذهب إلى "مركز التصدير".
            2. اختر نوع البيانات أو التقرير.
            3. حدد التنسيق المطلوب.
            4. انقر "تصدير البيانات" أو "إنشاء وتنزيل تقرير PDF".
            5. احفظ الملف أو شاركه.
            """,
            
            "المظاهر": """
            ## 🎨 تخصيص المظهر
            
            ### المظاهر المتاحة:
            
            - **المظهر الفاتح**: مناسب للاستخدام النهاري، ألوان هادئة ومريحة للعين.
            - **المظهر الداكن**: مثالي للاستخدام الليلي، يقلل إجهاد العين في الإضاءة المنخفضة.
            - **المظهر الأزرق**: مظهر مهني بألوان البحر، يركز على الثقة والاستقرار.
            - **المظهر الأخضر**: مظهر طبيعي ومريح، يرمز للنمو والتطور.
            
            ### كيفية تغيير المظهر:
            1. اذهب إلى الشريط الجانبي.
            2. ابحث عن قسم "اختيار المظهر".
            3. اختر المظهر المفضل.
            4. سيتم تطبيق التغيير فوراً.
            
            ### حفظ التفضيلات:
            - يتم حفظ اختيار المظهر تلقائياً.
            - سيتم استخدام نفس المظهر في الزيارات القادمة.
            """,
            
            "الإشعارات": """
            ## 🔔 إدارة الإشعارات
            
            ### أنواع الإشعارات:
            
            - **✅ إشعارات النجاح**: تأكيد العمليات المكتملة، نجاح التصدير أو الحفظ.
            - **⚠️ إشعارات التحذير**: تنبيهات مهمة تحتاج انتباه، بيانات ناقصة أو توصيات للتحسين.
            - **❌ إشعارات الخطأ**: مشاكل تقنية أو أخطاء، فشل في العمليات.
            - **ℹ️ إشعارات المعلومات**: معلومات عامة ونصائح، تحديثات النظام.
            
            ### إعدادات الإشعارات:
            - تفعيل/إلغاء الإشعارات من قسم "الملف الشخصي" في الشريط الجانبي.
            
            ### إدارة الإشعارات:
            - عرض الإشعارات الحديثة في الشريط الجانبي.
            - مسح الإشعارات القديمة بزر "مسح الإشعارات".
            """
        }
        
        content = help_content.get(topic, "المحتوى غير متاح")
        st.markdown(content)
        
        if st.button("إغلاق المساعدة", key="close_help_button"):
            st.session_state.show_help = False
            st.rerun() # Rerun to hide help content
    
    def create_performance_monitor(self):
        """Create performance monitoring section in the sidebar."""
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ⚡ الأداء")
        
        # Simulate performance metrics (will update on each rerun)
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
        """Clean up old notifications from session state (e.g., older than 24 hours)."""
        if st.session_state.notifications:
            cutoff_time = datetime.now() - timedelta(hours=24)
            st.session_state.notifications = [
                n for n in st.session_state.notifications 
                if n['timestamp'] > cutoff_time
            ]
    
    def create_manual_upload_section(self):
        """Create manual data upload section in the main content area."""
        st.title("📤 رفع البيانات اليدوي")
        st.markdown("---")
        
        st.info("⚠️ **ملاحظة هامة**: هذه الميزة تسمح برفع الملفات للمعاينة فقط. لدمج البيانات المرفوعة مع بيانات لوحة التحكم الرئيسية، ستحتاج إلى إعادة تشغيل التطبيق أو تطوير منطق دمج أكثر تعقيداً في DataProcessor.")

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
                    try:
                        df = pd.read_excel(file)
                        st.write(f"الأبعاد: {df.shape[0]} صف × {df.shape[1]} عمود")
                        if st.checkbox(f"معاينة {file.name}", key=f"preview_excel_{file.name}"):
                            st.dataframe(df.head())
                            
                    except Exception as e:
                        st.error(f"خطأ في قراءة الملف: {str(e)}")
                        self.add_notification(f"فشل قراءة ملف Excel: {file.name} - {str(e)}", "error")
        
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
                    try:
                        # Try different encodings for CSV
                        df = None
                        for encoding in ['utf-8', 'utf-8-sig', 'cp1256', 'iso-8859-1']:
                            try:
                                df = pd.read_csv(file, encoding=encoding)
                                break
                            except UnicodeDecodeError:
                                continue
                        if df is None:
                            raise ValueError("Failed to decode CSV with available encodings.")

                        st.write(f"الأبعاد: {df.shape[0]} صف × {df.shape[1]} عمود")
                        if st.checkbox(f"معاينة {file.name}", key=f"preview_csv_{file.name}"):
                            st.dataframe(df.head())
                            
                    except Exception as e:
                        st.error(f"خطأ في قراءة الملف: {str(e)}")
                        self.add_notification(f"فشل قراءة ملف CSV: {file.name} - {str(e)}", "error")
        
        # Data processing options (simulated for now)
        st.markdown("---")
        st.subheader("⚙️ خيارات المعالجة (محاكاة)")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            clean_data = st.checkbox("تنظيف البيانات تلقائياً", value=True, key="clean_data_checkbox")
            
        with col2:
            validate_data = st.checkbox("التحقق من جودة البيانات", value=True, key="validate_data_checkbox")
            
        with col3:
            merge_data = st.checkbox("دمج البيانات مع الموجود (يتطلب إعادة تشغيل)", value=False, key="merge_data_checkbox")
        
        if st.button("🚀 معالجة البيانات (محاكاة)", type="primary", key="process_data_button"):
            if uploaded_excel or uploaded_csv:
                with st.spinner("جاري معالجة البيانات... (محاكاة)"):
                    import time
                    time.sleep(2)
                    
                    st.success("✅ تم معالجة البيانات بنجاح! (محاكاة)")
                    self.add_notification("تم رفع ومعالجة البيانات الجديدة (محاكاة)", "success")
                    
                    st.subheader("📊 نتائج المعالجة (محاكاة)")
                    results_col1, results_col2, results_col3 = st.columns(3)
                    
                    with results_col1:
                        st.metric("الملفات المعالجة", len(uploaded_excel or []) + len(uploaded_csv or []))
                    
                    with results_col2:
                        st.metric("الأخطاء المكتشفة", np.random.randint(0, 5))
                    
                    with results_col3:
                        st.metric("البيانات المضافة", f"{np.random.randint(100, 1000)} صف")
                        
                    if merge_data:
                        st.warning("⚠️ لدمج البيانات فعلياً، ستحتاج إلى إعادة تشغيل التطبيق بعد الرفع الناجح.")
                        self.add_notification("لدمج البيانات فعلياً، أعد تشغيل التطبيق.", "warning")
            else:
                st.warning("⚠️ يرجى رفع ملف واحد على الأقل للمعاينة/المعالجة.")
                self.add_notification("يرجى رفع ملف واحد على الأقل للمعالجة.", "warning")
        
        # Data quality report (simulated for now)
        st.markdown("---")
        st.subheader("📋 تقرير جودة البيانات (محاكاة)")
        
        if st.button("إنشاء تقرير الجودة (محاكاة)", key="generate_quality_report_button_manual"):
            with st.spinner("جاري إنشاء التقرير... (محاكاة)"):
                import time
                time.sleep(1)
                
                quality_data = {
                    'المقياس': ['اكتمال البيانات', 'دقة البيانات', 'اتساق البيانات', 'صحة التنسيق'],
                    'النتيجة': [95, 88, 92, 97],
                    'الحالة': ['ممتاز', 'جيد', 'جيد جداً', 'ممتاز']
                }
                
                quality_df = pd.DataFrame(quality_data)
                st.dataframe(quality_df, use_container_width=True)
                
                fig = px.bar(
                    quality_df, 
                    x='المقياس', 
                    y='النتيجة',
                    title='مؤشرات جودة البيانات (محاكاة)',
                    color='النتيجة',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
                self.add_notification("تم إنشاء تقرير الجودة (محاكاة)", "success")

