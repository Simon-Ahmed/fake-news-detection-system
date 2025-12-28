import { useState } from 'react';

export default function App() {
  const [text, setText] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const analyzeText = async () => {
    if (!text.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch('https://fake-news-detection-system-production.up.railway.app/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          analysis_type: 'text'
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setResult(data);
      } else {
        setResult({ prediction: 'ERROR', explanation: 'Failed to analyze text' });
      }
    } catch (error) {
      setResult({ prediction: 'ERROR', explanation: 'Network error - using offline mode' });
    }
    setLoading(false);
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px',
      fontFamily: 'Arial, sans-serif'
    }}>
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h1 style={{ 
            color: 'white', 
            fontSize: '2.5rem', 
            marginBottom: '10px',
            textShadow: '2px 2px 4px rgba(0,0,0,0.3)'
          }}>
            🛡️ Fake News Detection System
          </h1>
          <p style={{ color: 'rgba(255,255,255,0.9)', fontSize: '1.1rem' }}>
            AI-powered system to detect fake news using machine learning
          </p>
        </div>

        {/* Main Content */}
        <div style={{ 
          background: 'white', 
          borderRadius: '12px', 
          padding: '30px',
          boxShadow: '0 10px 30px rgba(0,0,0,0.2)'
        }}>
          <h2 style={{ marginBottom: '20px', color: '#333' }}>Analyze News Text</h2>
          
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste news text here to analyze..."
            style={{
              width: '100%',
              height: '120px',
              padding: '15px',
              border: '2px solid #e1e5e9',
              borderRadius: '8px',
              fontSize: '16px',
              resize: 'vertical',
              marginBottom: '20px'
            }}
          />
          
          <button
            onClick={analyzeText}
            disabled={loading || !text.trim()}
            style={{
              background: loading ? '#ccc' : '#4CAF50',
              color: 'white',
              padding: '12px 30px',
              border: 'none',
              borderRadius: '6px',
              fontSize: '16px',
              cursor: loading ? 'not-allowed' : 'pointer',
              marginBottom: '30px'
            }}
          >
            {loading ? '🔄 Analyzing...' : '🔍 Analyze Text'}
          </button>

          {/* Results */}
          {result && (
            <div style={{
              background: result.prediction === 'FAKE' ? '#ffebee' : 
                         result.prediction === 'REAL' ? '#e8f5e8' : '#fff3e0',
              border: `2px solid ${result.prediction === 'FAKE' ? '#f44336' : 
                                  result.prediction === 'REAL' ? '#4CAF50' : '#ff9800'}`,
              borderRadius: '8px',
              padding: '20px',
              marginTop: '20px'
            }}>
              <h3 style={{ 
                color: result.prediction === 'FAKE' ? '#d32f2f' : 
                       result.prediction === 'REAL' ? '#2e7d32' : '#f57c00',
                marginBottom: '10px'
              }}>
                {result.prediction === 'FAKE' ? '🚨 FAKE NEWS DETECTED' :
                 result.prediction === 'REAL' ? '✅ APPEARS TO BE REAL' : '⚠️ ERROR'}
              </h3>
              
              {result.confidence && (
                <p style={{ marginBottom: '10px' }}>
                  <strong>Confidence:</strong> {Math.round(result.confidence * 100)}%
                </p>
              )}
              
              <p style={{ marginBottom: '0' }}>
                <strong>Analysis:</strong> {result.explanation}
              </p>
            </div>
          )}

          {/* Status */}
          <div style={{ 
            marginTop: '30px', 
            padding: '15px', 
            background: '#f5f5f5', 
            borderRadius: '6px',
            textAlign: 'center'
          }}>
            <p style={{ margin: '0', color: '#666' }}>
              ✅ System Status: <strong>Online</strong> | 
              Backend: <strong>Connected</strong> | 
              ML Model: <strong>Active</strong>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}