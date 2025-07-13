import React, { useState, useEffect } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { 
  XMarkIcon, 
  CogIcon,
  KeyIcon,
  EyeIcon,
  EyeSlashIcon,
  TrashIcon,
  MoonIcon,
  SunIcon
} from '@heroicons/react/24/outline';
import { useSettings } from '@/contexts/SettingsContext';
import { toast } from 'react-hot-toast';
import clsx from 'clsx';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface PasswordFieldProps {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  required?: boolean;
}

const PasswordField: React.FC<PasswordFieldProps> = ({
  id,
  label,
  value,
  onChange,
  placeholder,
  required = false
}) => {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className="space-y-2">
      <label htmlFor={id} className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      <div className="relative">
        <input
          id={id}
          type={showPassword ? 'text' : 'password'}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="w-full px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-chess-accent focus:border-chess-accent"
        />
        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
          className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
        >
          {showPassword ? (
            <EyeSlashIcon className="w-5 h-5" />
          ) : (
            <EyeIcon className="w-5 h-5" />
          )}
        </button>
      </div>
    </div>
  );
};

const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose }) => {
  const {
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
  } = useSettings();

  const [localOpenaiKey, setLocalOpenaiKey] = useState(openaiKey);
  const [localLangsmithKey, setLocalLangsmithKey] = useState(langsmithKey);
  const [localTavilyKey, setLocalTavilyKey] = useState(tavilyKey);
  const [localQdrantKey, setLocalQdrantKey] = useState(qdrantKey);
  const [localQdrantUrl, setLocalQdrantUrl] = useState(qdrantUrl);
  const [localDarkMode, setLocalDarkMode] = useState(darkMode);

  // Update local state when settings change
  useEffect(() => {
    setLocalOpenaiKey(openaiKey);
    setLocalLangsmithKey(langsmithKey);
    setLocalTavilyKey(tavilyKey);
    setLocalQdrantKey(qdrantKey);
    setLocalQdrantUrl(qdrantUrl);
    setLocalDarkMode(darkMode);
  }, [openaiKey, langsmithKey, tavilyKey, qdrantKey, qdrantUrl, darkMode]);

  const handleSave = () => {
    setOpenaiKey(localOpenaiKey);
    setLangsmithKey(localLangsmithKey);
    setTavilyKey(localTavilyKey);
    setQdrantKey(localQdrantKey);
    setQdrantUrl(localQdrantUrl);
    setDarkMode(localDarkMode);
    
    toast.success('Settings saved successfully');
    onClose();
  };

  const handleReset = () => {
    setLocalOpenaiKey(openaiKey);
    setLocalLangsmithKey(langsmithKey);
    setLocalTavilyKey(tavilyKey);
    setLocalQdrantKey(qdrantKey);
    setLocalQdrantUrl(qdrantUrl);
    setLocalDarkMode(darkMode);
  };

  const handleClearAll = () => {
    if (confirm('Are you sure you want to clear all API keys? This action cannot be undone.')) {
      clearAllKeys();
      setLocalOpenaiKey('');
      setLocalLangsmithKey('');
      setLocalTavilyKey('');
      setLocalQdrantKey('');
      setLocalQdrantUrl('');
      toast.success('All API keys cleared');
    }
  };

  const hasChanges = 
    localOpenaiKey !== openaiKey ||
    localLangsmithKey !== langsmithKey ||
    localTavilyKey !== tavilyKey ||
    localQdrantKey !== qdrantKey ||
    localQdrantUrl !== qdrantUrl ||
    localDarkMode !== darkMode;

  return (
    <Transition appear show={isOpen} as={React.Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={React.Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/25 backdrop-blur-sm" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={React.Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white dark:bg-gray-800 p-6 shadow-xl transition-all">
                <div className="flex items-center justify-between mb-4">
                  <Dialog.Title as="h3" className="text-lg font-medium text-gray-900 dark:text-gray-100">
                    Settings
                  </Dialog.Title>
                  <button
                    onClick={onClose}
                    className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
                  >
                    <XMarkIcon className="w-6 h-6" />
                  </button>
                </div>

                <div className="space-y-4">
                  {/* Theme toggle */}
                  <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex items-center gap-2">
                      {localDarkMode ? (
                        <MoonIcon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                      ) : (
                        <SunIcon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                      )}
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Dark Mode
                      </span>
                    </div>
                    <button
                      onClick={() => setLocalDarkMode(!localDarkMode)}
                      className={clsx(
                        'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                        localDarkMode ? 'bg-chess-accent' : 'bg-gray-200 dark:bg-gray-600'
                      )}
                    >
                      <span
                        className={clsx(
                          'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                          localDarkMode ? 'translate-x-6' : 'translate-x-1'
                        )}
                      />
                    </button>
                  </div>

                  {/* API Keys section */}
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <KeyIcon className="w-5 h-5 text-chess-accent" />
                      <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        API Keys
                      </h4>
                    </div>

                    <PasswordField
                      id="openai-key"
                      label="OpenAI API Key"
                      value={localOpenaiKey}
                      onChange={setLocalOpenaiKey}
                      placeholder="sk-..."
                      required
                    />

                    <PasswordField
                      id="tavily-key"
                      label="Tavily API Key"
                      value={localTavilyKey}
                      onChange={setLocalTavilyKey}
                      placeholder="tvly-..."
                      required
                    />

                    <PasswordField
                      id="langsmith-key"
                      label="LangSmith API Key (Optional)"
                      value={localLangsmithKey}
                      onChange={setLocalLangsmithKey}
                      placeholder="ls__..."
                    />

                    <PasswordField
                      id="qdrant-key"
                      label="Qdrant API Key (Optional)"
                      value={localQdrantKey}
                      onChange={setLocalQdrantKey}
                      placeholder="qdrant-..."
                    />

                    <div className="space-y-2">
                      <label htmlFor="qdrant-url" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Qdrant URL (Optional)
                      </label>
                      <input
                        id="qdrant-url"
                        type="url"
                        value={localQdrantUrl}
                        onChange={(e) => setLocalQdrantUrl(e.target.value)}
                        placeholder="https://your-cluster.qdrant.io"
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-chess-accent focus:border-chess-accent"
                      />
                    </div>
                  </div>

                  {/* Status indicator */}
                  <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex items-center gap-2">
                      <div className={clsx(
                        'w-2 h-2 rounded-full',
                        hasRequiredKeys() ? 'bg-green-500' : 'bg-red-500'
                      )} />
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {hasRequiredKeys() ? 'Ready to use' : 'Missing required keys'}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      Required: OpenAI API Key, Tavily API Key
                    </p>
                  </div>

                  {/* Action buttons */}
                  <div className="flex justify-between gap-2 pt-4">
                    <button
                      onClick={handleClearAll}
                      className="flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 transition-colors"
                    >
                      <TrashIcon className="w-4 h-4" />
                      Clear All
                    </button>
                    
                    <div className="flex gap-2">
                      <button
                        onClick={handleReset}
                        disabled={!hasChanges}
                        className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Reset
                      </button>
                      <button
                        onClick={handleSave}
                        disabled={!hasChanges}
                        className="px-4 py-2 text-sm font-medium text-white bg-chess-accent hover:bg-chess-accent/90 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Save
                      </button>
                    </div>
                  </div>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
};

export default SettingsModal; 