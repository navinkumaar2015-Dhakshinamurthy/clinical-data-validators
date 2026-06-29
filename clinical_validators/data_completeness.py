import pandas as pd

def validate_data_completeness(dataframe, test_field='test_type', completeness_rules=None):
    """
    Validates that required fields are present for specific test types.
    
    Args:
        dataframe: pandas DataFrame.
        test_field: Column name indicating the test type.
        completeness_rules: Dict mapping test types to lists of required fields.
                            Default: {'Blood': ['hemoglobin', 'wbc'], 'Urine': ['ph', 'protein']}
                            
    Returns:
        dict with validation results.
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Expected pandas DataFrame")
    if dataframe.empty:
        raise ValueError("DataFrame is empty")

    if completeness_rules is None:
        completeness_rules = {
            'Blood': ['hemoglobin', 'wbc'],
            'Urine': ['ph', 'protein']
        }

    failures = []
    failed_row_indices = set()

    for idx, row in dataframe.iterrows():
        test_type = row.get(test_field)
        if pd.isna(test_type):
            continue

        test_str = str(test_type).strip()
        if test_str in completeness_rules:
            required_fields = completeness_rules[test_str]
            for field in required_fields:
                if field not in dataframe.columns or pd.isna(row.get(field)) or str(row.get(field)).strip() == '':
                    failed_row_indices.add(idx)
                    patient_id = row.get('patient_id', 'UNKNOWN')
                    failures.append({
                        'row_index': idx,
                        'patient_id': patient_id,
                        'test_type': test_str,
                        'missing_field': field,
                        'error': f"Missing required field '{field}' for {test_str} test"
                    })

    return {
        'validator_name': 'data_completeness',
        'status': 'PASS' if len(failed_row_indices) == 0 else 'FAIL',
        'total_records': len(dataframe),
        'failed_records': len(failed_row_indices),
        'failure_count': len(failures),
        'failures': failures
    }
