import React from 'react';
import { FiTrash2, FiFileText } from 'react-icons/fi';

const TemplateList = ({ templates, selectedTemplate, onSelect, onDelete }) => {
  return (
    <div className="card">
      <h2><FiFileText /> Available Templates</h2>
      {templates.length === 0 ? (
        <p className="empty-state">No templates uploaded yet. Upload one to get started!</p>
      ) : (
        <div className="template-list">
          {templates.map((template) => (
            <div
              key={template.id}
              className={`template-item ${selectedTemplate === template.id ? 'selected' : ''}`}
              onClick={() => onSelect(template.id)}
            >
              <div className="template-info">
                <h3>{template.name}</h3>
                <p>Uploaded: {new Date(template.upload_date).toLocaleDateString()}</p>
              </div>
              <button
                className="btn-delete"
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(template.id);
                }}
              >
                <FiTrash2 />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TemplateList;
