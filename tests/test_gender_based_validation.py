import pandas as pd
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from clinical_validators.gender_based_validation import validate_gender_based_tests

class TestGenderValidation:
    def test_valid_gender(self):
        df = pd.DataFrame({'patient_id': [1], 'test_name': ['Prostate_Specific_Antigen'], 'gender': ['M']})
        assert validate_gender_based_tests(df)['status'] == 'PASS'
    def test_invalid_gender(self):
        df = pd.DataFrame({'patient_id': [1], 'test_name': ['Prostate_Specific_Antigen'], 'gender': ['F']})
        assert validate_gender_based_tests(df)['status'] == 'FAIL'
    def test_unrestricted_test(self):
        df = pd.DataFrame({'patient_id': [1], 'test_name': ['Blood_Test'], 'gender': ['F']})
        assert validate_gender_based_tests(df)['status'] == 'PASS'
