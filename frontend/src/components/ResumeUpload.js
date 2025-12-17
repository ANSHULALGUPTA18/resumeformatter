import React, { useState } from 'react';
import { FiUploadCloud } from 'react-icons/fi';

const ResumeUpload = ({ selectedTemplate, onFormatSuccess }) => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedTemplate) {
      alert('Please select a template first');
      return;
    }

    if (!files || files.length === 0) {
      alert('Please select at least one resume');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('template_id', selectedTemplate);
    
    // Add all files to form data
    files.forEach((file) => {
      formData.append('resume_files', file);
    });

    try {
      const response = await fetch('/api/format', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      
      if (data.success) {
        alert(`Successfully formatted ${data.files.length} resume(s)!`);
        setFiles([]);
        onFormatSuccess(data.files);
      } else {
        alert(data.message || 'Formatting failed');
      }
    } catch (error) {
      alert('Error formatting resumes');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2><FiUploadCloud /> Upload Resumes to Format</h2>
      {!selectedTemplate ? (
        <p className="warning">Please select a template first</p>
      ) : (
        <form onSubmit={handleSubmit}>
          <input
            type="file"
            accept=".pdf,.doc,.docx,.odt,.rtf"
            multiple
            onChange={(e) => setFiles(Array.from(e.target.files))}
            required
          />
          {files.length > 0 && (
            <p className="file-count">{files.length} file(s) selected</p>
          )}
          <button type="submit" disabled={loading} className="btn-success">
            {loading ? 'Formatting...' : 'Format Resumes'}
          </button>
        </form>
      )}
    </div>
  );
};

export default ResumeUpload;
