import React, { useState, useRef, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import { FaSun, FaMoon, FaDesktop, FaChevronDown } from 'react-icons/fa';

const ThemeSelector = () => {
  const { isDarkMode, setTheme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Get current theme preference
  const getCurrentTheme = () => {
    const savedTheme = localStorage.getItem('theme');
    if (!savedTheme) return 'system';
    return savedTheme;
  };

  const [currentTheme, setCurrentTheme] = useState(getCurrentTheme());

  // Handle theme selection
  const handleThemeChange = (theme) => {
    if (theme === 'system') {
      localStorage.removeItem('theme');
      const systemDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setTheme(systemDarkMode ? 'dark' : 'light');
    } else {
      setTheme(theme);
    }
    setCurrentTheme(theme);
    setIsOpen(false);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Theme options
  const themeOptions = [
    { id: 'light', name: 'Light', icon: <FaSun className="w-4 h-4 text-yellow-500" /> },
    { id: 'dark', name: 'Dark', icon: <FaMoon className="w-4 h-4 text-blue-400" /> },
    { id: 'system', name: 'System', icon: <FaDesktop className="w-4 h-4 text-gray-500 dark:text-gray-400" /> },
  ];

  // Get current theme option
  const currentThemeOption = themeOptions.find(option => option.id === currentTheme);

  return (
    <div className="fixed bottom-4 right-4 z-50" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-white dark:bg-gray-800 shadow-md border border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        <span className="flex items-center">
          {currentThemeOption?.icon}
          <span className="ml-2 font-medium">{currentThemeOption?.name}</span>
        </span>
        <FaChevronDown className={`w-3 h-3 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute right-0 bottom-12 w-48 py-2 mt-2 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700">
          {themeOptions.map((option) => (
            <button
              key={option.id}
              onClick={() => handleThemeChange(option.id)}
              className={`w-full flex items-center px-4 py-2 text-sm text-left hover:bg-gray-100 dark:hover:bg-gray-700 ${
                currentTheme === option.id ? 'bg-gray-100 dark:bg-gray-700' : ''
              }`}
            >
              {option.icon}
              <span className="ml-2">{option.name}</span>
              {currentTheme === option.id && (
                <span className="ml-auto">
                  <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default ThemeSelector; 