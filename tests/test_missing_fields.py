import pandas as pd
import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from clinical_validators.missing_fields import validate_missing_critical_fields


class TestMissingCriticalFields:
    """Test suite for missing_critical_fields validator"""
    
    def test_valid_dataframe_no_missing_values(self):
        """Test: Clean data should pass validation"""
        data = {
            'patient_id': [1001, 1002, 1003],
            'visit_date': ['2026-01-15', '2026-01-16', '2026-01-17'],
            'lab_test_name': ['Hemoglobin', 'Glucose', 'Cholesterol'],
            'lab_value': [14.5, 95, 180],
            'test_date': ['2026-01-15', '2026-01-16', '2026-01-17']
        }
        df = pd.DataFrame(data)
        result = validate_missing_critical_fields(df)
        
        assert result['status'] == 'PASS', "Clean data should pass"
        assert result['failed_records'] == 0, "Should have 0 failed records"
        assert result['total_records'] == 3, "Should have 3 total records"
        assert len(result['failures']) == 0, "Failures list should be empty"
        print("✓ Test 1 PASSED: Clean data validated successfully")
    
    def test_missing_patient_id(self):
        """Test: Missing patient_id should be detected"""
        data = {
            'patient_id': [1001, None, 1003],
            'visit_date': ['2026-01-15', '2026-01-16', '2026-01-17'],
            'lab_test_name': ['Hemoglobin', 'Glucose', 'Cholesterol'],
            'lab_value': [14.5, 95, 180],
            'test_date': ['2026-01-15', '2026-01-16', '2026-01-17']
        }
        df = pd.DataFrame(data)
        result = validate_missing_critical_fields(df)
        
        assert result['status'] == 'FAIL', "Should fail with missing patient_id"
        assert result['failed_records'] == 1, "Should have 1 failed record"
        assert any(f['missing_field'] == 'patient_id' for f in result['failures']), \
            "Should identify missing patient_id"
        print("✓ Test 2 PASSED: Missing patient_id detected")
    
    def test_missing_multiple_fields(self):
        """Test: Multiple missing fields across different rows"""
        data = {
            'patient_id': [1001, 1002, None],
            'visit_date': [None, '2026-01-16', '2026-01-17'],
            'lab_test_name': ['Hemoglobin', 'Glucose', 'Cholesterol'],
            'lab_value': [14.5, 95, 180],
            'test_date': ['2026-01-15', None, '2026-01-17']
        }
        df = pd.DataFrame(data)
        result = validate_missing_critical_fields(df)
        
        assert result['status'] == 'FAIL', "Should fail with missing fields"
        assert result['failed_records'] == 3, "Should have 3 failed records"
        assert result['failure_count'] == 3, "Should have 3 total failures"
        print("✓ Test 3 PASSED: Multiple missing fields detected correctly")
    
    def test_missing_lab_test_name(self):
        """Test: Missing lab_test_name detection (empty string)"""
        data = {
            'patient_id': [1001, 1002],
            'visit_date': ['2026-01-15', '2026-01-16'],
            'lab_test_name': ['Hemoglobin', ''],  # Empty string
            'lab_value': [14.5, 95],
            'test_date': ['2026-01-15', '2026-01-16']
        }
        df = pd.DataFrame(data)
        result = validate_missing_critical_fields(df)
        
        assert result['status'] == 'FAIL', "Should detect empty string as missing"
        assert result['failed_records'] == 1, "Should flag empty string row"
        assert any(f['missing_field'] == 'lab_test_name' and f['row_index'] == 1 
                   for f in result['failures']), "Should identify lab_test_name empty"
        print("✓ Test 4 PASSED: Empty string detected as missing value")
    
    def test_all_fields_missing(self):
        """Test: Edge case - all critical fields missing in one row"""
        data = {
            'patient_id': [None, 1002],
            'visit_date': [None, '2026-01-16'],
            'lab_test_name': [None, 'Glucose'],
            'lab_value': [None, 95],
            'test_date': [None, '2026-01-16']
        }
        df = pd.DataFrame(data)
        result = validate_missing_critical_fields(df)
        
        assert result['failed_records'] == 1, "Should detect row with all missing fields"
        assert result['failure_count'] == 5, "Should count 5 failures (1 per field)"
        print("✓ Test 5 PASSED: All missing fields in single row detected")
    
    def test_empty_dataframe_raises_error(self):
        """Test: Empty DataFrame should raise ValueError"""
        df = pd.DataFrame()
        
        with pytest.raises(ValueError):
            validate_missing_critical_fields(df)
        
        print("✓ Test 6 PASSED: Empty DataFrame raises ValueError")
    
    def test_invalid_input_type_raises_error(self):
        """Test: Non-DataFrame input should raise TypeError"""
        # Test with string input
        with pytest.raises(TypeError):
            validate_missing_critical_fields("not a dataframe")
        
        # Test with list input
        with pytest.raises(TypeError):
            validate_missing_critical_fields([1, 2, 3])
        
        print("✓ Test 7 PASSED: Invalid input types raise TypeError")
    
    def test_custom_critical_fields(self):
        """Test: Validator should work with custom field list"""
        data = {
            'patient_id': [1001, None],
            'visit_date': ['2026-01-15', '2026-01-16'],
            'other_field': ['A', 'B']
        }
        df = pd.DataFrame(data)
        custom_fields = ['patient_id', 'other_field']
        result = validate_missing_critical_fields(df, critical_fields=custom_fields)
        
        assert 'visit_date' not in result['critical_fields_checked'], \
            "Should only check specified fields"
        assert result['failed_records'] == 1, "Should detect missing patient_id"
        print("✓ Test 8 PASSED: Custom field list works correctly")
    
    def test_extra_columns_ignored(self):
        """Test: Extra columns should not affect validation"""
        data = {
            'patient_id': [1001, 1002],
            'visit_date': ['2026-01-15', '2026-01-16'],
            'lab_test_name': ['Hemoglobin', 'Glucose'],
            'lab_value': [14.5, 95],
            'test_date': ['2026-01-15', '2026-01-16'],
            'extra_column_1': ['X', 'Y'],
            'extra_column_2': [100, 200]
        }
        df = pd.DataFrame(data)
        result = validate_missing_critical_fields(df)
        
        assert result['status'] == 'PASS', "Extra columns should not cause failures"
        assert result['failed_records'] == 0, "Should have no failures"
        print("✓ Test 9 PASSED: Extra columns ignored correctly")
    
    def test_nan_vs_none_consistency(self):
        """Test: Both NaN and None are treated as missing"""
        data = {
            'patient_id': [1001, None, 1003],
            'visit_date': ['2026-01-15', '2026-01-16', pd.NaT],
            'lab_test_name': ['Hemoglobin', 'Glucose', 'Cholesterol'],
            'lab_value': [14.5, 95, 180],
            'test_date': ['2026-01-15', '2026-01-16', '2026-01-17']
        }
        df = pd.DataFrame(data)
        result = validate_missing_critical_fields(df)
        
        assert result['status'] == 'FAIL', "Should detect both None and NaT"
        assert result['failed_records'] == 2, "Should have 2 failed records"
        print("✓ Test 10 PASSED: NaN and None handled consistently")


if __name__ == '__main__':
    print("=" * 80)
    print("CLINICAL DATA VALIDATORS - TEST SUITE")
    print("Validator: missing_critical_fields")
    print("=" * 80)
    print()
    
    # Run with pytest
    pytest.main([__file__, '-v', '--tb=short'])
