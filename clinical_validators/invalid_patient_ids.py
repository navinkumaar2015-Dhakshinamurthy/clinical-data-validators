import pandas as pd
import re

def validate_patient_ids(dataframe, patient_id_field='patient_id', pattern=None, min_length=None, max_length=None):
    """
    Validates patient ID format according to specified rules.
    
    Args:
        dataframe: pandas DataFrame with clinical data
        patient_id_field: name of the patient ID column (default: 'patient_id')
        pattern: regex pattern for validation (default: None)
        min_length: minimum length of patient ID (default: None)
        max_length: maximum length of patient ID (default: None)
    
    Default behavior: Validates that patient IDs are exactly 5 digits
    
    Returns:
        dict with validation results
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Expected pandas DataFrame")
    if dataframe.empty:
        raise ValueError("DataFrame is empty")
    
    if patient_id_field not in dataframe.columns:
        raise ValueError(f"Column '{patient_id_field}' not found in DataFrame")
    
    # Default: 5-digit numeric ID
    if pattern is None and min_length is None and max_length is None:
        pattern = r'^\d{5}$'  # Exactly 5 digits
    
    failures = []
    failed_row_indices = set()
    
    for idx, val in dataframe[patient_id_field].items():
        if pd.isna(val) or str(val).strip() == '':
            continue  # Skip missing values
        
        patient_id_str = str(val).strip()
        is_valid = True
        error_reason = ""
        
        # Check pattern
        if pattern:
            if not re.match(pattern, patient_id_str):
                is_valid = False
                error_reason = f"Does not match pattern: {pattern}"
        
        # Check length
        if is_valid and (min_length is not None or max_length is not None):
            if min_length is not None and len(patient_id_str) < min_length:
                is_valid = False
                error_reason = f"Length {len(patient_id_str)} < minimum {min_length}"
            elif max_length is not None and len(patient_id_str) > max_length:
                is_valid = False
                error_reason = f"Length {len(patient_id_str)} > maximum {max_length}"
        
        if not is_valid:
            failed_row_indices.add(idx)
            failures.append({
                'row_index': idx,
                'field': patient_id_field,
                'invalid_value': patient_id_str,
                'error': error_reason
            })
    
    return {
        'validator_name': 'invalid_patient_ids',
        'status': 'PASS' if len(failed_row_indices) == 0 else 'FAIL',
        'total_records': len(dataframe),
        'failed_records': len(failed_row_indices),
        'failure_count': len(failures),
        'failures': failures
    }
