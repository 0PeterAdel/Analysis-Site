"""
Data models and schemas for the Safety & Compliance Analytics Platform
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Union
from datetime import datetime
import pandas as pd

@dataclass
class SafetyRecord:
    """Base class for safety records"""
    record_id: str
    dataset_source: str
    date: Optional[datetime]
    status: Optional[str]
    classification: Optional[str]
    department: Optional[str]
    activity_type: Optional[str]
    unit: Optional[str]
    risk_score: Optional[float]
    compliance_score: Optional[float]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'record_id': self.record_id,
            'dataset_source': self.dataset_source,
            'date': self.date,
            'status': self.status,
            'classification': self.classification,
            'department': self.department,
            'activity_type': self.activity_type,
            'unit': self.unit,
            'risk_score': self.risk_score,
            'compliance_score': self.compliance_score
        }

@dataclass
class KPIMetrics:
    """KPI metrics container"""
    total_records: int
    total_datasets: int
    open_items: int
    closed_items: int
    in_progress_items: int
    closure_rate: float
    avg_risk_score: float
    high_risk_items: int
    risk_trend: float
    avg_compliance_score: float
    compliance_trend: float
    top_department: str
    department_count: int
    top_activity: str
    activity_diversity: int
    
    def get_summary(self) -> Dict:
        """Get summary dictionary"""
        return {
            'Total Records': self.total_records,
            'Closure Rate (%)': round(self.closure_rate, 1),
            'Average Risk Score': round(self.avg_risk_score, 2),
            'High Risk Items': self.high_risk_items,
            'Average Compliance (%)': round(self.avg_compliance_score, 1),
            'Department Count': self.department_count,
            'Activity Diversity': self.activity_diversity
        }

@dataclass
class DataQualityReport:
    """Data quality assessment report"""
    dataset_name: str
    total_records: int
    total_columns: int
    missing_values: int
    completeness_percentage: float
    duplicate_records: int
    data_types: Dict[str, int]
    outliers_detected: int
    
    def get_quality_score(self) -> float:
        """Calculate overall quality score"""
        completeness_score = self.completeness_percentage
        duplicate_penalty = (self.duplicate_records / self.total_records) * 100 if self.total_records > 0 else 0
        
        quality_score = completeness_score - duplicate_penalty
        return max(0, min(100, quality_score))

@dataclass
class AnalyticsInsight:
    """Analytics insight container"""
    insight_type: str  # 'success', 'warning', 'error', 'info'
    title: str
    message: str
    confidence: float
    data_points: int
    recommendation: Optional[str] = None
    
    def to_display_dict(self) -> Dict:
        """Convert to display format"""
        return {
            'Type': self.insight_type.title(),
            'Title': self.title,
            'Message': self.message,
            'Confidence': f"{self.confidence:.1f}%",
            'Data Points': self.data_points,
            'Recommendation': self.recommendation or 'N/A'
        }

class DataSchema:
    """Data schema definitions"""
    
    COMMON_COLUMNS = {
        'record_id': 'string',
        'dataset_source': 'string',
        'date': 'datetime64[ns]',
        'status': 'string',
        'classification': 'string',
        'department': 'string',
        'activity_type': 'string',
        'unit': 'string',
        'risk_score': 'float64',
        'compliance_score': 'float64'
    }
    
    DATASET_SCHEMAS = {
        'site_audits': {
            'الرقم': 'string',
            'الوحدة': 'string',
            'التصنيف': 'string',
            'تاريخ الملاحظة': 'datetime64[ns]',
            'تصنيف النشاط': 'string',
            'الحالة': 'string',
            'الإدارة المسئولة عن تنفيذ التوصية': 'string'
        },
        'risk_assessment': {
            'رقم الإجراء / التوصية': 'string',
            'الوحدة': 'string',
            'نسب المخاطرة': 'float64',
            'تاريخ التقييم': 'datetime64[ns]',
            'تصنيف النشاط': 'string',
            'حالة التوصية': 'string'
        },
        'contractor_audits': {
            'رقم الإجراء / التوصية': 'string',
            'الوحدة': 'string',
            'تاريخ التدقيق': 'datetime64[ns]',
            'تصنيف النشاط': 'string',
            'حالة التوصية': 'string',
            'Compliance Percentage': 'float64'
        }
    }
    
    @classmethod
    def validate_dataframe(cls, df: pd.DataFrame, schema_name: str) -> List[str]:
        """Validate dataframe against schema"""
        errors = []
        
        if schema_name not in cls.DATASET_SCHEMAS:
            errors.append(f"Unknown schema: {schema_name}")
            return errors
        
        expected_schema = cls.DATASET_SCHEMAS[schema_name]
        
        # Check for missing columns
        missing_cols = set(expected_schema.keys()) - set(df.columns)
        if missing_cols:
            errors.append(f"Missing columns: {missing_cols}")
        
        # Check data types
        for col, expected_type in expected_schema.items():
            if col in df.columns:
                actual_type = str(df[col].dtype)
                if expected_type == 'datetime64[ns]' and 'datetime' not in actual_type:
                    errors.append(f"Column {col} should be datetime, got {actual_type}")
                elif expected_type == 'float64' and not pd.api.types.is_numeric_dtype(df[col]):
                    errors.append(f"Column {col} should be numeric, got {actual_type}")
        
        return errors

class MetricsCalculator:
    """Centralized metrics calculation"""
    
    @staticmethod
    def calculate_closure_rate(status_series: pd.Series) -> float:
        """Calculate closure rate"""
        if len(status_series) == 0:
            return 0.0
        
        closed_count = (status_series == 'Closed').sum()
        total_count = len(status_series.dropna())
        
        return (closed_count / total_count * 100) if total_count > 0 else 0.0
    
    @staticmethod
    def calculate_risk_distribution(risk_series: pd.Series) -> Dict[str, int]:
        """Calculate risk level distribution"""
        if risk_series.empty:
            return {'Low': 0, 'Medium': 0, 'High': 0}
        
        risk_categories = pd.cut(
            risk_series.dropna(),
            bins=[0, 0.3, 0.7, 1.0],
            labels=['Low', 'Medium', 'High'],
            include_lowest=True
        )
        
        return risk_categories.value_counts().to_dict()
    
    @staticmethod
    def calculate_trend(series: pd.Series, periods: int = 5) -> tuple:
        """Calculate trend direction and magnitude"""
        if len(series) < periods * 2:
            return 0.0, 'insufficient_data'
        
        recent = series.tail(periods).mean()
        older = series.head(periods).mean()
        
        if older == 0:
            return 0.0, 'no_baseline'
        
        trend_pct = ((recent - older) / older) * 100
        
        if abs(trend_pct) < 5:
            direction = 'stable'
        elif trend_pct > 0:
            direction = 'increasing'
        else:
            direction = 'decreasing'
        
        return trend_pct, direction
    
    @staticmethod
    def calculate_department_performance(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate comprehensive department performance metrics"""
        dept_metrics = df.groupby('department').agg({
            'record_id': 'count',
            'status': lambda x: (x == 'Closed').sum() / len(x) * 100,
            'risk_score': 'mean',
            'compliance_score': 'mean',
            'classification': lambda x: (x == 'High').sum()
        }).round(2)
        
        dept_metrics.columns = [
            'Total Items',
            'Closure Rate (%)',
            'Avg Risk Score',
            'Avg Compliance (%)',
            'High Priority Items'
        ]
        
        return dept_metrics.fillna(0)

