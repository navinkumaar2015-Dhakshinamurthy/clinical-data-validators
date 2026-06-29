# Clinical Data Validators

Production-ready data quality validators for clinical research datasets.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
import pandas as pd
from clinical_validators import validate_missing_critical_fields

# Load your clinical data
df = pd.read_csv('lab_results.csv')

# Run validation
result = validate_missing_critical_fields(df)

# Check results
print(result)
# Output:
# {
#   'validator_name': 'missing_critical_fields',
#   'status': 'PASS',
#   'total_records': 1000,
#   'failed_records': 0,
#   ...
# }
```

## Running Tests

```bash
pytest tests/ -v
```

## Validators

### missing_critical_fields
Checks that required clinical fields are not NULL/empty.

**Fields checked:** patient_id, visit_date, lab_test_name, lab_value, test_date

**Custom fields:**
```python
validate_missing_critical_fields(df, critical_fields=['custom_field_1', 'custom_field_2'])
```