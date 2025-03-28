import React from 'react';
import { useTheme } from '../context/ThemeContext';
import { FaSun, FaMoon } from 'react-icons/fa';

const ThemeToggle = () => {
  const { isDarkMode, toggleTheme } = useTheme();

  const handleToggle = () => {
    console.log('Theme toggle clicked, current mode:', isDarkMode);
    toggleTheme();
  };

  return (
    <button
      onClick={handleToggle}
      className="theme-toggle-button"
      aria-label={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
      title={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
      style={{
        border: '2px solid var(--accent)',
        padding: '8px',
        borderRadius: '50%',
        backgroundColor: isDarkMode ? 'var(--background-tertiary)' : 'var(--background-secondary)'
      }}
    >
      {isDarkMode ? (
        <FaSun className="theme-icon sun-icon" />
      ) : (
        <FaMoon className="theme-icon moon-icon" />
      )}
    </button>
  );
};

export default ThemeToggle; 