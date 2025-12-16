import React from 'react';
import { FiDownload, FiCheckCircle } from 'react-icons/fi';

const ResultsList = ({ results }) => {
  const handleDownload = (filename) => {
    window.open(`/api/download/${filename}`, '_blank');
  };

  if (results.length === 0) return null;

  return (
    <div className="card">
      <h2><FiCheckCircle /> Formatted Resumes</h2>
      <div className="results-list">
        {results.map((result, index) => (
          <div key={index} className="result-item">
            <div className="result-info">
              <h3>{result.name || 'Resume'}</h3>
              <p>Original: {result.original}</p>
              <p style={{fontSize: '0.85em', color: '#666'}}>
                Format: {result.filename.endsWith('.pdf') ? 'PDF' : 'DOCX'}
              </p>
            </div>
            <button
              className="btn-download"
              onClick={() => handleDownload(result.filename)}
            >
              <FiDownload /> Download {result.filename.endsWith('.pdf') ? 'PDF' : 'DOCX'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ResultsList;
