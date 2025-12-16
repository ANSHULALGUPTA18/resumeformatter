import React, { useState, useRef, useEffect } from 'react';
import './DownloadPhase.css';

// v2.1 - Back button in header
const DownloadPhase = ({ results, onBack, onStartOver, darkMode, toggleDarkMode }) => {
  const [selectedPreview, setSelectedPreview] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [editorConfig, setEditorConfig] = useState(null);
  const [downloadingFile, setDownloadingFile] = useState(null);
  const [headerVisible, setHeaderVisible] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);
  const [showPopup, setShowPopup] = useState(true);
  const previewContainerRef = useRef(null);
  const editorInstanceRef = useRef(null);
  
  const handleSaveAndDownload = async (result) => {
    const filename = result.filename;
    const candidateName = result.name || 'Resume';
    const templateName = result.template_name || 'Template';
    
    setDownloadingFile(filename);
    
    try {
      console.log('💾 Triggering OnlyOffice save...');
      
      // Trigger OnlyOffice to save the document
      if (editorInstanceRef.current) {
        try {
          // Call the OnlyOffice save method
          editorInstanceRef.current.processSaveResult(true);
          console.log('✅ OnlyOffice save triggered');
        } catch (saveError) {
          console.warn('⚠️ Could not trigger explicit save, relying on auto-save:', saveError);
        }
      }
      
      // Wait for OnlyOffice to complete the save (callback to backend)
      console.log('⏳ Waiting for save to complete...');
      await new Promise(resolve => setTimeout(resolve, 5000));
      
      console.log('📥 Downloading saved file...');
      
      // Build download URL with proper filename
      const downloadUrl = `/api/download/${filename}?name=${encodeURIComponent(candidateName)}&template=${encodeURIComponent(templateName)}`;
      
      // Fetch the file
      const response = await fetch(downloadUrl);
      
      if (!response.ok) {
        throw new Error(`Download failed: ${response.statusText}`);
      }
      
      // Get the blob
      const blob = await response.blob();
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${candidateName}_${templateName}.docx`;
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log('✅ Save & Download completed');
    } catch (error) {
      console.error('❌ Save & Download error:', error);
      alert('Save & Download failed. Please try again.');
    } finally {
      // Clear downloading state
      setTimeout(() => setDownloadingFile(null), 1000);
    }
  };
  
  const handleDownload = async (result) => {
    // Just call save and download
    await handleSaveAndDownload(result);
  };
  
  const handlePreviewClick = async (result) => {
    setSelectedPreview(result);
    setPreviewLoading(true);
    setShowPopup(true); // Show popup when opening preview
  };

  const togglePopup = () => {
    setShowPopup(!showPopup);
  };

  // Handle scroll to show/hide header
  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      
      if (currentScrollY > lastScrollY && currentScrollY > 100) {
        // Scrolling down & past threshold
        setHeaderVisible(false);
      } else if (currentScrollY < lastScrollY) {
        // Scrolling up
        setHeaderVisible(true);
      }
      
      setLastScrollY(currentScrollY);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, [lastScrollY]);
  
  // Load OnlyOffice editor when preview is selected
  useEffect(() => {
    if (!selectedPreview || !previewContainerRef.current) {
      return;
    }

    const loadEditor = async () => {
      try {
        console.log('🔄 Loading editor for:', selectedPreview.filename);
        
        // Destroy existing editor if any
        if (editorInstanceRef.current) {
          try {
            console.log('🗑️ Destroying previous editor...');
            editorInstanceRef.current.destroyEditor();
            editorInstanceRef.current = null;
          } catch (e) {
            console.log('⚠️ Editor already destroyed');
          }
        }
        
        // Wait for DocsAPI to be available
        const waitForDocsAPI = () => {
          return new Promise((resolve, reject) => {
            if (window.DocsAPI) {
              console.log('✅ DocsAPI already loaded');
              resolve();
              return;
            }
            
            console.log('⏳ Waiting for DocsAPI to load...');
            let attempts = 0;
            const checkInterval = setInterval(() => {
              attempts++;
              if (window.DocsAPI) {
                console.log('✅ DocsAPI loaded!');
                clearInterval(checkInterval);
                resolve();
              } else if (attempts > 50) {
                clearInterval(checkInterval);
                reject(new Error('DocsAPI failed to load after 10 seconds'));
              }
            }, 200);
          });
        };
        
        // Wait for API
        try {
          await waitForDocsAPI();
        } catch (error) {
          console.error('❌ DocsAPI failed to load:', error);
          alert('OnlyOffice API failed to load. Please ensure OnlyOffice Docker container is running on port 8080.');
          setPreviewLoading(false);
          return;
        }
        
        // Fetch editor config
        console.log('📡 Fetching editor config...');
        const response = await fetch(`/api/onlyoffice/config/${selectedPreview.filename}`);
        
        if (!response.ok) {
          console.error('❌ Failed to fetch config:', response.status);
          alert(`Failed to fetch editor config: ${response.status}`);
          setPreviewLoading(false);
          return;
        }
        
        const config = await response.json();
        console.log('📦 Config received:', config);
        
        if (config.success) {
          console.log('✅ Config valid, initializing editor...');
          setEditorConfig(config.config);
          
          // Wait for container to be ready
          setTimeout(() => {
            if (!previewContainerRef.current) {
              console.error('❌ Container ref is null');
              setPreviewLoading(false);
              return;
            }
            
            if (!window.DocsAPI) {
              console.error('❌ DocsAPI not available');
              setPreviewLoading(false);
              return;
            }
            
            try {
              // Use a stable, fixed container ID managed by React
              const containerId = 'onlyoffice-editor';
              const mountEl = document.getElementById(containerId);
              if (!mountEl) {
                console.error('❌ Editor mount element not found');
                setPreviewLoading(false);
                return;
              }
              console.log('🚀 Creating editor instance with ID:', containerId);
              console.log('📝 Editor config:', config.config);
              
              const editor = new window.DocsAPI.DocEditor(containerId, config.config);
              editorInstanceRef.current = editor;
              setPreviewLoading(false);
              console.log('✅ Editor loaded successfully!');
            } catch (error) {
              console.error('❌ Error creating editor:', error);
              alert(`Error creating editor: ${error.message}`);
              setPreviewLoading(false);
            }
          }, 500);
        } else {
          console.error('❌ Config not successful:', config);
          alert('Failed to get valid editor configuration');
          setPreviewLoading(false);
        }
      } catch (error) {
        console.error('❌ Error loading editor:', error);
        alert(`Error loading editor: ${error.message}`);
        setPreviewLoading(false);
      }
    };

    loadEditor();
    
    // Cleanup on unmount
    return () => {
      if (editorInstanceRef.current) {
        try {
          console.log('🧹 Cleaning up editor...');
          editorInstanceRef.current.destroyEditor();
          editorInstanceRef.current = null;
        } catch (e) {
          console.log('⚠️ Cleanup: Editor already destroyed');
        }
      }
    };
  }, [selectedPreview]);


  const handleDownloadAll = () => {
    results.forEach((result, index) => {
      setTimeout(() => {
        handleDownload(result);
      }, index * 500); // Stagger downloads by 500ms
    });
  };

  // If no results or results is empty, show error message
  if (!results || results.length === 0) {
    return (
      <div className="download-phase-new">
        <div className="message-content">
          <div className="message-icon">❌</div>
          <h3>Formatting Failed</h3>
          <p>Please try again. If the problem persists, check your resume and template files or contact support.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="download-phase-new">
      {/* Status Bar with Back Button and Tabs */}
      <div className={`status-bar ${!headerVisible ? 'hidden' : ''}`}>
        <button className="back-button-header" onClick={onBack} aria-label="Go back">
          <i className="fas fa-arrow-left"></i>
        </button>
        <div className="tabs-section">
          <span className="formatted-label">Formatted Resumes:</span>
          <div className="file-tabs-wrapper">
            <div className="file-tabs-container">
              {results.map((result, index) => (
                <div
                  key={index}
                  className={`file-tab-pill ${selectedPreview?.filename === result.filename ? 'active' : ''}`}
                >
                  <i className="far fa-file-alt" style={{ fontSize: '14px', color: '#6b7280' }}></i>
                  <span 
                    className="tab-pill-text"
                    onClick={() => handlePreviewClick(result)}
                  >
                    {result.name || result.filename || `Resume_${index + 1}`}
                  </span>
                  <button
                    className="tab-download-icon"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDownload(result);
                    }}
                    title="Download"
                  >
                    <i className="fas fa-download"></i>
                  </button>
                </div>
              ))}
            </div>
          </div>
          <button className="format-btn-new" onClick={onStartOver}>
            Format
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="main-content-new">
        {!selectedPreview ? (
          /* Success Card */
          <div className="success-card-container">
            <div className="success-card">
              <div className="success-icon-circle">
                <i className="fas fa-check"></i>
              </div>
              <h1 className="success-title">Your resumes are ready!</h1>
              <p className="success-subtitle">Click tabs above to view or download your formatted resumes</p>
            </div>
          </div>
        ) : (
          /* OnlyOffice Editor */
          <div className="editor-container-new">
            {previewLoading && (
              <div className="editor-loader-new">
                <div className="loader-spinner-new"></div>
                <p className="loader-text-new">Loading editor...</p>
              </div>
            )}
            <div 
              className="onlyoffice-editor-wrapper"
              style={{ 
                display: previewLoading ? 'none' : 'block',
                width: '100%',
                height: '100%'
              }}
            >
              <div id="onlyoffice-editor" ref={previewContainerRef} style={{ height: '100%', width: '100%' }} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DownloadPhase;
