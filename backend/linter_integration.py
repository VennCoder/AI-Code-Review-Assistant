import subprocess

def run_eslint(code):
    """Run ESLint for JavaScript/TypeScript analysis."""
    with open('temp.js', 'w') as f:
        f.write(code)
    
    result = subprocess.run(['eslint', 'temp.js'], capture_output=True, text=True)
    return result.stdout

def run_flake8(code):
    """Run Flake8 for Python analysis."""
    with open('temp.py', 'w') as f:
        f.write(code)
    
    result = subprocess.run(['flake8', 'temp.py'], capture_output=True, text=True)
    return result.stdout

def run_linters(code):
    """Wrapper to run multiple linters based on language."""
    if code.strip().startswith(('function', 'const', 'let', 'var')):
        return run_eslint(code)
    else:
        return run_flake8(code)
