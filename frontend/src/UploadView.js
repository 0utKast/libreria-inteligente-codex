import React, { useState, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import API_URL from './config';
import './UploadView.css';

function UploadView() {
  const [filesToUpload, setFilesToUpload] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const navigate = useNavigate();
  const fileInputRef = useRef(null); // Ref para el input de archivo

  const handleFileChange = (event) => {
    const selectedFiles = Array.from(event.target.files);
    const newFiles = selectedFiles.map(file => ({
      file,
      status: 'pending',
      message: ''
    }));
    setFilesToUpload(prevFiles => [...prevFiles, ...newFiles]);
  };

  const handleDrop = useCallback((event) => {
    event.preventDefault();
    event.stopPropagation();
    if (event.dataTransfer.files && event.dataTransfer.files.length > 0) {
      const selectedFiles = Array.from(event.dataTransfer.files);
      const newFiles = selectedFiles.map(file => ({
        file,
        status: 'pending',
        message: ''
      }));
      setFilesToUpload(prevFiles => [...prevFiles, ...newFiles]);
      event.dataTransfer.clearData();
    }
  }, []);

  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();
  };

  const updateFileStatus = (index, status, message) => {
    setFilesToUpload(prevFiles => {
      const updatedFiles = [...prevFiles];
      updatedFiles[index] = { ...updatedFiles[index], status, message };
      return updatedFiles;
    });
  };

  const handleUpload = async () => {
    if (filesToUpload.length === 0) return;

    setIsUploading(true);

    for (let i = 0; i < filesToUpload.length; i++) {
      if (filesToUpload[i].status !== 'pending') continue;

      updateFileStatus(i, 'uploading', 'Subiendo y analizando...');
      const formData = new FormData();
      formData.append('book_file', filesToUpload[i].file);

      try {
        const response = await fetch(`${API_URL}/upload-book/`, {
          method: 'POST',
          body: formData,
        });
        const result = await response.json();
        if (response.ok) {
          updateFileStatus(i, 'success', `'${result.title}' añadido correctamente.`);
        } else {
          updateFileStatus(i, 'error', `Error: ${result.detail || 'No se pudo procesar'}`);
        }
      } catch (error) {
        updateFileStatus(i, 'error', 'Error de conexión con el servidor.');
      }
    }
    setIsUploading(false);
  };

  const handleReset = () => {
    setFilesToUpload([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };
  
  const allDone = !isUploading && filesToUpload.length > 0 && filesToUpload.every(f => f.status === 'success' || f.status === 'error');

  return (
    <div className="upload-view-container" onDrop={handleDrop} onDragOver={handleDragOver}>
      <h2>Añadir Nuevos Libros</h2>
      <p>Sube uno o varios libros (PDF o EPUB) para que la IA los analice.</p>
      <div className="upload-container">
        <div className="drop-zone">
          <p>Arrastra y suelta archivos aquí, o usa el botón</p>
          <input 
            type="file" 
            id="file-input" 
            ref={fileInputRef} // Añadir la ref
            onChange={handleFileChange} 
            accept=".pdf,.epub" 
            multiple 
          />
          <label htmlFor="file-input" className="file-label">Seleccionar Archivos</label>
        </div>

        {filesToUpload.length > 0 && (
          <div className="file-list">
            {filesToUpload.map((fileObj, index) => (
              <div key={index} className={`file-item ${fileObj.status}`}>
                <span className="file-name">{fileObj.file.name}</span>
                <span className="file-status">{fileObj.message}</span>
              </div>
            ))}
          </div>
        )}

        {!allDone && (
          <button 
            onClick={handleUpload} 
            className="upload-button" 
            disabled={isUploading || filesToUpload.filter(f => f.status === 'pending').length === 0}
          >
            {isUploading ? 'Procesando...' : `Subir ${filesToUpload.filter(f => f.status === 'pending').length} Archivo(s)`}
          </button>
        )}

        {allDone && (
          <div className="completion-actions">
            <button onClick={() => navigate('/')} className="library-button">
              Ir a la Biblioteca
            </button>
            <button onClick={handleReset} className="reset-button">
              Añadir más libros
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default UploadView;