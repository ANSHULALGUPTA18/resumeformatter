import React from 'react';
import './WizardStepper.css';

const WizardStepper = ({ steps, currentStep }) => {
  return (
    <div className="wizard-stepper">
      {steps.map((step, index) => (
        <React.Fragment key={step.number}>
          <div className={`step ${currentStep === step.number ? 'active' : ''} ${currentStep > step.number ? 'completed' : ''}`}>
            <div className="step-circle">
              {currentStep > step.number ? (
                <span className="checkmark">✓</span>
              ) : (
                <span className="step-icon">{step.icon}</span>
              )}
            </div>
            <div className="step-label">
              <span className="step-number">Step {step.number}</span>
              <span className="step-title">{step.title}</span>
            </div>
          </div>
          {index < steps.length - 1 && (
            <div className={`step-connector ${currentStep > step.number ? 'completed' : ''}`}></div>
          )}
        </React.Fragment>
      ))}
    </div>
  );
};

export default WizardStepper;
