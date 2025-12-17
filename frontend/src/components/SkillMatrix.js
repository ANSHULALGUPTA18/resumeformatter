import React, { useState, useEffect } from 'react';
import './SkillMatrix.css';

const SkillMatrix = ({ skillCategories, onSkillsChange }) => {
  const [selectedSkills, setSelectedSkills] = useState({});
  const [skillLevels, setSkillLevels] = useState({});

  // Initialize skills with default values
  useEffect(() => {
    if (skillCategories && skillCategories.length > 0) {
      const initialSkills = {};
      const initialLevels = {};
      skillCategories.forEach(skill => {
        initialSkills[skill] = true; // All skills selected by default
        initialLevels[skill] = 3; // Default to "Intermediate" level (1-5 scale)
      });
      setSelectedSkills(initialSkills);
      setSkillLevels(initialLevels);
    }
  }, [skillCategories]);

  // Notify parent of changes
  useEffect(() => {
    const skills = Object.keys(selectedSkills)
      .filter(skill => selectedSkills[skill])
      .map(skill => ({
        name: skill,
        level: skillLevels[skill] || 3
      }));
    onSkillsChange(skills);
  }, [selectedSkills, skillLevels, onSkillsChange]);

  const toggleSkill = (skill) => {
    setSelectedSkills(prev => ({
      ...prev,
      [skill]: !prev[skill]
    }));
  };

  const updateSkillLevel = (skill, level) => {
    setSkillLevels(prev => ({
      ...prev,
      [skill]: level
    }));
  };

  const getLevelLabel = (level) => {
    const labels = {
      1: 'Beginner',
      2: 'Basic',
      3: 'Intermediate',
      4: 'Advanced',
      5: 'Expert'
    };
    return labels[level] || 'Intermediate';
  };

  if (!skillCategories || skillCategories.length === 0) {
    return null;
  }

  return (
    <div className="skill-matrix-container">
      <div className="skill-matrix-header">
        <i className="fas fa-chart-bar"></i>
        <h3>Skill Matrix</h3>
        <span className="skill-count">{Object.values(selectedSkills).filter(Boolean).length} selected</span>
      </div>

      <div className="skill-matrix-grid">
        {skillCategories.map((skill, index) => (
          <div
            key={index}
            className={`skill-item ${selectedSkills[skill] ? 'selected' : ''}`}
          >
            <div className="skill-checkbox-wrapper">
              <input
                type="checkbox"
                id={`skill-${index}`}
                checked={selectedSkills[skill] || false}
                onChange={() => toggleSkill(skill)}
                className="skill-checkbox"
              />
              <label htmlFor={`skill-${index}`} className="skill-label">
                {skill}
              </label>
            </div>

            {selectedSkills[skill] && (
              <div className="skill-level-selector">
                <div className="level-dots">
                  {[1, 2, 3, 4, 5].map(level => (
                    <button
                      key={level}
                      className={`level-dot ${(skillLevels[skill] || 3) >= level ? 'active' : ''}`}
                      onClick={() => updateSkillLevel(skill, level)}
                      title={getLevelLabel(level)}
                      aria-label={`Set ${skill} to ${getLevelLabel(level)}`}
                    />
                  ))}
                </div>
                <span className="level-label">{getLevelLabel(skillLevels[skill] || 3)}</span>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="skill-matrix-footer">
        <button
          className="select-all-btn"
          onClick={() => {
            const allSelected = {};
            skillCategories.forEach(skill => {
              allSelected[skill] = true;
            });
            setSelectedSkills(allSelected);
          }}
        >
          Select All
        </button>
        <button
          className="deselect-all-btn"
          onClick={() => {
            const noneSelected = {};
            skillCategories.forEach(skill => {
              noneSelected[skill] = false;
            });
            setSelectedSkills(noneSelected);
          }}
        >
          Deselect All
        </button>
      </div>
    </div>
  );
};

export default SkillMatrix;
