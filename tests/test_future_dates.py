import pandas as pd
import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))
from clinical_validators.future_dates import validate_future_dates

class TestFutureDates:
    def test_valid_past_dates(self):
        df = pd.DataFrame({'patient_id': [1001], 'visit_date': ['2023-01-15'], 'test_date': ['2023-01-15']})
        assert validate_future_dates(df)['status'] == 'PASS'

    def test_future_visit_date(self):
        future_date = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
        df = pd.DataFrame({'patient_id': [1001], 'visit_date': [future_date], 'test_date': ['2023-01-15']})
        result = validate_future_dates(df)
        assert result['status'] == 'FAIL'
        assert result['failures'][0]['field'] == 'visit_date'

    def test_empty_dataframe_raises_error(self):
        with pytest.raises(ValueError): validate_future_dates(pd.DataFrame())
