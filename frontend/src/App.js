import React, { useState, useEffect } from 'react';
import { useMsal } from '@azure/msal-react';
import WizardStepper from './components/WizardStepper';
import TemplateSelectionNew from './components/TemplateSelectionNew';
import ResumeUploadPhase from './components/ResumeUploadPhase';
import DownloadPhase from './components/DownloadPhase';
import './App.css';

// Clear localStorage immediately when the module loads, but preserve certain items
const savedDarkMode = localStorage.getItem('darkMode');
const savedFavorites = localStorage.getItem('templateFavorites');
localStorage.clear();
if (savedDarkMode) {
  localStorage.setItem('darkMode', savedDarkMode);
}
if (savedFavorites) {
  localStorage.setItem('templateFavorites', savedFavorites);
}

function App() {
  const { instance, accounts } = useMsal();
  const [currentStep, setCurrentStep] = useState(1); // Always start from step 1
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(null); // Don't persist template selection
  const [results, setResults] = useState([]); // Don't persist results
  const [isFormatting, setIsFormatting] = useState(false);
  const [darkMode, setDarkMode] = useState(savedDarkMode ? JSON.parse(savedDarkMode) : false);

  // Ensure fresh start on component mount
  useEffect(() => {
    // Force reset to step 1 (localStorage already cleared at module load)
    setCurrentStep(1);
    setSelectedTemplate(null);
    setResults([]);
  }, []);

  // No localStorage persistence - always start fresh

  // No browser history navigation - always start fresh

  // Toggle dark mode
  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem('darkMode', JSON.stringify(newMode));
  };

  // Logout handler
  const handleLogout = () => {
    instance.logoutPopup({
      postLogoutRedirectUri: "/",
      mainWindowRedirectUri: "/"
    });
  };

  // Get user info
  const userAccount = accounts[0];
  const userName = userAccount?.name || userAccount?.username || 'User';

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

  useEffect(() => {
    fetchTemplates();
  }, []);

  const handleTemplateDelete = async (templateId) => {
    console.log('🗑️ Starting deletion for template:', templateId);
    try {
      const response = await fetch(`/api/templates/${templateId}`, {
        method: 'DELETE'
      });
      
      console.log('📡 Delete response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('📋 Delete response data:', data);
      
      if (data.success) {
        console.log('✅ Template deleted successfully, refreshing list...');
        // Refresh templates immediately
        await fetchTemplates();
        if (selectedTemplate === templateId) {
          setSelectedTemplate(null);
        }
        console.log('✅ Template list refreshed');
        return { success: true };
      } else {
        const errorMsg = 'Error deleting template: ' + (data.message || 'Unknown error');
        console.error('❌', errorMsg);
        alert(errorMsg);
        throw new Error(errorMsg);
      }
    } catch (error) {
      console.error('❌ Delete error:', error);
      alert('Error deleting template: ' + error.message);
      throw error;
    }
  };

  const handleTemplateSelect = (templateId) => {
    setSelectedTemplate(templateId);
    // Auto-advance to next step after selection
    setTimeout(() => setCurrentStep(2), 500);
  };

  const handleTemplateUpload = () => {
    fetchTemplates();
  };

  const handleFormatSuccess = (formattedResults) => {
    setResults(formattedResults);
    setIsFormatting(false);
    setCurrentStep(3);
  };

  const handleStartOver = () => {
    setCurrentStep(1);
    setSelectedTemplate(null);
    setResults([]);
    // Clear localStorage
    localStorage.removeItem('currentStep');
    localStorage.removeItem('selectedTemplate');
    localStorage.removeItem('results');
  };

  const steps = [
    { number: 1, title: 'Select Template', icon: '📋' },
    { number: 2, title: 'Upload Resumes', icon: '📄' },
    { number: 3, title: 'Download Results', icon: '📥' }
  ];

  return (
    <div className={`App ${darkMode ? 'dark-mode' : ''} ${currentStep === 3 ? 'fullscreen-mode' : ''}`}>
      {currentStep !== 3 && (
        <header className="header">
          <div className="header-content">
            <div className="header-left">
              <div className="logo-circle">
                <img src="/logo.png" alt="Resume Formatter Pro" className="logo-image" />
              </div>
              <div className="brand-info">
                <h1 className="brand-title">Resume Formatter Pro</h1>
                <p className="brand-subtitle">powered by Techgene</p>
              </div>
            </div>
            <div className="header-actions">
              <div className="auth-controls">
                <span className="user-info" title={userAccount?.username}>
                  👤 {userName}
                </span>
                <button className="dark-mode-toggle" onClick={toggleDarkMode} title={darkMode ? 'Light Mode' : 'Dark Mode'}>
                  {darkMode ? '☀️' : '🌙'}
                </button>
                <button className="logout-button" onClick={handleLogout} title="Sign out">
                  🚪 Logout
                </button>
              </div>
            </div>
          </div>
        </header>
      )}

      <div className="main-container">
        {/* Step Progress Indicator - Hidden for steps 1 and 3 */}
        {currentStep === 2 && (
          <div className="step-navigation">
            <WizardStepper steps={steps} currentStep={currentStep} />
          </div>
        )}

        <div className="wizard-content">
          {currentStep === 1 && (
            <TemplateSelectionNew
              templates={templates}
              selectedTemplate={selectedTemplate}
              onSelect={handleTemplateSelect}
              onDelete={handleTemplateDelete}
              onUpload={handleTemplateUpload}
              darkMode={darkMode}
              onBack={null}
            />
          )}

          {currentStep === 2 && (
            <ResumeUploadPhase
              selectedTemplate={selectedTemplate}
              templates={templates}
              onFormatSuccess={handleFormatSuccess}
              onBack={() => setCurrentStep(1)}
              isFormatting={isFormatting}
              setIsFormatting={setIsFormatting}
            />
          )}

          {currentStep === 3 && (
            <DownloadPhase
              results={results}
              onBack={() => setCurrentStep(2)}
              onStartOver={handleStartOver}
              darkMode={darkMode}
              toggleDarkMode={toggleDarkMode}
            />
          )}
        </div>
      </div>

      {currentStep !== 3 && (
        <footer className="footer">
          <p>© 2025 Resume Formatter Pro • Powered by TECHGENE</p>
        </footer>
      )}
    </div>
  );
}

export default App;
