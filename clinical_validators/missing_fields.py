import pandas as pd
from typing import Dict, List, Optional

def validate_missing_critical_fields(
    dataframe: pd.DataFrame, 
    critical_fields: Optional[List[str]] = None
) -> Dict:
    """
    Validates that critical clinical fields are not NULL/empty.
    
    This validator checks for missing values (NaN, None, empty strings) in 
    critical clinical data fields. It's designed to catch common data quality 
    issues in clinical research datasets.
    
    Args:
        dataframe: pandas DataFrame with clinical data
        critical_fields: list of required field names. If None, uses default 
                        clinical fields (patient_id, visit_date, lab_test_name, 
                        lab_value, test_date)
        
    Returns:
        Dictionary with validation results containing:
        - validator_name: name of the validator
        - status: 'PASS' or 'FAIL'
        - total_records: total rows in dataframe
        - failed_records: number of rows with missing values
        - failure_count: total number of missing value instances
        - critical_fields_checked: list of fields that were validated
        - failures: list of detailed failure information
        
    Raises:
        ValueError: if dataframe is empty or critical_fields is empty list
        TypeError: if dataframe is not a pandas DataFrame
        
    Example:
        >>> import pandas as pd
        >>> from clinical_validators import validate_missing_critical_fields
        >>> df = pd.read_csv('lab_data.csv')
        >>> result = validate_missing_critical_fields(df)
        >>> print(result['status'])
        'FAIL'
        >>> print(f"Failed records: {result['failed_records']}")
        'Failed records: 5'
    """
    
    # ===== INPUT VALIDATION =====
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(dataframe).__name__}")
    
    if dataframe.empty:
        raise ValueError("DataFrame is empty - cannot validate empty dataset")
    
    # Default critical fields for clinical data
    if critical_fields is None:
        critical_fields = [
            'patient_id', 
            'visit_date', 
            'lab_test_name', 
            'lab_value', 
            'test_date'
        ]
    
    if isinstance(critical_fields, list) and len(critical_fields) == 0:
        raise ValueError("critical_fields list cannot be empty")
    
    # ===== VALIDATION LOGIC =====
    failures = []
    
    # Check each critical field
    for field in critical_fields:
        # Skip if field doesn't exist in dataframe
        if field not in dataframe.columns:
            continue
        
        # Find rows where field is NULL, NaN, or empty string
        # This handles: None, np.nan, pd.NaT, and empty strings
        missing_mask = (dataframe[field].isna()) | (dataframe[field] == '')
        missing_indices = dataframe[missing_mask].index.tolist()
        
        # Record each failure with context
        for idx in missing_indices:
            # Safely retrieve patient_id for context
            patient_id = 'UNKNOWN'
            try:
                if 'patient_id' in dataframe.columns:
                    pid_value = dataframe.at[idx, 'patient_id']
                    # Check if patient_id itself is missing
                    if pd.isna(pid_value) or pid_value == '':
                        patient_id = 'UNKNOWN'
                    else:
                        patient_id = str(pid_value)
            except (KeyError, IndexError, TypeError):
                patient_id = 'UNKNOWN'
            
            failures.append({
                'row_index': idx,
                'missing_field': field,
                'patient_id': patient_id
            })
    
    # Count unique rows with any failures
    failed_row_indices = set([f['row_index'] for f in failures])
    
    # ===== RETURN RESULTS =====
    return {
        'validator_name': 'missing_critical_fields',
        'status': 'PASS' if len(failed_row_indices) == 0 else 'FAIL',
        'total_records': len(dataframe),
        'failed_records': len(failed_row_indices),
        'critical_fields_checked': critical_fields,
        'failure_count': len(failures),
        'failures': failures
    }
