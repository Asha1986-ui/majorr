import "./LanguageSelector.css";
import React, { useState, useRef, useEffect } from "react";
import { FaGlobe, FaChevronDown, FaCheck } from "react-icons/fa";
import { useTranslation } from "../../context/LanguageContext";

function LanguageSelector({ isCompact = false }) {
  const { currentLanguage, changeLanguage, languages, currentLangConfig } =
    useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target)
      ) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const handleSelect = (code) => {
    changeLanguage(code);
    setIsOpen(false);
  };

  return (
    <div
      className={`language-selector-wrapper ${isCompact ? "compact" : ""}`}
      ref={dropdownRef}
    >
      <button
        type="button"
        className={`lang-select-btn ${isOpen ? "active" : ""}`}
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Change Application Language"
        title="Change Language / ಭಾಷೆಯನ್ನು ಬದಲಾಯಿಸಿ"
      >
        <span className="lang-globe-icon">
          <FaGlobe />
        </span>
        <span className="lang-current-flag">{currentLangConfig.flag}</span>
        <span className="lang-current-name">
          {currentLangConfig.nativeName}
        </span>
        <FaChevronDown className={`lang-chevron ${isOpen ? "rotate" : ""}`} />
      </button>

      {isOpen && (
        <div className="lang-dropdown-menu">
          <div className="lang-dropdown-header">
            <span>🌐 Select Language</span>
          </div>
          <div className="lang-options-list">
            {languages.map((lang) => (
              <button
                key={lang.code}
                type="button"
                className={`lang-option-item ${
                  currentLanguage === lang.code ? "selected" : ""
                }`}
                onClick={() => handleSelect(lang.code)}
              >
                <span className="lang-option-flag">{lang.flag}</span>
                <div className="lang-option-labels">
                  <span className="lang-native-name">{lang.nativeName}</span>
                  <span className="lang-eng-name">{lang.name}</span>
                </div>
                {currentLanguage === lang.code && (
                  <FaCheck className="lang-check-icon" />
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default LanguageSelector;
