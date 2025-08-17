"""
Font configuration for ReportLab PDF generation
"""

import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def register_fonts():
    """Register custom fonts for use with ReportLab"""
    try:
        fonts_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts')
        
        # Register Noto Sans Arabic font
        pdfmetrics.registerFont(TTFont('NotoSansArabic', os.path.join(fonts_dir, 'NotoSansArabic-Regular.ttf')))
        pdfmetrics.registerFont(TTFont('NotoSansArabic-Bold', os.path.join(fonts_dir, 'NotoSansArabic-Bold.ttf')))
        
        return True
    except Exception as e:
        print(f"Error registering fonts: {str(e)}")
        return False

def get_font_config():
    """Get font configuration for ReportLab"""
    return {
        'normal': 'NotoSansArabic',
        'bold': 'NotoSansArabic-Bold',
        'default_size': 12,
        'title_size': 24,
        'heading_size': 16,
        'subheading_size': 14,
    }
