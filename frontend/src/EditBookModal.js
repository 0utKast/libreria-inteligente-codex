import React, { useState, useEffect } from 'react';
import API_URL from './config';
import './EditBookModal.css';

function EditBookModal({ book, onClose, onBookUpdated }) {
  const [title, setTitle] = useState('');
  const [author, setAuthor] = useState('');
  const [coverImage, setCoverImage] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (book) {
      setTitle(book.title || '');
      setAuthor(book.author || '');
    }
  }, [book]);

  if (!book) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSaving(true);

    const formData = new FormData();
    formData.append('title', title);
    formData.append('author', author);
    if (coverImage) {
      formData.append('cover_image', coverImage);
    }

    try {
      const response = await fetch(`${API_URL}/books/${book.id}`, {
        method: 'PUT',
        body: formData,
      });

      if (response.ok) {
        const updatedBook = await response.json();
        onBookUpdated(updatedBook);
        onClose();
      } else {
        alert('Error al actualizar el libro.');
      }
    } catch (error) {
      alert('Error de conexión al actualizar el libro.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Editar Libro</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="title">Título</label>
            <input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="author">Autor</label>
            <input
              id="author"
              type="text"
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="cover">Portada (opcional)</label>
            <input
              id="cover"
              type="file"
              accept="image/*"
              onChange={(e) => setCoverImage(e.target.files[0])}
            />
          </div>
          <div className="modal-actions">
            <button type="button" onClick={onClose} disabled={isSaving}>Cancelar</button>
            <button type="submit" disabled={isSaving}>
              {isSaving ? 'Guardando...' : 'Guardar Cambios'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default EditBookModal;
