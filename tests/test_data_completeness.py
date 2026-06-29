import pandas as pd
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from clinical_validators.data_completeness import validate_data_completeness

class TestDataCompleteness:
    def test_complete_blood(self):
        df = pd.DataFrame({'patient_id': [1], 'test_type': ['Blood'], 'hemoglobin': [14], 'wbc': [5]})
        assert validate_data_completeness(df)['status'] == 'PASS'
        
    def test_incomplete_blood(self):
        df = pd.DataFrame({'patient_id': [1], 'test_type': ['Blood'], 'hemoglobin': [14], 'wbc': [None]})
        assert validate_data_completeness(df)['status'] == 'FAIL'
        
    def test_different_test_type(self):
        # Urine test requires 'ph' and 'protein'. 'hemoglobin' and 'wbc' are for Blood, so they can be None.
        df = pd.DataFrame({
            'patient_id': [1], 
            'test_type': ['Urine'], 
            'ph': [6.0], 
            'protein': ['Negative'], 
            'hemoglobin': [None], 
            'wbc': [None]
        })
        assert validate_data_completeness(df)['status'] == 'PASS'