class InsightGenerator:
    """Automated insight generation"""
    
    @staticmethod
    def generate_closure_insights(closure_rate: float, total_items: int) -> AnalyticsInsight:
        """Generate insights about closure rates"""
        if closure_rate >= 80:
            return AnalyticsInsight(
                insight_type='success',
                title='Excellent Closure Performance',
                message=f'Outstanding closure rate of {closure_rate:.1f}% indicates strong follow-through on safety items.',
                confidence=95.0,
                data_points=total_items,
                recommendation='Maintain current processes and consider sharing best practices with other departments.'
            )
        elif closure_rate >= 60:
            return AnalyticsInsight(
                insight_type='warning',
                title='Moderate Closure Performance',
                message=f'Closure rate of {closure_rate:.1f}% suggests room for improvement in item resolution.',
                confidence=85.0,
                data_points=total_items,
                recommendation='Review closure processes and identify bottlenecks preventing timely resolution.'
            )
        else:
            return AnalyticsInsight(
                insight_type='error',
                title='Low Closure Performance',
                message=f'Low closure rate of {closure_rate:.1f}% requires immediate attention to improve safety compliance.',
                confidence=90.0,
                data_points=total_items,
                recommendation='Implement urgent action plan to address open items and improve closure processes.'
            )
    
    @staticmethod
    def generate_risk_insights(avg_risk: float, high_risk_count: int) -> AnalyticsInsight:
        """Generate insights about risk levels"""
        if avg_risk > 0.7:
            return AnalyticsInsight(
                insight_type='error',
                title='High Risk Environment',
                message=f'Average risk score of {avg_risk:.2f} with {high_risk_count} high-risk items indicates significant safety concerns.',
                confidence=95.0,
                data_points=high_risk_count,
                recommendation='Immediate risk mitigation required. Focus on high-risk items first.'
            )
        elif avg_risk > 0.4:
            return AnalyticsInsight(
                insight_type='warning',
                title='Moderate Risk Level',
                message=f'Risk score of {avg_risk:.2f} requires ongoing monitoring and preventive measures.',
                confidence=80.0,
                data_points=high_risk_count,
                recommendation='Implement proactive risk management strategies and regular monitoring.'
            )
        else:
            return AnalyticsInsight(
                insight_type='success',
                title='Low Risk Environment',
                message=f'Low risk score of {avg_risk:.2f} indicates effective safety management.',
                confidence=85.0,
                data_points=high_risk_count,
                recommendation='Continue current safety practices and maintain vigilance.'
            )
    
    @staticmethod
    def generate_trend_insights(trend_value: float, trend_direction: str, metric_name: str) -> AnalyticsInsight:
        """Generate insights about trends"""
        if trend_direction == 'increasing' and 'risk' in metric_name.lower():
            return AnalyticsInsight(
                insight_type='warning',
                title=f'Increasing {metric_name}',
                message=f'{metric_name} is trending upward by {abs(trend_value):.1f}%.',
                confidence=75.0,
                data_points=10,
                recommendation=f'Investigate causes of increasing {metric_name.lower()} and implement corrective measures.'
            )
        elif trend_direction == 'decreasing' and 'risk' in metric_name.lower():
            return AnalyticsInsight(
                insight_type='success',
                title=f'Improving {metric_name}',
                message=f'{metric_name} is trending downward by {abs(trend_value):.1f}%.',
                confidence=80.0,
                data_points=10,
                recommendation=f'Continue current strategies that are reducing {metric_name.lower()}.'
            )
        else:
            return AnalyticsInsight(
                insight_type='info',
                title=f'Stable {metric_name}',
                message=f'{metric_name} remains stable with minimal variation.',
                confidence=70.0,
                data_points=10,
                recommendation=f'Monitor {metric_name.lower()} for any significant changes.'
            )