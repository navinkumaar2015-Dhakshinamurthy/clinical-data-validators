import pandas as pd
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from clinical_validators.out_of_range_values import validate_out_of_range_values

class TestOutOfRangeValues:
    def test_valid_ranges(self):
        df = pd.DataFrame({
            'patient_id': [1001, 1002],
            'lab_value': [150.5, 500],
            'age': [35, 67]
        })
        result = validate_out_of_range_values(df)
        assert result['status'] == 'PASS'
        assert result['failed_records'] == 0
    
    def test_lab_value_too_high(self):
        df = pd.DataFrame({
            'patient_id': [1001, 1002],
            'lab_value': [150.5, 15000],  # 15000 > 10000
            'age': [35, 67]
        })
        result = validate_out_of_range_values(df)
        assert result['status'] == 'FAIL'
        assert result['failed_records'] == 1
        assert result['failures'][0]['field'] == 'lab_value'
    
    def test_age_out_of_range(self):
        df = pd.DataFrame({
            'patient_id': [1001, 1002],
            'lab_value': [150.5, 500],
            'age': [35, 150]  # 150 > 120
        })
        result = validate_out_of_range_values(df)
        assert result['status'] == 'FAIL'
        assert result['failed_records'] == 1
        assert result['failures'][0]['field'] == 'age'
