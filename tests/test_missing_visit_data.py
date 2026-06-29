import pandas as pd
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from clinical_validators.missing_visit_data import validate_missing_visit_data

class TestMissingVisitData:
    def test_valid_data(self):
        df = pd.DataFrame({'patient_id': [1], 'lab_value': [100], 'visit_date': ['2026-01-01']})
        assert validate_missing_visit_data(df)['status'] == 'PASS'
    def test_missing_visit(self):
        df = pd.DataFrame({'patient_id': [1], 'lab_value': [100], 'visit_date': [None]})
        assert validate_missing_visit_data(df)['status'] == 'FAIL'
    def test_no_lab_no_visit(self):
        df = pd.DataFrame({'patient_id': [1], 'lab_value': [None], 'visit_date': [None]})
        assert validate_missing_visit_data(df)['status'] == 'PASS'
