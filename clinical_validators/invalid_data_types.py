import pandas as pd

def validate_invalid_data_types(dataframe, numeric_fields=None, date_fields=None):
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Expected pandas DataFrame")
    if dataframe.empty:
        raise ValueError("DataFrame is empty")

    if numeric_fields is None:
        numeric_fields = ['lab_value']
    if date_fields is None:
        date_fields = ['visit_date', 'test_date']

    failures = []
    failed_row_indices = set()

    for field in numeric_fields:
        if field not in dataframe.columns: continue
        for idx, val in dataframe[field].items():
            if pd.isna(val) or str(val).strip() == '': continue
            try:
                float(val)
            except (ValueError, TypeError):
                failed_row_indices.add(idx)
                patient_id = dataframe.at[idx, 'patient_id'] if 'patient_id' in dataframe.columns else 'UNKNOWN'
                failures.append({'row_index': idx, 'field': field, 'invalid_value': str(val), 'expected_type': 'numeric', 'patient_id': patient_id})

    for field in date_fields:
        if field not in dataframe.columns: continue
        for idx, val in dataframe[field].items():
            if pd.isna(val) or str(val).strip() == '': continue
            try:
                pd.to_datetime(val)
            except (ValueError, TypeError):
                failed_row_indices.add(idx)
                patient_id = dataframe.at[idx, 'patient_id'] if 'patient_id' in dataframe.columns else 'UNKNOWN'
                failures.append({'row_index': idx, 'field': field, 'invalid_value': str(val), 'expected_type': 'datetime', 'patient_id': patient_id})

    return {
        'validator_name': 'invalid_data_types',
        'status': 'PASS' if len(failed_row_indices) == 0 else 'FAIL',
        'total_records': len(dataframe),
        'failed_records': len(failed_row_indices),
        'failure_count': len(failures),
        'failures': failures
    }
