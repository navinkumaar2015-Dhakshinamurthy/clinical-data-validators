import pandas as pd

def validate_missing_visit_data(dataframe, lab_field='lab_value', visit_field='visit_date'):
    """
    Validates that if a patient has a lab result, they must have a corresponding visit record.
    
    Args:
        dataframe: pandas DataFrame with clinical data.
        lab_field: Column name containing lab results.
        visit_field: Column name containing visit dates.
        
    Returns:
        dict with validation results.
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Expected pandas DataFrame")
    if dataframe.empty:
        raise ValueError("DataFrame is empty")

    failures = []
    failed_row_indices = set()

    for idx, row in dataframe.iterrows():
        has_lab = pd.notna(row.get(lab_field)) and str(row.get(lab_field)).strip() != ''
        has_visit = pd.notna(row.get(visit_field)) and str(row.get(visit_field)).strip() != ''

        if has_lab and not has_visit:
            failed_row_indices.add(idx)
            patient_id = row.get('patient_id', 'UNKNOWN')
            failures.append({
                'row_index': idx,
                'patient_id': patient_id,
                'error': f"Has lab value '{row[lab_field]}' but missing {visit_field}"
            })

    return {
        'validator_name': 'missing_visit_data',
        'status': 'PASS' if len(failed_row_indices) == 0 else 'FAIL',
        'total_records': len(dataframe),
        'failed_records': len(failed_row_indices),
        'failure_count': len(failures),
        'failures': failures
    }
