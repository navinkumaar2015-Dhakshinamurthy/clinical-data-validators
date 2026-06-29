import pandas as pd

def validate_gender_based_tests(dataframe, test_field='test_name', gender_field='gender', rules=None):
    """
    Validates that certain medical tests are only performed on appropriate genders.
    
    Args:
        dataframe: pandas DataFrame.
        test_field: Column name for test name.
        gender_field: Column name for gender.
        rules: Dict mapping test names to allowed genders. 
               Default: {'Prostate_Specific_Antigen': ['M', 'Male'], 'Pap_Smear': ['F', 'Female']}
               
    Returns:
        dict with validation results.
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Expected pandas DataFrame")
    if dataframe.empty:
        raise ValueError("DataFrame is empty")

    if rules is None:
        rules = {
            'Prostate_Specific_Antigen': ['M', 'Male'],
            'Pap_Smear': ['F', 'Female']
        }

    failures = []
    failed_row_indices = set()

    for idx, row in dataframe.iterrows():
        test_name = row.get(test_field)
        gender = row.get(gender_field)

        if pd.isna(test_name) or pd.isna(gender):
            continue

        test_str = str(test_name).strip()
        gender_str = str(gender).strip()

        if test_str in rules:
            allowed_genders = [g.lower() for g in rules[test_str]]
            if gender_str.lower() not in allowed_genders:
                failed_row_indices.add(idx)
                patient_id = row.get('patient_id', 'UNKNOWN')
                failures.append({
                    'row_index': idx,
                    'patient_id': patient_id,
                    'test': test_str,
                    'gender': gender_str,
                    'error': f"Test {test_str} is invalid for gender {gender_str}"
                })

    return {
        'validator_name': 'gender_based_validation',
        'status': 'PASS' if len(failed_row_indices) == 0 else 'FAIL',
        'total_records': len(dataframe),
        'failed_records': len(failed_row_indices),
        'failure_count': len(failures),
        'failures': failures
    }
