import pandas as pd
from datetime import datetime

def validate_age_consistency(dataframe, age_field='age', birth_date_field='birth_date', tolerance_years=1):
    """
    Validates that the recorded age is consistent with the birth date.
    
    Args:
        dataframe: pandas DataFrame.
        age_field: Column name for age.
        birth_date_field: Column name for birth date.
        tolerance_years: Allowed difference in years (default 1 for leap year/rounding).
        
    Returns:
        dict with validation results.
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Expected pandas DataFrame")
    if dataframe.empty:
        raise ValueError("DataFrame is empty")

    failures = []
    failed_row_indices = set()
    now = datetime.now()

    for idx, row in dataframe.iterrows():
        age = row.get(age_field)
        birth_date = row.get(birth_date_field)

        if pd.isna(age) or pd.isna(birth_date):
            continue

        try:
            birth_dt = pd.to_datetime(birth_date).to_pydatetime()
            calculated_age = (now - birth_dt).days / 365.25
            if abs(calculated_age - float(age)) > tolerance_years:
                failed_row_indices.add(idx)
                patient_id = row.get('patient_id', 'UNKNOWN')
                failures.append({
                    'row_index': idx,
                    'patient_id': patient_id,
                    'recorded_age': age,
                    'calculated_age': round(calculated_age, 1),
                    'error': 'Age does not match birth date'
                })
        except (ValueError, TypeError):
            continue

    return {
        'validator_name': 'age_consistency',
        'status': 'PASS' if len(failed_row_indices) == 0 else 'FAIL',
        'total_records': len(dataframe),
        'failed_records': len(failed_row_indices),
        'failure_count': len(failures),
        'failures': failures
    }
