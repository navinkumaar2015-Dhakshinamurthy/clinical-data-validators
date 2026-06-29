# Clinical Data Validators

A comprehensive Python library for validating clinical datasets with 10 different validators.

## Installation

### From PyPI (Production)
ash
pip install clinical-data-validators


### From TestPyPI (Testing)
ash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple clinical-data-validators


## Quick Start

python
import pandas as pd
from clinical_validators import (
    validate_missing_critical_fields,
    validate_invalid_data_types,
    validate_future_dates,
    validate_out_of_range_values,
    validate_duplicate_records,
    validate_patient_ids,
    validate_missing_visit_data,
    validate_age_consistency,
    validate_gender_based_tests,
    validate_data_completeness
)

# Load your clinical data
df = pd.read_csv("your_data.csv")

# Run validators
result = validate_missing_critical_fields(df, critical_fields=['patient_id', 'lab_value'])
print(result)


## Available Validators

1. **validate_missing_critical_fields** - Check for missing required fields
2. **validate_invalid_data_types** - Validate data types (numeric, dates)
3. **validate_future_dates** - Detect future dates in historical data
4. **validate_out_of_range_values** - Check values against clinical ranges
5. **validate_duplicate_records** - Find duplicate patient records
6. **validate_patient_ids** - Validate patient ID format
7. **validate_missing_visit_data** - Ensure lab results have visit records
8. **validate_age_consistency** - Verify age matches birth date
9. **validate_gender_based_tests** - Check gender-specific test validity
10. **validate_data_completeness** - Ensure required fields for specific tests

## Testing

ash
pytest tests/ -v


## Version

Current version: 0.4.0

## Author

Navin Kumar

## License

MIT License
