"""
Advanced Filters Component for the Safety & Compliance Dashboard
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import settings from the config module
from src.config.settings import SECTORS, STATUS_OPTIONS, PRIORITY_OPTIONS, RISK_LEVELS, COLORS

# Helper function for unique keys (assuming it's in utils.helpers)
# If utils.helpers is not in sys.path, you might need to adjust the import or define it here.
try:
    from src.utils.helpers import generate_unique_key
except ImportError:
    # Fallback for local testing if helpers is not available
    def generate_unique_key(widget_id: str) -> str:
        """Generates a unique key for Streamlit widgets."""
        return f"{widget_id}_{st.session_state.get('run_id', 0)}"


class AdvancedFilters:
    def __init__(self):
        # Filters will be collected and returned by create_complete_filter_system
        pass
        
    def create_filter_header(self, theme: Dict[str, str]):
        """Create modern filter header with dynamic theme colors."""
        st.sidebar.markdown(f"""
        <div style='text-align: center; padding: 0.5rem; background: {theme['primary_color']}15; 
                    border-radius: 8px; margin-bottom: 1rem; border: 1px solid {theme['primary_color']}25;'>
            <h3 style='margin: 0; color: {theme['primary_color']}; font-weight: bold; text-shadow: 0 0 1px {theme["primary_color"]}30;'>🔍 المرشحات المتقدمة</h3>
        </div>
        """, unsafe_allow_html=True)
    
    def create_filter_presets_section(self, current_filters: Dict[str, Any]):
        """
        Create filter presets management section.
        Loads selected preset into session state to update filter widgets.
        """
        with st.sidebar.expander("⚙️ إعدادات المرشحات", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ مسح جميع المرشحات", key=generate_unique_key("clear_all_filters")):
                    self._clear_all_filters()
                    st.rerun() # Rerun to apply cleared filters
            
            with col2:
                saved_presets = self._get_saved_filter_presets()
                preset_options = [""] + list(saved_presets.keys())
                
                # Determine default selection for the selectbox
                # If a preset was just loaded, its name should be selected
                # Otherwise, it should be empty
                default_preset_index = 0
                if 'last_loaded_preset' in st.session_state and st.session_state.last_loaded_preset in preset_options:
                    default_preset_index = preset_options.index(st.session_state.last_loaded_preset)

                selected_preset_name = st.selectbox(
                    "تحميل مرشح محفوظ", 
                    preset_options,
                    index=default_preset_index,
                    key=generate_unique_key("load_filter_preset")
                )
                
                if selected_preset_name and selected_preset_name != "":
                    loaded_filters = saved_presets[selected_preset_name]
                    self._apply_preset_to_session_state(loaded_filters)
                    st.session_state.last_loaded_preset = selected_preset_name # Store for default selection
                    st.success(f"تم تحميل المرشح: {selected_preset_name}")
                    st.rerun() # Rerun to apply loaded filters to widgets

    def _apply_preset_to_session_state(self, preset_filters: Dict[str, Any]):
        """Applies loaded preset values to session state variables for filter widgets."""
        # Date range
        if 'date_range' in preset_filters and preset_filters['date_range']:
            # Convert string dates back to datetime.date objects
            start_date_str, end_date_str = preset_filters['date_range']
            st.session_state.date_range_filter = (datetime.fromisoformat(start_date_str).date(), datetime.fromisoformat(end_date_str).date())
        else:
            # Reset date filter if not in preset
            if 'date_range_filter' in st.session_state:
                del st.session_state.date_range_filter

        # Sectors
        if 'sectors' in preset_filters:
            st.session_state.selected_sectors = preset_filters['sectors']
        else:
            if 'selected_sectors' in st.session_state:
                del st.session_state.selected_sectors

        # Status
        if 'status' in preset_filters:
            st.session_state.selected_status = preset_filters['status']
        else:
            if 'selected_status' in st.session_state:
                del st.session_state.selected_status

        # Priority
        if 'priority' in preset_filters:
            st.session_state.selected_priority = preset_filters['priority']
        else:
            if 'selected_priority' in st.session_state:
                del st.session_state.selected_priority

        # Risk Level
        if 'risk_level' in preset_filters:
            st.session_state.selected_risk = preset_filters['risk_level']
        else:
            if 'selected_risk' in st.session_state:
                del st.session_state.selected_risk

        # Text Search
        if 'search_query' in preset_filters:
            st.session_state.text_search = preset_filters['search_query']
        else:
            if 'text_search' in st.session_state:
                del st.session_state.text_search
        
        # Numeric range filters would need similar handling if implemented
        # For now, assuming they are not part of presets or are reset on load.

    def create_date_filter(self, min_date_global: datetime, max_date_global: datetime) -> Optional[tuple]:
        """Create date range filter with global min/max bounds and presets."""
        st.sidebar.markdown("#### 📅 نطاق التاريخ")
        
        # Ensure min_date_global and max_date_global are datetime.date objects
        min_date_global_date = min_date_global.date() if isinstance(min_date_global, datetime) else min_date_global
        max_date_global_date = max_date_global.date() if isinstance(max_date_global, datetime) else max_date_global

        # Determine current value for date_input based on session state or global range
        # Ensure the value is within the min/max bounds to avoid StreamlitAPIException
        current_date_value_start = st.session_state.get('date_range_filter', (min_date_global_date, max_date_global_date))[0]
        current_date_value_end = st.session_state.get('date_range_filter', (min_date_global_date, max_date_global_date))[1]

        # Adjust current_date_value to be within global bounds if it falls outside
        if current_date_value_start < min_date_global_date:
            current_date_value_start = min_date_global_date
        if current_date_value_end > max_date_global_date:
            current_date_value_end = max_date_global_date
        if current_date_value_start > current_date_value_end: # Handle case where start date somehow becomes after end date
            current_date_value_start = min_date_global_date
            current_date_value_end = max_date_global_date


        date_range = st.sidebar.date_input(
            "اختر النطاق الزمني",
            value=(current_date_value_start, current_date_value_end),
            min_value=min_date_global_date,
            max_value=max_date_global_date,
            key=generate_unique_key("date_range_filter")
        )
        
        # Update session state with current selection
        st.session_state.date_range_filter = date_range

        return date_range if date_range and len(date_range) == 2 else None
    
    def create_sector_filter(self, available_sectors: List[str]) -> List[str]:
        """Create sector filter with select all/none functionality."""
        st.sidebar.markdown("#### 🏢 القطاعات")
        
        # Ensure available_sectors is not empty, fallback to predefined if necessary
        if not available_sectors:
            available_sectors = SECTORS
        
        # Select all/none buttons
        col1, col2 = st.sidebar.columns(2)
        with col1:
            # Use a callback for select all/none to avoid immediate rerun and ensure state consistency
            st.button("✅ تحديد الكل", key=generate_unique_key("select_all_sectors"), 
                      on_click=lambda: st.session_state.__setitem__('selected_sectors', available_sectors))
        
        with col2:
            st.button("❌ إلغاء الكل", key=generate_unique_key("deselect_all_sectors"), 
                      on_click=lambda: st.session_state.__setitem__('selected_sectors', []))
        
        # Multi-select for sectors
        # Default value comes from session state, which is updated by buttons or presets
        selected_sectors = st.sidebar.multiselect(
            "اختر القطاعات",
            available_sectors,
            default=st.session_state.get('selected_sectors', []), # Default to empty list if not set
            key=generate_unique_key("sector_multiselect")
        )
        
        # Update session state with current selection (important for persistence across reruns)
        st.session_state.selected_sectors = selected_sectors
        
        return selected_sectors
    
    def create_status_filter(self) -> List[str]:
        """Create status filter with multiple selection."""
        st.sidebar.markdown("#### 📊 الحالة")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.button("✅ كل الحالات", key=generate_unique_key("select_all_status"),
                      on_click=lambda: st.session_state.__setitem__('selected_status', STATUS_OPTIONS))
        
        with col2:
            st.button("❌ مسح الحالات", key=generate_unique_key("clear_all_status"),
                      on_click=lambda: st.session_state.__setitem__('selected_status', []))
        
        selected_status = st.sidebar.multiselect(
            "اختر الحالات",
            STATUS_OPTIONS,
            default=st.session_state.get('selected_status', ["الكل"]), # Default to "الكل" if not set
            key=generate_unique_key("status_multiselect")
        )
        
        st.session_state.selected_status = selected_status
        return selected_status
    
    def create_priority_filter(self) -> str:
        """Create priority filter."""
        st.sidebar.markdown("#### ⚡ الأولوية")
        
        selected_priority = st.sidebar.selectbox(
            "مستوى الأولوية",
            PRIORITY_OPTIONS,
            index=PRIORITY_OPTIONS.index(st.session_state.get('selected_priority', "الكل")),
            key=generate_unique_key("priority_filter")
        )
        
        st.session_state.selected_priority = selected_priority
        return selected_priority
    
    def create_risk_level_filter(self) -> str:
        """Create risk level filter."""
        st.sidebar.markdown("#### ⚠️ مستوى المخاطر")
        
        selected_risk = st.sidebar.selectbox(
            "مستوى المخاطر",
            RISK_LEVELS,
            index=RISK_LEVELS.index(st.session_state.get('selected_risk', "الكل")),
            key=generate_unique_key("risk_level_filter")
        )
        
        st.session_state.selected_risk = selected_risk
        return selected_risk
    
    def create_text_search_filter(self) -> str:
        """Create text search filter."""
        st.sidebar.markdown("#### 🔍 البحث النصي")
        
        search_query = st.sidebar.text_input(
            "ابحث في البيانات",
            placeholder="أدخل كلمة البحث...",
            value=st.session_state.get('text_search', ''),
            key=generate_unique_key("text_search")
        )
        
        st.session_state.text_search = search_query
        return search_query
    
    def create_numeric_range_filter(self, column_name: str, min_val: float, 
                                  max_val: float, step: float = 1.0) -> tuple:
        """Create numeric range filter."""
        st.sidebar.markdown(f"#### 🔢 نطاق {column_name}")
        
        # Ensure a unique key for each numeric range filter based on column_name
        slider_key = generate_unique_key(f"numeric_range_{column_name}")
        
        # Initialize session state for this specific slider if not present
        if slider_key not in st.session_state:
            st.session_state[slider_key] = (min_val, max_val)

        range_values = st.sidebar.slider(
            f"اختر نطاق {column_name}",
            min_value=min_val,
            max_value=max_val,
            value=st.session_state[slider_key], # Use session state value
            step=step,
            key=slider_key
        )
        
        st.session_state[slider_key] = range_values # Update session state
        return range_values
    
    def create_save_preset_section(self, current_filters: Dict[str, Any]):
        """Create section to save current filter preset."""
        st.sidebar.markdown("---")
        with st.sidebar.expander("💾 حفظ المرشح الحالي"):
            preset_name = st.text_input(
                "اسم المرشح", 
                key=generate_unique_key("preset_name_input")
            )
            
            if st.button("حفظ", key=generate_unique_key("save_filter_preset")) and preset_name:
                self._save_filter_preset(preset_name, current_filters)
                st.success(f"تم حفظ المرشح: {preset_name}")
                # No rerun here, as it's just saving state. User can load it later.
    
    def create_complete_filter_system(self, unified_data: Dict[str, pd.DataFrame], kpi_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create the complete filter system in the sidebar.
        This is the main entry point for app.py to call.
        """
        theme = st.session_state.current_theme_config # Get current theme
        self.create_filter_header(theme)
        
        if not unified_data:
            st.sidebar.info("لا توجد بيانات متاحة للتصفية")
            return {}
        
        # Initialize filters dictionary to return
        filters = {}
        
        # Filter presets section (handles loading presets into session state)
        self.create_filter_presets_section(filters) # Pass filters to allow saving current state

        # Determine global date range from kpi_data
        min_date_global = datetime.now() - timedelta(days=365) # Default fallback
        max_date_global = datetime.now() # Default fallback

        if kpi_data:
            all_min_dates = []
            all_max_dates = []
            for kpi_type, kpi_info in kpi_data.items():
                if kpi_info and kpi_info.get('date_range'):
                    if kpi_info['date_range'].get('min_date') and pd.notna(kpi_info['date_range']['min_date']):
                        all_min_dates.append(kpi_info['date_range']['min_date'])
                    if kpi_info['date_range'].get('max_date') and pd.notna(kpi_info['date_range']['max_date']):
                        all_max_dates.append(kpi_info['date_range']['max_date'])
            
            if all_min_dates:
                min_date_global = min(all_min_dates)
            if all_max_dates:
                max_date_global = max(all_max_dates)
        
        # Date range filter
        date_range = self.create_date_filter(min_date_global, max_date_global)
        if date_range:
            filters['date_range'] = date_range
        
        # Extract available sectors from unified data
        available_sectors = self._extract_available_sectors(unified_data)
        
        # Sector filter
        selected_sectors = self.create_sector_filter(available_sectors)
        if selected_sectors:
            filters['sectors'] = selected_sectors
        
        # Status filter
        selected_status = self.create_status_filter()
        if selected_status and "الكل" not in selected_status: # Only add if not "الكل" selected
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
        
        # Example numeric range filter (can be extended based on actual data columns)
        # if 'نسبة_المخاطرة' in unified_data.get('risk_assessments', pd.DataFrame()).columns:
        #     risk_percentage_df = unified_data['risk_assessments']['نسبة_المخاطرة'].dropna()
        #     if not risk_percentage_df.empty:
        #         min_risk_perc = float(risk_percentage_df.min())
        #         max_risk_perc = float(risk_percentage_df.max())
        #         selected_risk_perc_range = self.create_numeric_range_filter(
        #             "نسبة المخاطرة", min_risk_perc, max_risk_perc, step=0.01
        #         )
        #         filters['risk_percentage_range'] = selected_risk_perc_range

        # Save current filters
        self.create_save_preset_section(filters)
        
        # Display active filters summary
        self._display_active_filters_summary(filters)
        
        return filters
    
    def _extract_available_sectors(self, unified_data: Dict[str, pd.DataFrame]) -> List[str]:
        """Extract available sectors from unified data using standardized column names."""
        available_sectors = set()
        
        for df_type, df in unified_data.items():
            if not df.empty:
                if 'الإدارة' in df.columns:
                    available_sectors.update(df['الإدارة'].dropna().unique())
                elif 'القطاع' in df.columns:
                    available_sectors.update(df['القطاع'].dropna().unique())
        
        return sorted(list(available_sectors)) if available_sectors else SECTORS
    
    def _display_active_filters_summary(self, filters: Dict[str, Any]):
        """Display summary of active filters in the sidebar."""
        st.sidebar.markdown("---")
        st.sidebar.markdown("#### 📋 المرشحات النشطة")
        
        active_count = 0
        for key, value in filters.items():
            if value and (isinstance(value, list) and "الكل" not in value and value or \
                          isinstance(value, str) and value != "الكل" and value or \
                          isinstance(value, tuple) and value): # Check for non-empty/non-"الكل" values
                active_count += 1
                if key == 'date_range':
                    st.sidebar.markdown(f"📅 **التاريخ:** {value[0].strftime('%Y-%m-%d')} إلى {value[1].strftime('%Y-%m-%d')}")
                elif key == 'sectors':
                    st.sidebar.markdown(f"🏢 **القطاعات:** {len(value)} محدد")
                elif key == 'status':
                    st.sidebar.markdown(f"📊 **الحالة:** {', '.join(value)}")
                elif key == 'search_query':
                    st.sidebar.markdown(f"🔍 **البحث:** '{value}'")
                elif key == 'priority':
                    st.sidebar.markdown(f"⚡ **الأولوية:** {value}")
                elif key == 'risk_level':
                    st.sidebar.markdown(f"⚠️ **مستوى المخاطر:** {value}")
                else:
                    st.sidebar.markdown(f"**{key}:** {value}")
        
        if active_count == 0:
            st.sidebar.info("لا توجد مرشحات نشطة")
        else:
            st.sidebar.success(f"عدد المرشحات النشطة: {active_count}")
    
    def _get_saved_filter_presets(self) -> Dict[str, Any]:
        """Get saved filter presets from session state."""
        return st.session_state.get('filter_presets', {})
    
    def _save_filter_preset(self, name: str, filters: Dict[str, Any]):
        """Save filter preset to session state, converting dates to strings for serialization."""
        if 'filter_presets' not in st.session_state:
            st.session_state.filter_presets = {}
        
        serializable_filters = {}
        for key, value in filters.items():
            if key == 'date_range' and value and isinstance(value[0], datetime):
                serializable_filters[key] = (value[0].isoformat(), value[1].isoformat())
            elif key == 'date_range' and value and isinstance(value[0], datetime.date): # Handle date objects
                serializable_filters[key] = (value[0].isoformat(), value[1].isoformat())
            else:
                serializable_filters[key] = value
        
        st.session_state.filter_presets[name] = serializable_filters
    
    def _clear_all_filters(self):
        """Clear all active filters by resetting relevant session state keys."""
        # Keys for standard filters
        filter_keys = [
            'date_range_filter', # For date_input widget
            'selected_sectors', 
            'selected_status', 
            'selected_priority',
            'selected_risk', # Corrected from selected_risk_level
            'text_search', # For text_input widget
            'last_loaded_preset' # Clear last loaded preset name
        ]
        
        # Clear numeric range sliders if they were implemented with dynamic keys
        # This part assumes a naming convention for numeric slider keys
        for key in list(st.session_state.keys()):
            if key.startswith('numeric_range_'):
                filter_keys.append(key)

        for key in filter_keys:
            if key in st.session_state:
                del st.session_state[key]

