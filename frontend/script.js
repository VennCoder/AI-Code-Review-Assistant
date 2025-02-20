document.getElementById('analyze-btn').addEventListener('click', function() {
    const code = document.getElementById('code-input').value;
    const loader = document.getElementById('loader');
    const resultsDiv = document.getElementById('results');

    // Clear previous results
    resultsDiv.style.display = "none";
    document.getElementById('best-practices').innerHTML = '';
    document.getElementById('linter-results').innerHTML = '';
    document.getElementById('ml-results').innerHTML = '';
    document.getElementById('security-results').innerHTML = '';

    // Show loader
    loader.style.display = 'block';

    // Send code to the Flask backend
    fetch('http://127.0.0.1:5000/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code }),
    })
    .then(response => response.json())
    .then(data => {
        loader.style.display = 'none';
        resultsDiv.style.display = 'block';

        // Display results
        document.getElementById('best-practices').innerHTML = `<h3>Best Practices:</h3><p>${data.best_practices}</p>`;
        document.getElementById('linter-results').innerHTML = `<h3>Linter Results:</h3><p>${data.linter_results}</p>`;
        document.getElementById('ml-results').innerHTML = `<h3>ML Analysis:</h3><p>${data.ml_results}</p>`;
        document.getElementById('security-results').innerHTML = `<h3>Security Analysis:</h3><p>${data.security_analysis}</p>`;
    })
    .catch(error => {
        loader.style.display = 'none';
        alert('Error analyzing code: ' + error);
    });
});
