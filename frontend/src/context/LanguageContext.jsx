import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import en from "../locales/en.json";
import kn from "../locales/kn.json";
import hi from "../locales/hi.json";
import ta from "../locales/ta.json";
import te from "../locales/te.json";
import ml from "../locales/ml.json";

export const SUPPORTED_LANGUAGES = [
  {
    code: "en",
    name: "English",
    nativeName: "English",
    flag: "🇬🇧",
    locale: "en-IN",
    voiceLang: "en-IN",
  },
  {
    code: "kn",
    name: "Kannada",
    nativeName: "ಕನ್ನಡ",
    flag: "🇮🇳",
    locale: "kn-IN",
    voiceLang: "kn-IN",
  },
  {
    code: "hi",
    name: "Hindi",
    nativeName: "हिन्दी",
    flag: "🇮🇳",
    locale: "hi-IN",
    voiceLang: "hi-IN",
  },
  {
    code: "ta",
    name: "Tamil",
    nativeName: "தமிழ்",
    flag: "🇮🇳",
    locale: "ta-IN",
    voiceLang: "ta-IN",
  },
  {
    code: "te",
    name: "Telugu",
    nativeName: "తెలుగు",
    flag: "🇮🇳",
    locale: "te-IN",
    voiceLang: "te-IN",
  },
  {
    code: "ml",
    name: "Malayalam",
    nativeName: "മലയാളം",
    flag: "🇮🇳",
    locale: "ml-IN",
    voiceLang: "ml-IN",
  },
];

const TRANSLATIONS = { en, kn, hi, ta, te, ml };

const LanguageContext = createContext(null);

export function LanguageProvider({ children }) {
  const [currentLanguage, setCurrentLanguage] = useState(() => {
    try {
      const saved = localStorage.getItem("diasense_language");
      if (saved && TRANSLATIONS[saved]) {
        return saved;
      }
    } catch (e) {}
    return "en";
  });

  // Sync html lang and body dataset attribute
  useEffect(() => {
    document.documentElement.lang = currentLanguage;
    if (document.body) {
      document.body.dataset.lang = currentLanguage;
    }
    try {
      localStorage.setItem("diasense_language", currentLanguage);
    } catch (e) {}
  }, [currentLanguage]);

  const changeLanguage = useCallback((code) => {
    if (TRANSLATIONS[code]) {
      setCurrentLanguage(code);
      try {
        localStorage.setItem("diasense_language", code);
      } catch (e) {}
    }
  }, []);

  const currentLangConfig = SUPPORTED_LANGUAGES.find(
    (l) => l.code === currentLanguage
  ) || SUPPORTED_LANGUAGES[0];

  /**
   * Translates a dot-notated key (e.g. "dashboard.heroTitle")
   * with automatic fallback to English and string interpolation support.
   */
  const t = useCallback(
    (key, params = {}) => {
      if (!key) return "";

      const keys = key.split(".");
      
      // Helper function to resolve nested keys
      const getNested = (obj, pathArray) => {
        let curr = obj;
        for (const k of pathArray) {
          if (curr && typeof curr === "object" && k in curr) {
            curr = curr[k];
          } else {
            return undefined;
          }
        }
        return curr;
      };

      // Try current language first
      let value = getNested(TRANSLATIONS[currentLanguage], keys);

      // Fallback to English if key missing in selected language
      if (value === undefined && currentLanguage !== "en") {
        value = getNested(TRANSLATIONS["en"], keys);
      }

      // If still missing, return the raw key
      if (value === undefined) {
        return key;
      }

      // If not a string (e.g. array or object), return directly
      if (typeof value !== "string") {
        return value;
      }

      // Replace variables in format {name} or {count}
      let interpolated = value;
      if (params && typeof params === "object") {
        Object.entries(params).forEach(([paramKey, paramVal]) => {
          interpolated = interpolated.replace(
            new RegExp(`\\{${paramKey}\\}`, "g"),
            String(paramVal)
          );
        });
      }

      return interpolated;
    },
    [currentLanguage]
  );

  const value = {
    currentLanguage,
    changeLanguage,
    languages: SUPPORTED_LANGUAGES,
    currentLangConfig,
    t,
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useTranslation() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useTranslation must be used within a LanguageProvider");
  }
  return context;
}

export default LanguageContext;
