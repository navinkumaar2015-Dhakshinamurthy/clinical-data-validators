import pandas as pd

def validate_future_dates(dataframe, date_fields=None):
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Expected pandas DataFrame")
    if dataframe.empty:
        raise ValueError("DataFrame is empty")

    if date_fields is None:
        date_fields = ['visit_date', 'test_date']

    failures = []
    failed_row_indices = set()
    now = pd.Timestamp.now()

    for field in date_fields:
        if field not in dataframe.columns: continue
        for idx, val in dataframe[field].items():
            if pd.isna(val) or str(val).strip() == '': continue
            try:
                # QA FIX: Force tz-naive to prevent comparison crashes with mixed timezone data
                date_val = pd.to_datetime(val).tz_localize(None) 
                if date_val > now:
                    failed_row_indices.add(idx)
                    patient_id = dataframe.at[idx, 'patient_id'] if 'patient_id' in dataframe.columns else 'UNKNOWN'
                    failures.append({'row_index': idx, 'field': field, 'invalid_value': str(val), 'error': 'Date is in the future', 'patient_id': patient_id})
            except (ValueError, TypeError):
                continue

    return {
        'validator_name': 'future_dates',
        'status': 'PASS' if len(failed_row_indices) == 0 else 'FAIL',
        'total_records': len(dataframe),
        'failed_records': len(failed_row_indices),
        'failure_count': len(failures),
        'failures': failures
    }
