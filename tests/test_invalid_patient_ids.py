import pandas as pd
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from clinical_validators.invalid_patient_ids import validate_patient_ids

class TestInvalidPatientIds:
    def test_valid_patient_ids(self):
        df = pd.DataFrame({
            'patient_id': ['12345', '67890', '11111']
        })
        result = validate_patient_ids(df)
        assert result['status'] == 'PASS'
        assert result['failed_records'] == 0
    
    def test_invalid_format_too_short(self):
        df = pd.DataFrame({
            'patient_id': ['12345', '1234']  # 1234 is only 4 digits
        })
        result = validate_patient_ids(df)
        assert result['status'] == 'FAIL'
        assert result['failed_records'] == 1
    
    def test_invalid_format_non_numeric(self):
        df = pd.DataFrame({
            'patient_id': ['12345', 'ABC12']  # ABC12 contains letters
        })
        result = validate_patient_ids(df)
        assert result['status'] == 'FAIL'
        assert result['failed_records'] == 1
