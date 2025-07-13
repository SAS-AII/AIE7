import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface SettingsContextType {
  openaiKey: string;
  langsmithKey: string;
  tavilyKey: string;
  qdrantKey: string;
  qdrantUrl: string;
  darkMode: boolean;
  setOpenaiKey: (key: string) => void;
  setLangsmithKey: (key: string) => void;
  setTavilyKey: (key: string) => void;
  setQdrantKey: (key: string) => void;
  setQdrantUrl: (url: string) => void;
  setDarkMode: (enabled: boolean) => void;
  clearAllKeys: () => void;
  hasRequiredKeys: () => boolean;
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

interface SettingsProviderProps {
  children: ReactNode;
}

export const SettingsProvider: React.FC<SettingsProviderProps> = ({ children }) => {
  const [openaiKey, setOpenaiKeyState] = useState<string>('');
  const [langsmithKey, setLangsmithKeyState] = useState<string>('');
  const [tavilyKey, setTavilyKeyState] = useState<string>('');
  const [qdrantKey, setQdrantKeyState] = useState<string>('');
  const [qdrantUrl, setQdrantUrlState] = useState<string>('');
  const [darkMode, setDarkModeState] = useState<boolean>(false);
  const [isLoaded, setIsLoaded] = useState<boolean>(false);

  // Load settings from localStorage on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedOpenaiKey = localStorage.getItem('openaiKey') || '';
      const savedLangsmithKey = localStorage.getItem('langsmithKey') || '';
      const savedTavilyKey = localStorage.getItem('tavilyKey') || '';
      const savedQdrantKey = localStorage.getItem('qdrantKey') || '';
      const savedQdrantUrl = localStorage.getItem('qdrantUrl') || '';
      const savedDarkMode = localStorage.getItem('darkMode') === 'true';

      setOpenaiKeyState(savedOpenaiKey);
      setLangsmithKeyState(savedLangsmithKey);
      setTavilyKeyState(savedTavilyKey);
      setQdrantKeyState(savedQdrantKey);
      setQdrantUrlState(savedQdrantUrl);
      setDarkModeState(savedDarkMode);
      setIsLoaded(true);

      // Apply dark mode class to document
      if (savedDarkMode) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    }
  }, []);

  const setOpenaiKey = (key: string) => {
    setOpenaiKeyState(key);
    if (typeof window !== 'undefined') {
      localStorage.setItem('openaiKey', key);
    }
  };

  const setLangsmithKey = (key: string) => {
    setLangsmithKeyState(key);
    if (typeof window !== 'undefined') {
      localStorage.setItem('langsmithKey', key);
    }
  };

  const setTavilyKey = (key: string) => {
    setTavilyKeyState(key);
    if (typeof window !== 'undefined') {
      localStorage.setItem('tavilyKey', key);
    }
  };

  const setQdrantKey = (key: string) => {
    setQdrantKeyState(key);
    if (typeof window !== 'undefined') {
      localStorage.setItem('qdrantKey', key);
    }
  };

  const setQdrantUrl = (url: string) => {
    setQdrantUrlState(url);
    if (typeof window !== 'undefined') {
      localStorage.setItem('qdrantUrl', url);
    }
  };

  const setDarkMode = (enabled: boolean) => {
    setDarkModeState(enabled);
    if (typeof window !== 'undefined') {
      localStorage.setItem('darkMode', enabled.toString());
      if (enabled) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    }
  };

  const clearAllKeys = () => {
    setOpenaiKeyState('');
    setLangsmithKeyState('');
    setTavilyKeyState('');
    setQdrantKeyState('');
    setQdrantUrlState('');
    
    if (typeof window !== 'undefined') {
      localStorage.removeItem('openaiKey');
      localStorage.removeItem('langsmithKey');
      localStorage.removeItem('tavilyKey');
      localStorage.removeItem('qdrantKey');
      localStorage.removeItem('qdrantUrl');
    }
  };

  const hasRequiredKeys = () => {
    return openaiKey.trim() !== '' && tavilyKey.trim() !== '';
  };

  // Don't render until settings are loaded from localStorage
  if (!isLoaded) {
    return null;
  }

  const value: SettingsContextType = {
    openaiKey,
    langsmithKey,
    tavilyKey,
    qdrantKey,
    qdrantUrl,
    darkMode,
    setOpenaiKey,
    setLangsmithKey,
    setTavilyKey,
    setQdrantKey,
    setQdrantUrl,
    setDarkMode,
    clearAllKeys,
    hasRequiredKeys,
  };

  return (
    <SettingsContext.Provider value={value}>
      {children}
    </SettingsContext.Provider>
  );
};

export const useSettings = (): SettingsContextType => {
  const context = useContext(SettingsContext);
  if (context === undefined) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};

export default SettingsContext; 