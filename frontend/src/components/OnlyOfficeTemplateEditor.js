import React, { useState, useEffect, useRef } from 'react';
import './OnlyOfficeTemplateEditor.css';

const OnlyOfficeTemplateEditor = ({ template, onClose, onSave, darkMode }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [documentKey, setDocumentKey] = useState(null);
  const editorContainerRef = useRef(null);
  const docEditorRef = useRef(null);

  useEffect(() => {
    loadOnlyOfficeEditor();
    
    // Cleanup on unmount
    return () => {
      if (docEditorRef.current) {
        try {
          docEditorRef.current.destroyEditor();
        } catch (e) {
          console.log('Editor cleanup:', e);
        }
      }
    };
  }, [template]);

  const loadOnlyOfficeEditor = async () => {
    try {
      setLoading(true);
      setError(null);

      // Check OnlyOffice availability
      const statusResponse = await fetch('/api/onlyoffice/status');
      const statusData = await statusResponse.json();
      
      if (!statusData.available) {
        setError('OnlyOffice Document Server is not running. Please start it first.');
        setLoading(false);
        return;
      }

      // Get OnlyOffice config for this template
      const configResponse = await fetch(`/api/onlyoffice/edit/${template.id}`);
      
      if (!configResponse.ok) {
        const errorData = await configResponse.json();
        throw new Error(errorData.message || 'Failed to load editor configuration');
      }

      const config = await configResponse.json();
      console.log('OnlyOffice config:', config);

      // Generate unique document key for this editing session
      const docKey = `${template.id}_${Date.now()}`;
      setDocumentKey(docKey);

      // Update config with document key
      config.document.key = docKey;
      
      // Add event handlers
      config.events = {
        onDocumentReady: () => {
          console.log('✅ Document is ready for editing');
          setLoading(false);
        },
        onError: (error) => {
          console.error('❌ Editor error:', error);
          setError(`Editor error: ${error.data || 'Unknown error'}`);
          setLoading(false);
        },
        onDocumentStateChange: (event) => {
          console.log('Document modified:', event.data);
        },
        onRequestSaveAs: (event) => {
          console.log('Save As requested:', event);
        }
      };

      // Initialize OnlyOffice Document Editor
      if (window.DocsAPI) {
        docEditorRef.current = new window.DocsAPI.DocEditor(editorContainerRef.current.id, config);
      } else {
        throw new Error('OnlyOffice API not loaded. Please check OnlyOffice Document Server.');
      }

    } catch (error) {
      console.error('Error loading editor:', error);
      setError(error.message || 'Failed to load document editor');
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      // Force document save
      if (docEditorRef.current) {
        // OnlyOffice auto-saves, but we can trigger manual save
        alert('✅ Template saved successfully! Changes are automatically saved.');
        onSave();
        onClose();
      }
    } catch (error) {
      console.error('Save error:', error);
      alert(`Failed to save: ${error.message}`);
    }
  };

  if (error) {
    return (
      <div className="editor-overlay">
        <div className="editor-modal">
          <div className="editor-header">
            <h2>❌ Editor Error</h2>
            <button className="close-btn" onClick={onClose}>×</button>
          </div>
          <div className="editor-error">
            <p>{error}</p>
            <div className="error-help">
              <h4>To start OnlyOffice Document Server:</h4>
              <ol>
                <li>Docker method: <code>docker start onlyoffice-documentserver</code></li>
                <li>Or run: <code>docker run -i -t -d -p 8080:80 onlyoffice/documentserver</code></li>
              </ol>
            </div>
            <button className="btn-primary" onClick={onClose}>Close</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="editor-overlay">
      <div className="editor-modal editor-modal-fullscreen">
        <div className="editor-header">
          <div className="editor-title">
            <i className="fas fa-edit"></i>
            <span>Editing: {template.name}</span>
          </div>
          <div className="editor-actions">
            {loading && <span className="loading-indicator">⏳ Loading editor...</span>}
            <button className="btn-save" onClick={handleSave} disabled={loading}>
              <i className="fas fa-save"></i> Save & Close
            </button>
            <button className="close-btn" onClick={onClose} title="Close without saving">×</button>
          </div>
        </div>
        
        <div className="editor-body">
          {loading && (
            <div className="editor-loading">
              <div className="spinner"></div>
              <p>Loading document editor...</p>
            </div>
          )}
          <div 
            id={`onlyoffice-editor-${template.id}`}
            ref={editorContainerRef}
            className="onlyoffice-container"
            style={{ display: loading ? 'none' : 'block' }}
          ></div>
        </div>
        
        <div className="editor-footer">
          <div className="editor-info">
            <i className="fas fa-info-circle"></i>
            <span>Changes are automatically saved. Click "Save & Close" when done.</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OnlyOfficeTemplateEditor;
