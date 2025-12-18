import React, { useState, useRef, useEffect } from 'react';
import { HiOutlineArrowRightOnRectangle } from 'react-icons/hi2';
import './UserProfileDropdown.css';

function UserProfileDropdown({ userAccount, onLogout, profilePhoto }) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  // Extract user initials from name
  const getInitials = (name) => {
    if (!name) return 'U';
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const userName = userAccount?.name || userAccount?.username || 'User';
  const userEmail = userAccount?.username || 'email@example.com';
  const initials = getInitials(userName);

  return (
    <div className="user-profile-dropdown" ref={dropdownRef}>
      {/* Avatar Button */}
      <button
        className="avatar-button"
        onClick={() => setIsOpen(!isOpen)}
        title="User Profile"
        aria-label="Open user profile menu"
        aria-expanded={isOpen}
      >
        <div className="avatar-circle">
          {profilePhoto ? (
            <img src={profilePhoto} alt={userName} className="avatar-image" />
          ) : (
            <span className="avatar-initials">{initials}</span>
          )}
        </div>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="dropdown-menu">
          {/* Profile Header */}
          <div className="profile-header">
            <div className="profile-avatar-large">
              {profilePhoto ? (
                <img src={profilePhoto} alt={userName} className="avatar-image-large" />
              ) : (
                <span className="avatar-initials-large">{initials}</span>
              )}
            </div>
            <div className="profile-info">
              <div className="profile-name">{userName}</div>
              <div className="profile-email" title={userEmail}>{userEmail}</div>
            </div>
          </div>

          {/* Divider */}
          <div className="dropdown-divider"></div>

          {/* Logout Button */}
          <button
            className="logout-menu-button"
            onClick={() => {
              onLogout();
              setIsOpen(false);
            }}
          >
            <HiOutlineArrowRightOnRectangle className="logout-icon" />
            <span>Sign Out</span>
          </button>
        </div>
      )}
    </div>
  );
}

export default UserProfileDropdown;
