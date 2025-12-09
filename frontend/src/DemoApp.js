import React, { useState, useEffect } from 'react';
import TemplateSelectionDemo from './components/TemplateSelectionDemo';
import './App.css';

function DemoApp() {
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [darkMode, setDarkMode] = useState(false);

  // Fetch templates on component mount
  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const response = await fetch('/api/templates');
      const data = await response.json();
      if (data.success) {
        setTemplates(data.templates);
      }
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const handleTemplateSelect = (templateId) => {
    setSelectedTemplate(templateId);
    console.log('Selected template:', templateId);
  };

  const handleTemplateDelete = async (templateId) => {
    try {
      const response = await fetch(`/api/templates/${templateId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        // Refresh templates after deletion
        await fetchTemplates();
        if (selectedTemplate === templateId) {
          setSelectedTemplate(null);
        }
      } else {
        alert('Failed to delete template');
      }
    } catch (error) {
      console.error('Error deleting template:', error);
      alert('Error deleting template');
    }
  };

  const handleTemplateUpload = () => {
    // Refresh templates after upload
    fetchTemplates();
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  return (
    <div className={`app ${darkMode ? 'dark-mode' : ''}`}>
      {/* Demo Header */}
      <div style={{
        position: 'fixed',
        top: 0,
        right: 0,
        zIndex: 1002,
        padding: '8px 16px',
        background: 'rgba(0, 0, 0, 0.8)',
        color: 'white',
        fontSize: '12px',
        borderBottomLeftRadius: '8px'
      }}>
        <button 
          onClick={toggleDarkMode}
          style={{
            background: 'none',
            border: '1px solid white',
            color: 'white',
            padding: '4px 8px',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '12px',
            marginRight: '8px'
          }}
        >
          {darkMode ? '☀️ Light' : '🌙 Dark'}
        </button>
        <a 
          href="/"
          style={{
            color: 'white',
            textDecoration: 'none',
            padding: '4px 8px',
            border: '1px solid white',
            borderRadius: '4px',
            fontSize: '12px'
          }}
        >
          ← Back to Main App
        </a>
      </div>

      <TemplateSelectionDemo
        templates={templates}
        selectedTemplate={selectedTemplate}
        onSelect={handleTemplateSelect}
        onDelete={handleTemplateDelete}
        onUpload={handleTemplateUpload}
        darkMode={darkMode}
        onBack={() => window.location.href = '/'}
      />
    </div>
  );
}

export default DemoApp;
