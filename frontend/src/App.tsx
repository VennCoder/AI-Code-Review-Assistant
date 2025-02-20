import React, { useState } from 'react';
import axios from 'axios';

const App: React.FC = () => {
    const [code, setCode] = useState<string>('');
    const [results, setResults] = useState<any>(null);

    const analyzeCode = async () => {
        try {
            const response = await axios.post('http://localhost:5000/analyze', { code });
            setResults(response.data);
        } catch (error) {
            console.error("Error analyzing code", error);
        }
    };

    return (
        <div>
            <h1>AI Code Review Tool</h1>
            <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="Paste your code here"
                style={{ width: '100%', height: '200px' }}
            />
            <button onClick={analyzeCode}>Analyze Code</button>

            {results && (
                <div>
                    <h3>Linter Results</h3>
                    <pre>{results.linter_results}</pre>

                    <h3>ML Results</h3>
                    <pre>{results.ml_results.analysis}</pre>
                </div>
            )}
        </div>
    );
};

export default App;
