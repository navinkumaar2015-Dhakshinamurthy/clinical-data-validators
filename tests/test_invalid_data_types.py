import pandas as pd
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from clinical_validators.invalid_data_types import validate_invalid_data_types

class TestInvalidDataTypes:
    def test_valid_data_types(self):
        df = pd.DataFrame({'patient_id': [1001], 'lab_value': [14.5], 'visit_date': ['2026-01-15'], 'test_date': ['2026-01-15']})
        assert validate_invalid_data_types(df)['status'] == 'PASS'

    def test_invalid_numeric_value(self):
        df = pd.DataFrame({'patient_id': [1001], 'lab_value': ['abc'], 'visit_date': ['2026-01-15'], 'test_date': ['2026-01-15']})
        result = validate_invalid_data_types(df)
        assert result['status'] == 'FAIL'
        assert result['failures'][0]['field'] == 'lab_value'

    def test_invalid_date_format(self):
        df = pd.DataFrame({'patient_id': [1001], 'lab_value': [14.5], 'visit_date': ['not-a-date'], 'test_date': ['2026-01-15']})
        result = validate_invalid_data_types(df)
        assert result['status'] == 'FAIL'
        assert result['failures'][0]['field'] == 'visit_date'

    def test_empty_dataframe_raises_error(self):
        with pytest.raises(ValueError): validate_invalid_data_types(pd.DataFrame())
