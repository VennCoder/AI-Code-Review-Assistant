from flask import Flask, request, jsonify
import subprocess
import os
import tempfile
import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification
from flask_cors import CORS  # Import CORS to handle cross-origin requests

# Initialize the app and load the model and tokenizer for CodeBERT
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

tokenizer = RobertaTokenizer.from_pretrained('microsoft/codebert-base')
model = RobertaForSequenceClassification.from_pretrained('microsoft/codebert-base')

# Function to analyze code
def analyze_code(code):
    # Check for syntax errors using exec() to catch SyntaxError immediately
    syntax_error = None
    try:
        exec(code)
    except SyntaxError as e:
        syntax_error = f"SyntaxError detected: {e}"

    # Save the code to a temporary file for linting and security checks
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.py')
    temp_file.write(code.encode('utf-8'))
    temp_file.close()
    
    # Pylint analysis
    pylint_command = f'pylint {temp_file.name} --output-format=text'
    pylint_output = subprocess.getoutput(pylint_command)
    
    # Parse the pylint output into best practices and linter results
    best_practices, linter_results = parse_pylint_output(pylint_output)
    
    # Machine learning analysis with CodeBERT
    ml_results = analyze_with_codebert(code)
    
    # Security analysis with Bandit (skip if there's a SyntaxError)
    if not syntax_error:
        bandit_command = f'bandit -r {temp_file.name}'
        bandit_output = subprocess.getoutput(bandit_command)
        security_results = parse_bandit_output(bandit_output)
    else:
        security_results = "Skipping Bandit due to syntax errors."
    
    # Clean up the temporary file
    os.remove(temp_file.name)

    # Adjust final result: flag critical issues only when multiple checks raise concerns
    if ml_results['confidence'] < 0.75 and not linter_results and "No issues identified." in security_results:
        ml_results['analysis'] = "The code is clean according to both the linter and security analysis, with low risk flagged by the machine learning model."
    
    # Return the analysis results, including any syntax errors detected
    return {
        "syntax_error": syntax_error,
        "best_practices": best_practices,
        "linter_results": linter_results,
        "ml_results": ml_results['analysis'],
        "security_analysis": security_results
    }

# Helper functions
def parse_pylint_output(output):
    """Parse the pylint output and convert it into natural language suggestions."""
    best_practices = []
    linter_issues = []
    
    for line in output.splitlines():
        if "C0304" in line:
            best_practices.append("1. Missing a final newline at the end of the file.")
        if "C0114" in line:
            best_practices.append("2. There is no module-level docstring. You should add a comment at the beginning of the file explaining what it does.")
        if "C0116" in line:
            best_practices.append("3. The function is missing a docstring. You should add a comment inside the function explaining what it does.")
        if "W0125" in line:
            best_practices.append("4. There are conditional statements with constant values ('if True'). These always evaluate to 'True', making the conditions unnecessary and potentially confusing.")
        if "W292" in line:
            linter_issues.append("1. There is no newline at the end of the file, which is generally considered bad practice in Python.")
    
    return "\n".join(best_practices), "\n".join(linter_issues)

def analyze_with_codebert(code):
    """Use CodeBERT to analyze the code for potential issues with a stricter threshold."""
    inputs = tokenizer(code, return_tensors="pt", truncation=True, max_length=512)
    outputs = model(**inputs)
    logits = outputs.logits
    probabilities = torch.softmax(logits, dim=-1).squeeze()

    # Adjust the threshold to reduce false positives
    low_threshold = 0.75  # Increased to reduce false positives on simple code
    high_threshold = 0.90  # Raised to make critical warnings stricter
    prediction_confidence = probabilities[1].item()  # Confidence of the "issue" class

    if prediction_confidence > high_threshold:
        return {"analysis": f"Critical issues detected with high confidence ({prediction_confidence:.2f}). Immediate review needed.", "confidence": prediction_confidence}
    elif prediction_confidence > low_threshold:
        return {"analysis": f"Potential issues detected with a confidence of {prediction_confidence:.2f}. Review recommended.", "confidence": prediction_confidence}
    else:
        return {"analysis": f"The code appears clean with a confidence of {1 - prediction_confidence:.2f}.", "confidence": prediction_confidence}

def parse_bandit_output(output):
    """Parse the Bandit output and return a natural language summary."""
    if "No issues identified." in output:
        return "The security analysis did not find any issues with this code. It appears safe from known security vulnerabilities."
    else:
        return output  # You can enhance this to parse more detailed issues if required

# Define the API endpoint
@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    code = data.get('code', '')
    
    # Analyze the code
    analysis_results = analyze_code(code)
    
    # Return the results as JSON
    return jsonify(analysis_results)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
