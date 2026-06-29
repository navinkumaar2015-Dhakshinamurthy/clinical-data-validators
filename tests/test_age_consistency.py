import pandas as pd
import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
sys.path.insert(0, str(Path(__file__).parent.parent))
from clinical_validators.age_consistency import validate_age_consistency

class TestAgeConsistency:
    def test_valid_age(self):
        birth = (datetime.now() - timedelta(days=30*365)).strftime('%Y-%m-%d')
        df = pd.DataFrame({'patient_id': [1], 'age': [30], 'birth_date': [birth]})
        assert validate_age_consistency(df)['status'] == 'PASS'
    def test_invalid_age(self):
        birth = (datetime.now() - timedelta(days=30*365)).strftime('%Y-%m-%d')
        df = pd.DataFrame({'patient_id': [1], 'age': [50], 'birth_date': [birth]})
        assert validate_age_consistency(df)['status'] == 'FAIL'
    def test_missing_data(self):
        df = pd.DataFrame({'patient_id': [1], 'age': [None], 'birth_date': [None]})
        assert validate_age_consistency(df)['status'] == 'PASS'
