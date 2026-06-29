from .missing_fields import validate_missing_critical_fields
from .invalid_data_types import validate_invalid_data_types
from .future_dates import validate_future_dates
from .out_of_range_values import validate_out_of_range_values
from .duplicate_records import validate_duplicate_records
from .invalid_patient_ids import validate_patient_ids
from .missing_visit_data import validate_missing_visit_data
from .age_consistency import validate_age_consistency
from .gender_based_validation import validate_gender_based_tests
from .data_completeness import validate_data_completeness

__version__ = "0.4.0"
__all__ = [
    'validate_missing_critical_fields',
    'validate_invalid_data_types',
    'validate_future_dates',
    'validate_out_of_range_values',
    'validate_duplicate_records',
    'validate_patient_ids',
    'validate_missing_visit_data',
    'validate_age_consistency',
    'validate_gender_based_tests',
    'validate_data_completeness'
]
