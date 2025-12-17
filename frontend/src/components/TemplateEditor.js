import React, { useState, useEffect } from 'react';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import './TemplateEditor.css';

const TemplateEditor = ({ template, onClose, onSave, darkMode }) => {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    // Load template content
    fetchTemplateContent();
  }, [template]);

  const fetchTemplateContent = async () => {
    try {
      setLoading(true);
      console.log(`Fetching content for template: ${template.id}`);

      const response = await fetch(`/api/templates/${template.id}/content`);
      console.log(`Response status: ${response.status}`);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Server error:', errorText);
        alert(`Failed to load template: ${response.status} - ${errorText}`);
        onClose();
        return;
      }

      const data = await response.json();
      console.log('Template data received:', data);

      if (data.success) {
        setContent(data.content || '<p>No content found</p>');
      } else {
        alert(`Failed to load template: ${data.message || 'Unknown error'}`);
        onClose();
      }
    } catch (error) {
      console.error('Error loading template:', error);
      alert(`Error loading template: ${error.message}`);
      onClose();
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      console.log('Saving template content...');

      const response = await fetch(`/api/templates/${template.id}/content`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content }),
      });

      console.log(`Save response status: ${response.status}`);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Save error:', errorText);
        alert(`Failed to save template: ${response.status} - ${errorText}`);
        return;
      }

      const data = await response.json();
      console.log('Save response:', data);

      if (data.success) {
        alert('✅ Template saved successfully!');
        onSave();
        onClose();
      } else {
        alert('Failed to save template: ' + (data.message || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error saving template:', error);
      alert(`Error saving template: ${error.message}`);
    } finally {
      setSaving(false);
    }
  };

  // Quill editor modules configuration (basic toolbar)
  const modules = {
    toolbar: [
      [{ 'header': [1, 2, 3, false] }],
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      [{ 'align': [] }],
      ['link'],
      ['clean']
    ],
  };

  const formats = [
    'header',
    'bold', 'italic', 'underline', 'strike',
    'list', 'bullet',
    'align',
    'link'
  ];

  return (
    <div className="editor-overlay" onClick={onClose}>
      <div
        className={`editor-modal ${darkMode ? 'dark-mode' : ''}`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="editor-header">
          <div className="editor-title">
            <span className="editor-icon">✏️</span>
            <h2>Edit Template: {template.name}</h2>
          </div>
          <button className="editor-close-btn" onClick={onClose} title="Close">
            ×
          </button>
        </div>

        <div className="editor-body">
          {loading ? (
            <div className="editor-loading">
              <div className="spinner"></div>
              <p>Loading template...</p>
            </div>
          ) : (
            <ReactQuill
              theme="snow"
              value={content}
              onChange={setContent}
              modules={modules}
              formats={formats}
              placeholder="Start editing your template..."
              className="template-editor-quill"
            />
          )}
        </div>

        <div className="editor-footer">
          <div className="editor-info">
            <span className="info-text">
              💡 Basic text editing • Preserves most formatting • Complex edits use OnlyOffice
            </span>
          </div>
          <div className="editor-actions">
            <button
              className="btn-secondary"
              onClick={onClose}
              disabled={saving}
            >
              Cancel
            </button>
            <button
              className="btn-primary"
              onClick={handleSave}
              disabled={saving || loading}
            >
              {saving ? 'Saving...' : '💾 Save Changes'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TemplateEditor;
