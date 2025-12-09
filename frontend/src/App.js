import React, { useState, useEffect } from 'react';
import { useMsal } from '@azure/msal-react';
import WizardStepper from './components/WizardStepper';
import TemplateSelection from './components/TemplateSelection';
import ResumeUploadPhase from './components/ResumeUploadPhase';
import DownloadPhase from './components/DownloadPhase';
import './App.css';

function App() {
  const { instance, accounts } = useMsal();
  const [currentStep, setCurrentStep] = useState(() => {
    const saved = localStorage.getItem('currentStep');
    return saved ? parseInt(saved) : 1;
  });
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(() => {
    const saved = localStorage.getItem('selectedTemplate');
    return saved ? saved : null;
  });
  const [results, setResults] = useState(() => {
    const saved = localStorage.getItem('results');
    return saved ? JSON.parse(saved) : [];
  });
  const [isFormatting, setIsFormatting] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  // Load dark mode from localStorage
  useEffect(() => {
    const savedDarkMode = localStorage.getItem('darkMode');
    if (savedDarkMode) {
      setDarkMode(JSON.parse(savedDarkMode));
    }
  }, []);

  // Save state to localStorage
  useEffect(() => {
    localStorage.setItem('currentStep', currentStep.toString());
  }, [currentStep]);

  useEffect(() => {
    if (selectedTemplate) {
      localStorage.setItem('selectedTemplate', selectedTemplate);
    }
  }, [selectedTemplate]);

  useEffect(() => {
    if (results.length > 0) {
      localStorage.setItem('results', JSON.stringify(results));
    }
  }, [results]);

  // Handle browser back/forward navigation
  useEffect(() => {
    const handlePopState = (event) => {
      if (event.state && event.state.step) {
        setCurrentStep(event.state.step);
      }
    };

    // Push initial state
    window.history.replaceState({ step: currentStep }, '', window.location.href);

    // Listen for back/forward
    window.addEventListener('popstate', handlePopState);

    return () => {
      window.removeEventListener('popstate', handlePopState);
    };
  }, []);

  // Update history when step changes
  useEffect(() => {
    window.history.pushState({ step: currentStep }, '', window.location.href);
  }, [currentStep]);

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
      const response = await fetch('http://localhost:5000/api/templates');
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
    if (window.confirm('Are you sure you want to delete this template?')) {
      try {
        await fetch(`http://localhost:5000/api/templates/${templateId}`, {
          method: 'DELETE'
        });
        fetchTemplates();
        if (selectedTemplate === templateId) {
          setSelectedTemplate(null);
        }
      } catch (error) {
        alert('Error deleting template');
      }
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
            <div className="logo">
              <span className="logo-icon">✨</span>
              <h1>Resume Formatter Pro</h1>
            </div>
            <div className="header-actions">
              <p className="tagline">Transform Your Resumes with Professional Templates</p>
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
        {/* Navigation Arrows */}
        <div className="step-navigation">
          <button 
            className="nav-arrow nav-arrow-left"
            onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
            disabled={currentStep === 1}
            title="Previous Step"
          >
            <span className="arrow-icon">←</span>
            <span className="arrow-label">Back</span>
          </button>
          
          {currentStep !== 3 && (
            <WizardStepper steps={steps} currentStep={currentStep} />
          )}
          
          <button 
            className="nav-arrow nav-arrow-right"
            onClick={() => setCurrentStep(Math.min(3, currentStep + 1))}
            disabled={currentStep === 3 || (currentStep === 1 && !selectedTemplate) || (currentStep === 2 && results.length === 0)}
            title="Next Step"
          >
            <span className="arrow-label">Next</span>
            <span className="arrow-icon">→</span>
          </button>
        </div>

        <div className="wizard-content">
          {currentStep === 1 && (
            <TemplateSelection
              templates={templates}
              selectedTemplate={selectedTemplate}
              onSelect={handleTemplateSelect}
              onDelete={handleTemplateDelete}
              onUpload={handleTemplateUpload}
              darkMode={darkMode}
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
              onStartOver={handleStartOver}
              darkMode={darkMode}
              toggleDarkMode={toggleDarkMode}
            />
          )}
        </div>
      </div>

      {currentStep !== 3 && (
        <footer className="footer">
          <p>© 2025 Resume Formatter Pro • Powered by AI</p>
        </footer>
      )}
    </div>
  );
}

export default App;
