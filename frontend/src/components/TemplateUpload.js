import React, { useState } from 'react';
import { FiUpload } from 'react-icons/fi';
import { uploadTemplate } from '../services/api';

const TemplateUpload = ({ onUploadSuccess }) => {
  const [templateName, setTemplateName] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!templateName || !file) {
      alert('Please provide template name and file');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('template_name', templateName);
    formData.append('template_file', file);

    try {
      const data = await uploadTemplate(formData);
      
      if (data.success) {
        alert('Template uploaded successfully!');
        setTemplateName('');
        setFile(null);
        onUploadSuccess();
      } else {
        alert(data.message || 'Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Error uploading template. Failed to fetch.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2><FiUpload /> Upload Resume Template</h2>
      <p className="info-text" style={{fontSize: '0.9em', color: '#666', marginBottom: '10px'}}>
        ✅ <strong>Supported formats:</strong> <strong>.pdf</strong>, <strong>.docx</strong>, and <strong>.doc</strong> templates. 
        Old .doc files will be automatically converted to .docx for better compatibility.
      </p>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Template Name (e.g., Company Standard Format)"
          value={templateName}
          onChange={(e) => setTemplateName(e.target.value)}
          required
        />
        <input
          type="file"
          accept=".pdf,.docx,.doc"
          onChange={(e) => setFile(e.target.files[0])}
          required
        />
        <button type="submit" disabled={loading} className="btn-primary">
          {loading ? 'Uploading...' : 'Upload Template'}
        </button>
      </form>
    </div>
  );
};

export default TemplateUpload;
