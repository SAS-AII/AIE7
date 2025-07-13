import React, { useState, useEffect, useCallback } from 'react';
import { Dialog } from '@headlessui/react';
import { 
  XMarkIcon, 
  DocumentPlusIcon, 
  TrashIcon, 
  FolderOpenIcon,
  CloudArrowUpIcon,
  DocumentTextIcon,
  PhotoIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';
import { getApiUrl } from '@/utils/api';

interface KnowledgeFile {
  filename: string;
  content_type: string;
  total_chunks: number;
  file_hash: string;
  chunk_count: number;
  source: string;
}

interface KnowledgeModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const KnowledgeModal: React.FC<KnowledgeModalProps> = ({ isOpen, onClose }) => {
  const [files, setFiles] = useState<KnowledgeFile[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);

  // Load files when modal opens
  useEffect(() => {
    if (isOpen) {
      loadFiles();
    }
  }, [isOpen]);

  const loadFiles = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await fetch(getApiUrl('/knowledge/files'));
      if (response.ok) {
        const data = await response.json();
        setFiles(data.files || []);
      } else {
        toast.error('Failed to load knowledge files');
      }
    } catch (error) {
      console.error('Error loading files:', error);
      toast.error('Error loading knowledge files');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleFileSelect = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  }, []);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  }, []);

  const uploadFile = useCallback(async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch(getApiUrl('/knowledge/upload'), {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        if (result.exists) {
          // File already exists, ask user if they want to overwrite
          const shouldOverwrite = confirm(result.message + '\n\nDo you want to overwrite it?');
          if (shouldOverwrite) {
            await overwriteFile(selectedFile.name, selectedFile);
          }
        } else {
          toast.success(`Successfully uploaded ${selectedFile.name}`);
          setSelectedFile(null);
          await loadFiles();
        }
      } else {
        toast.error(result.detail || 'Failed to upload file');
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      toast.error('Error uploading file');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  }, [selectedFile, loadFiles]);

  const overwriteFile = useCallback(async (filename: string, file: File) => {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(getApiUrl(`/knowledge/files/${encodeURIComponent(filename)}/overwrite`), {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        toast.success(`Successfully overwritten ${filename}`);
        setSelectedFile(null);
        await loadFiles();
      } else {
        const result = await response.json();
        toast.error(result.detail || 'Failed to overwrite file');
      }
    } catch (error) {
      console.error('Error overwriting file:', error);
      toast.error('Error overwriting file');
    }
  }, [loadFiles]);

  const deleteFile = useCallback(async (filename: string) => {
    if (!confirm(`Are you sure you want to delete "${filename}"? This will remove all associated knowledge chunks.`)) {
      return;
    }

    try {
      const response = await fetch(getApiUrl(`/knowledge/files/${encodeURIComponent(filename)}`), {
        method: 'DELETE',
      });

      if (response.ok) {
        toast.success(`Successfully deleted ${filename}`);
        await loadFiles();
      } else {
        const result = await response.json();
        toast.error(result.detail || 'Failed to delete file');
      }
    } catch (error) {
      console.error('Error deleting file:', error);
      toast.error('Error deleting file');
    }
  }, [loadFiles]);

  const getFileIcon = (contentType: string) => {
    if (contentType.startsWith('image/')) {
      return <PhotoIcon className="w-5 h-5 text-green-500" />;
    } else if (contentType === 'application/pdf') {
      return <DocumentTextIcon className="w-5 h-5 text-red-500" />;
    } else {
      return <DocumentTextIcon className="w-5 h-5 text-blue-500" />;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Dialog 
      as="div" 
      className="relative z-50" 
      open={isOpen} 
      onClose={onClose}
    >
      <div className="fixed inset-0 bg-black bg-opacity-25" />
      
      <div className="fixed inset-0 overflow-y-auto">
        <div className="flex min-h-full items-center justify-center p-4 text-center">
          <Dialog.Panel className="w-full max-w-4xl transform overflow-hidden rounded-2xl bg-white dark:bg-gray-800 p-6 text-left align-middle shadow-xl transition-all">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-blue-600 rounded-lg flex items-center justify-center">
                  <FolderOpenIcon className="w-5 h-5 text-white" />
                </div>
                <div>
                  <Dialog.Title className="text-lg font-medium text-gray-900 dark:text-white">
                    Chess Knowledge Base
                  </Dialog.Title>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Manage your chess documents and knowledge files
                  </p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
              >
                <XMarkIcon className="w-6 h-6" />
              </button>
            </div>

            {/* Upload Section */}
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                Upload New Knowledge
              </h3>
              
              <div
                className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                  dragActive 
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                    : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                {selectedFile ? (
                  <div className="space-y-3">
                    <div className="flex items-center justify-center space-x-2">
                      {getFileIcon(selectedFile.type)}
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {selectedFile.name}
                      </span>
                      <span className="text-xs text-gray-500">
                        ({formatFileSize(selectedFile.size)})
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-center space-x-3">
                      <button
                        onClick={uploadFile}
                        disabled={isUploading}
                        className="px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white rounded-lg transition-colors"
                      >
                        {isUploading ? 'Uploading...' : 'Upload'}
                      </button>
                      <button
                        onClick={() => setSelectedFile(null)}
                        disabled={isUploading}
                        className="px-4 py-2 bg-gray-500 hover:bg-gray-600 disabled:bg-gray-300 text-white rounded-lg transition-colors"
                      >
                        Cancel
                      </button>
                    </div>

                    {isUploading && (
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${uploadProgress}%` }}
                        />
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="space-y-3">
                    <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Drop files here or{' '}
                        <label className="text-blue-500 hover:text-blue-600 cursor-pointer">
                          browse
                          <input
                            type="file"
                            className="hidden"
                            accept=".pdf,.txt,.png,.jpg,.jpeg,.gif"
                            onChange={handleFileSelect}
                          />
                        </label>
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Supports PDF, text files, and images
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Files List */}
            <div>
              <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                Uploaded Files ({files.length})
              </h3>
              
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                </div>
              ) : files.length === 0 ? (
                <div className="text-center py-8">
                  <FolderOpenIcon className="mx-auto h-12 w-12 text-gray-400 mb-3" />
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    No knowledge files uploaded yet
                  </p>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                    Upload chess documents to enhance the assistant's knowledge
                  </p>
                </div>
              ) : (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {files.map((file) => (
                    <div
                      key={file.filename}
                      className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                    >
                      <div className="flex items-center space-x-3">
                        {getFileIcon(file.content_type)}
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-white">
                            {file.filename}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {file.chunk_count} chunks • {file.content_type}
                          </p>
                        </div>
                      </div>
                      
                      <button
                        onClick={() => deleteFile(file.filename)}
                        className="p-2 text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-colors"
                        title="Delete file"
                      >
                        <TrashIcon className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Info Message */}
            <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <div className="flex items-start space-x-3">
                <ExclamationTriangleIcon className="w-5 h-5 text-blue-500 mt-0.5" />
                <div className="text-sm text-blue-700 dark:text-blue-300">
                  <p className="font-medium">Knowledge Base Information</p>
                  <p className="mt-1">
                    Files are processed and stored as vector embeddings in your knowledge base. 
                    The chess assistant will use this information to provide more accurate and detailed responses.
                  </p>
                </div>
              </div>
            </div>
          </Dialog.Panel>
        </div>
      </div>
    </Dialog>
  );
};

export default KnowledgeModal; 