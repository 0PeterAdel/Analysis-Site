"""
Advanced Filters Component for the Safety & Compliance Dashboard
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sys
import os

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from config.settings import SECTORS, STATUS_OPTIONS, PRIORITY_OPTIONS, RISK_LEVELS
from utils.helpers import generate_unique_key

class AdvancedFilters:
    def __init__(self):
        self.filters = {}
        
    def create_filter_header(self):
        """Create modern filter header"""
        st.sidebar.markdown("""
        <div style='text-align: center; padding: 0.5rem; background: #f0f2f6; 
                    border-radius: 8px; margin-bottom: 1rem;'>
            <h3 style='margin: 0; color: #1f77b4;'>🔍 المرشحات المتقدمة</h3>
        </div>
        """, unsafe_allow_html=True)
    
    def create_filter_presets_section(self) -> Dict[str, Any]:
        """Create filter presets management section"""
        filters = {}
        
        with st.sidebar.expander("⚙️ إعدادات المرشحات", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ مسح جميع المرشحات", key=generate_unique_key("clear_all_filters")):
                    self._clear_all_filters()
                    st.rerun()
            
            with col2:
                saved_presets = self._get_saved_filter_presets()
                if saved_presets:
                    selected_preset = st.selectbox(
                        "تحميل مرشح محفوظ", 
                        [""] + list(saved_presets.keys()),
                        key=generate_unique_key("load_filter_preset")
                    )
                    if selected_preset:
                        filters.update(saved_presets[selected_preset])
                        st.success(f"تم تحميل المرشح: {selected_preset}")
        
        return filters
    
    def create_date_filter(self) -> Optional[tuple]:
        """Create date range filter"""
        st.sidebar.markdown("#### 📅 نطاق التاريخ")
        
        # Preset date ranges
        date_presets = {
            "آخر 7 أيام": (datetime.now() - timedelta(days=7), datetime.now()),
            "آخر 30 يوم": (datetime.now() - timedelta(days=30), datetime.now()),
            "آخر 3 أشهر": (datetime.now() - timedelta(days=90), datetime.now()),
            "آخر سنة": (datetime.now() - timedelta(days=365), datetime.now()),
            "مخصص": None
        }
        
        selected_preset = st.sidebar.selectbox(
            "اختر نطاق زمني",
            list(date_presets.keys()),
            key=generate_unique_key("date_preset")
        )
        
        if selected_preset == "مخصص":
            date_range = st.sidebar.date_input(
                "اختر النطاق الزمني المخصص",
                value=(datetime.now() - timedelta(days=30), datetime.now()),
                key=generate_unique_key("custom_date_range")
            )
        else:
            date_range = date_presets[selected_preset]
        
        return date_range if date_range and len(date_range) == 2 else None
    
    def create_sector_filter(self, available_sectors: List[str]) -> List[str]:
        """Create sector filter with select all/none functionality"""
        st.sidebar.markdown("#### 🏢 القطاعات")
        
        if not available_sectors:
            available_sectors = SECTORS
        
        # Select all/none buttons
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("✅ تحديد الكل", key=generate_unique_key("select_all_sectors")):
                st.session_state.selected_sectors = available_sectors
                st.rerun()
        
        with col2:
            if st.button("❌ إلغاء الكل", key=generate_unique_key("deselect_all_sectors")):
                st.session_state.selected_sectors = []
                st.rerun()
        
        # Multi-select for sectors
        default_sectors = st.session_state.get('selected_sectors', available_sectors[:3])
        selected_sectors = st.sidebar.multiselect(
            "اختر القطاعات",
            available_sectors,
            default=default_sectors,
            key=generate_unique_key("sector_multiselect")
        )
        
        # Update session state
        st.session_state.selected_sectors = selected_sectors
        
        return selected_sectors
    
    def create_status_filter(self) -> List[str]:
        """Create status filter with multiple selection"""
        st.sidebar.markdown("#### 📊 الحالة")
        
        # Select all/none for status
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("✅ كل الحالات", key=generate_unique_key("select_all_status")):
                st.session_state.selected_status = STATUS_OPTIONS
                st.rerun()
        
        with col2:
            if st.button("❌ مسح الحالات", key=generate_unique_key("clear_all_status")):
                st.session_state.selected_status = []
                st.rerun()
        
        default_status = st.session_state.get('selected_status', ["الكل"])
        selected_status = st.sidebar.multiselect(
            "اختر الحالات",
            STATUS_OPTIONS,
            default=default_status,
            key=generate_unique_key("status_multiselect")
        )
        
        st.session_state.selected_status = selected_status
        return selected_status
    
    def create_priority_filter(self) -> str:
        """Create priority filter"""
        st.sidebar.markdown("#### ⚡ الأولوية")
        
        selected_priority = st.sidebar.selectbox(
            "مستوى الأولوية",
            PRIORITY_OPTIONS,
            key=generate_unique_key("priority_filter")
        )
        
        return selected_priority
    
    def create_risk_level_filter(self) -> str:
        """Create risk level filter"""
        st.sidebar.markdown("#### ⚠️ مستوى المخاطر")
        
        selected_risk = st.sidebar.selectbox(
            "مستوى المخاطر",
            RISK_LEVELS,
            key=generate_unique_key("risk_level_filter")
        )
        
        return selected_risk
    
    def create_text_search_filter(self) -> str:
        """Create text search filter"""
        st.sidebar.markdown("#### 🔍 البحث النصي")
        
        search_query = st.sidebar.text_input(
            "ابحث في البيانات",
            placeholder="أدخل كلمة البحث...",
            key=generate_unique_key("text_search")
        )
        
        return search_query
    
    def create_numeric_range_filter(self, column_name: str, min_val: float, 
                                  max_val: float, step: float = 1.0) -> tuple:
        """Create numeric range filter"""
        st.sidebar.markdown(f"#### 🔢 نطاق {column_name}")
        
        range_values = st.sidebar.slider(
            f"اختر نطاق {column_name}",
            min_value=min_val,
            max_value=max_val,
            value=(min_val, max_val),
            step=step,
            key=generate_unique_key(f"numeric_range_{column_name}")
        )
        
        return range_values
    
    def create_save_preset_section(self, current_filters: Dict[str, Any]):
        """Create section to save current filter preset"""
        st.sidebar.markdown("---")
        with st.sidebar.expander("💾 حفظ المرشح الحالي"):
            preset_name = st.text_input(
                "اسم المرشح", 
                key=generate_unique_key("preset_name_input")
            )
            
            if st.button("حفظ", key=generate_unique_key("save_filter_preset")) and preset_name:
                self._save_filter_preset(preset_name, current_filters)
                st.success(f"تم حفظ المرشح: {preset_name}")
                st.rerun()
    
    def create_complete_filter_system(self, unified_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Create complete filter system"""
        self.create_filter_header()
        
        if not unified_data:
            st.sidebar.info("لا توجد بيانات متاحة للتصفية")
            return {}
        
        # Initialize filters dictionary
        filters = {}
        
        # Filter presets
        preset_filters = self.create_filter_presets_section()
        filters.update(preset_filters)
        
        # Date range filter
        date_range = self.create_date_filter()
        if date_range:
            filters['date_range'] = date_range
        
        # Get available sectors from data
        available_sectors = self._extract_available_sectors(unified_data)
        
        # Sector filter
        selected_sectors = self.create_sector_filter(available_sectors)
        if selected_sectors:
            filters['sectors'] = selected_sectors
        
        # Status filter
        selected_status = self.create_status_filter()
        if selected_status:
            filters['status'] = selected_status
        
        # Priority filter
        selected_priority = self.create_priority_filter()
        if selected_priority != "الكل":
            filters['priority'] = selected_priority
        
        # Risk level filter
        selected_risk = self.create_risk_level_filter()
        if selected_risk != "الكل":
            filters['risk_level'] = selected_risk
        
        # Text search filter
        search_query = self.create_text_search_filter()
        if search_query:
            filters['search_query'] = search_query
        
        # Save current filters
        self.create_save_preset_section(filters)
        
        # Display active filters summary
        self._display_active_filters_summary(filters)
        
        return filters
    
    def _extract_available_sectors(self, unified_data: Dict[str, pd.DataFrame]) -> List[str]:
        """Extract available sectors from unified data"""
        available_sectors = set()
        
        for dataset_name, df in unified_data.items():
            if not df.empty:
                sector_columns = [col for col in df.columns 
                                if 'قطاع' in str(col) or 'sector' in str(col).lower()]
                for col in sector_columns:
                    available_sectors.update(df[col].dropna().unique())
        
        return sorted(list(available_sectors)) if available_sectors else SECTORS
    
    def _display_active_filters_summary(self, filters: Dict[str, Any]):
        """Display summary of active filters"""
        if not filters:
            return
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("#### 📋 المرشحات النشطة")
        
        active_count = 0
        for key, value in filters.items():
            if value:
                active_count += 1
                if key == 'date_range':
                    st.sidebar.markdown(f"📅 **التاريخ:** {value[0].strftime('%Y-%m-%d')} إلى {value[1].strftime('%Y-%m-%d')}")
                elif key == 'sectors':
                    st.sidebar.markdown(f"🏢 **القطاعات:** {len(value)} محدد")
                elif key == 'status':
                    st.sidebar.markdown(f"📊 **الحالة:** {len(value)} محدد")
                elif key == 'search_query':
                    st.sidebar.markdown(f"🔍 **البحث:** {value}")
                else:
                    st.sidebar.markdown(f"**{key}:** {value}")
        
        if active_count == 0:
            st.sidebar.info("لا توجد مرشحات نشطة")
        else:
            st.sidebar.success(f"عدد المرشحات النشطة: {active_count}")
    
    def _get_saved_filter_presets(self) -> Dict[str, Any]:
        """Get saved filter presets from session state"""
        return st.session_state.get('filter_presets', {})
    
    def _save_filter_preset(self, name: str, filters: Dict[str, Any]):
        """Save filter preset to session state"""
        if 'filter_presets' not in st.session_state:
            st.session_state.filter_presets = {}
        
        # Convert date objects to strings for serialization
        serializable_filters = {}
        for key, value in filters.items():
            if key == 'date_range' and value:
                serializable_filters[key] = (value[0].isoformat(), value[1].isoformat())
            else:
                serializable_filters[key] = value
        
        st.session_state.filter_presets[name] = serializable_filters
    
    def _clear_all_filters(self):
        """Clear all active filters"""
        # Clear session state filter-related keys
        filter_keys = [
            'selected_sectors', 'selected_status', 'selected_priority',
            'selected_risk_level', 'search_query'
        ]
        
        for key in filter_keys:
            if key in st.session_state:
                del st.session_state[key]