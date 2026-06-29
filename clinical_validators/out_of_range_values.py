import pandas as pd

def validate_out_of_range_values(dataframe, range_rules=None):
    """
    Validates that numeric fields fall within acceptable clinical ranges.
    
    Args:
        dataframe: pandas DataFrame with clinical data
        range_rules: dict with field names as keys and (min, max) tuples as values
                    Example: {'lab_value': (0, 1000), 'age': (0, 120)}
    
    Returns:
        dict with validation results
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Expected pandas DataFrame")
    if dataframe.empty:
        raise ValueError("DataFrame is empty")
    
    # Default clinical ranges
    if range_rules is None:
        range_rules = {
            'lab_value': (0, 10000),  # Generic lab value range
            'age': (0, 120)  # Human age range
        }
    
    failures = []
    failed_row_indices = set()
    
    for field, (min_val, max_val) in range_rules.items():
        if field not in dataframe.columns:
            continue
        
        for idx, val in dataframe[field].items():
            if pd.isna(val):
                continue  # Skip missing values
            
            try:
                numeric_val = float(val)
                if numeric_val < min_val or numeric_val > max_val:
                    failed_row_indices.add(idx)
                    patient_id = dataframe.at[idx, 'patient_id'] if 'patient_id' in dataframe.columns else 'UNKNOWN'
                    failures.append({
                        'row_index': idx,
                        'field': field,
                        'invalid_value': numeric_val,
                        'expected_range': f"{min_val}-{max_val}",
                        'patient_id': patient_id
                    })
            except (ValueError, TypeError):
                # Skip non-numeric values (handled by invalid_data_types validator)
                continue
    
    return {
        'validator_name': 'out_of_range_values',
        'status': 'PASS' if len(failed_row_indices) == 0 else 'FAIL',
        'total_records': len(dataframe),
        'failed_records': len(failed_row_indices),
        'failure_count': len(failures),
        'failures': failures
    }
