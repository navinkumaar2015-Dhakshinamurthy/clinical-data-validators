import pandas as pd

def validate_duplicate_records(dataframe, duplicate_fields=None):
    """
    Validates that there are no duplicate records based on specified fields.
    Typical use case: same patient + same test + same date
    
    Args:
        dataframe: pandas DataFrame with clinical data
        duplicate_fields: list of field names to check for duplicates
                         Default: ['patient_id', 'test_name', 'test_date']
    
    Returns:
        dict with validation results
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Expected pandas DataFrame")
    if dataframe.empty:
        raise ValueError("DataFrame is empty")
    
    if duplicate_fields is None:
        duplicate_fields = ['patient_id', 'test_name', 'test_date']
    
    # Check if all required fields exist
    available_fields = [f for f in duplicate_fields if f in dataframe.columns]
    if len(available_fields) < 2:
        raise ValueError(f"Need at least 2 fields to check duplicates. Found: {available_fields}")
    
    # Find duplicates
    duplicates = dataframe[dataframe.duplicated(subset=available_fields, keep=False)]
    
    failures = []
    if not duplicates.empty:
        # Get unique duplicate groups
        duplicate_groups = duplicates.groupby(available_fields).size().reset_index(name='count')
        duplicate_groups = duplicate_groups[duplicate_groups['count'] > 1]
        
        for _, row in duplicate_groups.iterrows():
            # Find all rows in this duplicate group
            mask = True
            for field in available_fields:
                mask = mask & (duplicates[field] == row[field])
            duplicate_indices = duplicates[mask].index.tolist()
            
            for idx in duplicate_indices:
                failures.append({
                    'row_index': idx,
                    'duplicate_fields': available_fields,
                    'duplicate_values': {field: row[field] for field in available_fields},
                    'occurrences': int(row['count'])
                })
    
    failed_row_indices = set(f['row_index'] for f in failures)
    
    return {
        'validator_name': 'duplicate_records',
        'status': 'PASS' if len(failed_row_indices) == 0 else 'FAIL',
        'total_records': len(dataframe),
        'failed_records': len(failed_row_indices),
        'failure_count': len(failures),
        'failures': failures
    }
