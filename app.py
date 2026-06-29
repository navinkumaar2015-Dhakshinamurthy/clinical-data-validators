from flask import Flask, request, jsonify, render_template_string, send_file
import pandas as pd
import numpy as np
import io
import json
from datetime import datetime
from clinical_validators import (
    validate_missing_critical_fields,
    validate_invalid_data_types,
    validate_future_dates,
    validate_out_of_range_values,
    validate_duplicate_records,
    validate_patient_ids,
    validate_missing_visit_data,
    validate_age_consistency,
    validate_gender_based_tests,
    validate_data_completeness
)

app = Flask(__name__)

def convert_to_serializable(obj):
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif pd.isna(obj):
        return None
    else:
        return obj

HTML_PAGE = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clinical Data Validator - Production Ready</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
        h1 { text-align: center; color: #2c3e50; margin-bottom: 10px; }
        .subtitle { text-align: center; color: #7f8c8d; margin-bottom: 30px; }
        .form-section { background: #f8f9fa; padding: 30px; border-radius: 8px; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; font-weight: 600; color: #34495e; margin-bottom: 8px; }
        input[type="file"], input[type="date"] { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 6px; font-size: 14px; }
        .checkbox-group { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 12px; }
        .checkbox-item { display: flex; align-items: center; padding: 12px; background: white; border-radius: 6px; border: 2px solid #e0e0e0; cursor: pointer; transition: all 0.3s; }
        .checkbox-item:hover { border-color: #667eea; transform: translateY(-2px); box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .checkbox-item input { margin-right: 10px; width: 18px; height: 18px; cursor: pointer; }
        .checkbox-item label { margin: 0; cursor: pointer; font-weight: 500; }
        .btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 40px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: 600; width: 100%; transition: all 0.3s; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4); }
        .btn:disabled { background: #95a5a6; cursor: not-allowed; transform: none; }
        .btn-secondary { background: #95a5a6; margin-top: 10px; }
        .btn-success { background: #27ae60; }
        .btn-success:hover { background: #229954; }
        .loading { display: none; text-align: center; padding: 20px; }
        .loading.active { display: block; }
        .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #667eea; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; margin: 0 auto 15px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .error { background: #fee; border-left: 4px solid #e74c3c; padding: 15px; margin: 20px 0; border-radius: 4px; display: none; color: #c0392b; }
        .error.show { display: block; }
        .results { display: none; margin-top: 30px; }
        .results.show { display: block; }
        .results-header { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; }
        .timestamp { color: #7f8c8d; font-size: 14px; }
        .summary-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
        .card h3 { color: #7f8c8d; font-size: 14px; margin-bottom: 10px; text-transform: uppercase; }
        .card .value { font-size: 32px; font-weight: bold; color: #2c3e50; }
        .card.success .value { color: #27ae60; }
        .card.fail .value { color: #e74c3c; }
        .validator-result { background: #f8f9fa; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #ddd; }
        .validator-result.pass { border-left-color: #27ae60; }
        .validator-result.fail { border-left-color: #e74c3c; }
        .validator-result h4 { margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; }
        .status-badge { padding: 5px 15px; border-radius: 20px; font-size: 12px; font-weight: 600; text-transform: uppercase; color: white; }
        .status-badge.pass { background: #27ae60; }
        .status-badge.fail { background: #e74c3c; }
        .error-detail { background: white; padding: 10px; margin: 5px 0; border-radius: 4px; border-left: 3px solid #e74c3c; font-family: monospace; font-size: 13px; }
        .file-info { background: #e8f4f8; padding: 10px; border-radius: 6px; margin: 10px 0; font-size: 14px; }
        @media (max-width: 768px) {
            .container { padding: 20px; }
            h1 { font-size: 1.8em; }
            .checkbox-group { grid-template-columns: 1fr; }
            .summary-cards { grid-template-columns: 1fr; }
            .results-header { flex-direction: column; text-align: center; gap: 10px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏥 Clinical Data Validator</h1>
        <p class="subtitle">Professional-grade clinical dataset validation</p>
        
        <div class="error" id="error"></div>
        
        <form class="form-section">
            <div class="form-group">
                <label>📁 Upload CSV File</label>
                <input type="file" id="file" accept=".csv" required onchange="showFileInfo()">
                <div class="file-info" id="fileInfo" style="display:none;"></div>
            </div>
            
            <div class="form-group">
                <label>🔍 Select Validators to Run (Choose required ones)</label>
                <div class="checkbox-group">
                    <div class="checkbox-item">
                        <input type="checkbox" id="v1" name="validators" value="missing_fields" checked>
                        <label for="v1">Missing Critical Fields</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="v2" name="validators" value="invalid_data_types" checked>
                        <label for="v2">Invalid Data Types</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="v3" name="validators" value="future_dates" checked>
                        <label for="v3">Future Dates Detection</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="v4" name="validators" value="out_of_range" checked>
                        <label for="v4">Out of Range Values</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="v5" name="validators" value="duplicates" checked>
                        <label for="v5">Duplicate Records</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="v6" name="validators" value="patient_ids" checked>
                        <label for="v6">Invalid Patient IDs</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="v7" name="validators" value="missing_visit">
                        <label for="v7">Missing Visit Data</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="v8" name="validators" value="age_consistency">
                        <label for="v8">Age Consistency</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="v9" name="validators" value="gender_based">
                        <label for="v9">Gender-Based Validation</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="v10" name="validators" value="data_completeness">
                        <label for="v10">Data Completeness</label>
                    </div>
                </div>
            </div>
            
            <div class="form-group">
                <label>📅 Reference Date for Future Dates (Optional)</label>
                <input type="date" id="refdate">
                <small style="color: #7f8c8d; display: block; margin-top: 5px;">Leave empty to use today's date</small>
            </div>
            
            <button type="button" class="btn" onclick="runValidation()" id="runBtn">🚀 Run Validation Suite</button>
            <button type="button" class="btn btn-secondary" onclick="clearForm()">Clear Form</button>
        </form>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Validating your clinical data... This may take a moment.</p>
        </div>
        
        <div class="results" id="results"></div>
    </div>

    <script>
        var validationResults = null;
        var currentFilename = '';
        
        function showFileInfo() {
            var fileInput = document.getElementById('file');
            var fileInfo = document.getElementById('fileInfo');
            if (fileInput.files && fileInput.files[0]) {
                var file = fileInput.files[0];
                var sizeKB = (file.size / 1024).toFixed(2);
                fileInfo.innerHTML = '<strong>Selected:</strong> ' + file.name + ' (' + sizeKB + ' KB)';
                fileInfo.style.display = 'block';
                currentFilename = file.name;
            }
        }
        
        function runValidation() {
            var fileInput = document.getElementById('file');
            var file = fileInput.files[0];
            var loading = document.getElementById('loading');
            var results = document.getElementById('results');
            var error = document.getElementById('error');
            var runBtn = document.getElementById('runBtn');
            
            error.className = 'error';
            results.className = 'results';
            
            if (!file) {
                error.textContent = '❌ Please select a CSV file to upload.';
                error.className = 'error show';
                error.scrollIntoView({behavior: 'smooth'});
                return;
            }
            
            if (!file.name.toLowerCase().endsWith('.csv')) {
                error.textContent = '❌ Please upload a CSV file only.';
                error.className = 'error show';
                error.scrollIntoView({behavior: 'smooth'});
                return;
            }
            
            var validators = [];
            var checkboxes = document.querySelectorAll('input[name="validators"]:checked');
            checkboxes.forEach(function(cb) {
                validators.push(cb.value);
            });
            
            if (validators.length === 0) {
                error.textContent = '❌ Please select at least one validator to run.';
                error.className = 'error show';
                error.scrollIntoView({behavior: 'smooth'});
                return;
            }
            
            var formData = new FormData();
            formData.append('file', file);
            validators.forEach(function(v) {
                formData.append('validators', v);
            });
            
            var refdate = document.getElementById('refdate').value;
            if (refdate) {
                formData.append('reference_date', refdate);
            }
            
            loading.className = 'loading active';
            runBtn.disabled = true;
            
            fetch('/validate', {
                method: 'POST',
                body: formData
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(data) {
                loading.className = 'loading';
                runBtn.disabled = false;
                if (data.error) {
                    error.textContent = '❌ ' + data.error;
                    error.className = 'error show';
                    error.scrollIntoView({behavior: 'smooth'});
                } else {
                    validationResults = data;
                    displayResults(data);
                }
            })
            .catch(function(err) {
                loading.className = 'loading';
                runBtn.disabled = false;
                error.textContent = '❌ Network error: ' + err.message + '. Please try again.';
                error.className = 'error show';
                error.scrollIntoView({behavior: 'smooth'});
            });
        }
        
        function displayResults(data) {
            var results = document.getElementById('results');
            var timestamp = new Date().toLocaleString();
            
            var passed = 0;
            var failed = 0;
            var totalFailedRecords = 0;
            for (var name in data.validation_summary) {
                if (data.validation_summary[name].status === 'PASS') passed++;
                else failed++;
                totalFailedRecords += data.validation_summary[name].failed_records;
            }
            
            var html = '<div class="results-header">';
            html += '<div><h2>📊 Validation Results</h2>';
            html += '<p class="timestamp">Validated: ' + timestamp + ' | File: ' + data.filename + '</p></div>';
            html += '<div><button class="btn btn-success" onclick="downloadCSV()">📥 Download Results as CSV</button></div>';
            html += '</div>';
            
            html += '<div class="summary-cards">';
            html += '<div class="card"><h3>Total Records</h3><div class="value">' + data.total_records + '</div></div>';
            html += '<div class="card success"><h3>Validators Passed</h3><div class="value">' + passed + '</div></div>';
            html += '<div class="card ' + (failed > 0 ? 'fail' : 'success') + '"><h3>Validators Failed</h3><div class="value">' + failed + '</div></div>';
            html += '<div class="card ' + (totalFailedRecords > 0 ? 'fail' : 'success') + '"><h3>Total Failed Records</h3><div class="value">' + totalFailedRecords + '</div></div>';
            html += '</div>';
            
            for (var name in data.detailed_results) {
                var r = data.detailed_results[name];
                var statusClass = r.status.toLowerCase();
                var displayName = name.replace(/_/g, ' ').replace(/\\b\\w/g, function(l) { return l.toUpperCase(); });
                
                html += '<div class="validator-result ' + statusClass + '">';
                html += '<h4><span>' + displayName + '</span><span class="status-badge ' + statusClass + '">' + r.status + '</span></h4>';
                html += '<p><strong>Failed Records:</strong> ' + r.failed_records + ' | <strong>Failure Count:</strong> ' + r.failure_count + '</p>';
                
                if (r.failures && r.failures.length > 0) {
                    html += '<div style="margin-top: 10px;"><strong>Details (showing first 5):</strong><ul style="margin-top: 5px; padding-left: 20px;">';
                    var limit = Math.min(r.failures.length, 5);
                    for (var i = 0; i < limit; i++) {
                        var f = r.failures[i];
                        var detailMsg = 'Row ' + f.row_index;
                        if (f.field) detailMsg += ' - Field: ' + f.field;
                        if (f.invalid_value !== undefined) detailMsg += ' - Value: "' + f.invalid_value + '"';
                        if (f.error) detailMsg += ' - ' + f.error;
                        if (f.expected_range) detailMsg += ' - Expected: ' + f.expected_range;
                        html += '<li class="error-detail">' + detailMsg + '</li>';
                    }
                    if (r.failures.length > 5) {
                        html += '<li class="error-detail">... and ' + (r.failures.length - 5) + ' more failures</li>';
                    }
                    html += '</ul></div>';
                }
                html += '</div>';
            }
            
            results.innerHTML = html;
            results.className = 'results show';
            results.scrollIntoView({behavior: 'smooth'});
        }
        
        function downloadCSV() {
            if (!validationResults) return;
            
            var csv = 'Validator Name,Status,Failed Records,Failure Count,Error Details\\n';
            for (var name in validationResults.detailed_results) {
                var r = validationResults.detailed_results[name];
                var errorDetails = '';
                if (r.failures && r.failures.length > 0) {
                    errorDetails = r.failures.map(function(f) {
                        return 'Row ' + f.row_index + (f.field ? ':' + f.field : '') + (f.invalid_value ? '="' + f.invalid_value + '"' : '');
                    }).join('; ');
                }
                csv += name + ',' + r.status + ',' + r.failed_records + ',' + r.failure_count + ',"' + errorDetails + '"\\n';
            }
            
            var blob = new Blob([csv], { type: 'text/csv' });
            var url = window.URL.createObjectURL(blob);
            var a = document.createElement('a');
            a.href = url;
            var timestamp = new Date().toISOString().split('T')[0];
            a.download = 'validation_results_' + timestamp + '_' + validationResults.filename.replace('.csv', '') + '.csv';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }
        
        function clearForm() {
            document.getElementById('file').value = '';
            document.getElementById('fileInfo').style.display = 'none';
            document.getElementById('refdate').value = '';
            document.getElementById('error').className = 'error';
            document.getElementById('results').className = 'results';
            validationResults = null;
            currentFilename = '';
            window.scrollTo({top: 0, behavior: 'smooth'});
        }
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/validate', methods=['POST'])
def validate():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded. Please select a CSV file.'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected. Please choose a file to upload.'}), 400
    
    if not file.filename.lower().endswith('.csv'):
        return jsonify({'error': 'Invalid file type. Please upload a CSV file only.'}), 400
    
    validators = request.form.getlist('validators')
    if not validators:
        return jsonify({'error': 'No validators selected. Please choose at least one validator to run.'}), 400
    
    reference_date = request.form.get('reference_date')
    
    try:
        file_content = file.stream.read().decode('utf-8')
        df = pd.read_csv(io.StringIO(file_content))
        
        if df.empty:
            return jsonify({'error': 'The uploaded CSV file is empty. Please upload a file with data.'}), 400
        
        validator_map = {
            'missing_fields': lambda: validate_missing_critical_fields(df),
            'invalid_data_types': lambda: validate_invalid_data_types(df),
            'future_dates': lambda: validate_future_dates(df),
            'out_of_range': lambda: validate_out_of_range_values(df),
            'duplicates': lambda: validate_duplicate_records(df),
            'patient_ids': lambda: validate_patient_ids(df),
            'missing_visit': lambda: validate_missing_visit_data(df),
            'age_consistency': lambda: validate_age_consistency(df),
            'gender_based': lambda: validate_gender_based_tests(df),
            'data_completeness': lambda: validate_data_completeness(df)
        }
        
        results = {
            'filename': file.filename,
            'total_records': len(df),
            'validation_summary': {},
            'detailed_results': {}
        }
        
        for vname in validators:
            if vname in validator_map:
                try:
                    result = validator_map[vname]()
                    results['detailed_results'][vname] = result
                    results['validation_summary'][vname] = {
                        'status': result['status'],
                        'failed_records': int(result['failed_records'])
                    }
                except Exception as e:
                    results['detailed_results'][vname] = {
                        'status': 'ERROR',
                        'failed_records': 0,
                        'failure_count': 0,
                        'error': str(e)
                    }
        
        results = convert_to_serializable(results)
        return jsonify(results)
    
    except pd.errors.EmptyDataError:
        return jsonify({'error': 'The CSV file is empty or malformed. Please check your file.'}), 400
    except pd.errors.ParserError:
        return jsonify({'error': 'Error parsing CSV. Please ensure the file is a valid CSV format.'}), 400
    except UnicodeDecodeError:
        return jsonify({'error': 'File encoding error. Please ensure the file is UTF-8 encoded.'}), 400
    except Exception as e:
        return jsonify({'error': 'Unexpected error: ' + str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
