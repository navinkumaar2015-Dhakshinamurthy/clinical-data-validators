import pandas as pd
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from clinical_validators.duplicate_records import validate_duplicate_records

class TestDuplicateRecords:
    def test_no_duplicates(self):
        df = pd.DataFrame({
            'patient_id': [1001, 1002, 1003],
            'test_name': ['Blood', 'Urine', 'X-Ray'],
            'test_date': ['2026-01-15', '2026-01-16', '2026-01-17']
        })
        result = validate_duplicate_records(df)
        assert result['status'] == 'PASS'
        assert result['failed_records'] == 0
    
    def test_exact_duplicates(self):
        df = pd.DataFrame({
            'patient_id': [1001, 1001],  # Same patient
            'test_name': ['Blood', 'Blood'],  # Same test
            'test_date': ['2026-01-15', '2026-01-15']  # Same date
        })
        result = validate_duplicate_records(df)
        assert result['status'] == 'FAIL'
        assert result['failed_records'] == 2  # Both rows are duplicates
    
    def test_partial_duplicates_not_flagged(self):
        df = pd.DataFrame({
            'patient_id': [1001, 1001],  # Same patient
            'test_name': ['Blood', 'Urine'],  # Different test
            'test_date': ['2026-01-15', '2026-01-15']  # Same date
        })
        result = validate_duplicate_records(df)
        assert result['status'] == 'PASS'  # Not exact duplicates
