import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import API_URL from './config';
import './LibraryView.css';
import EditBookModal from './EditBookModal'; // Importar el modal

// Hook personalizado para debounce
const useDebounce = (value, delay) => {
  const [debouncedValue, setDebouncedValue] = useState(value);
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);
    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);
  return debouncedValue;
};

// Componente para la portada (con fallback a genérica)
const BookCover = ({ src, alt, title }) => {
  const [hasError, setHasError] = useState(false);
  useEffect(() => { setHasError(false); }, [src]);
  const handleError = () => { setHasError(true); };

  if (hasError || !src) {
    const initial = title ? title[0].toUpperCase() : '?';
    return (
      <div className="generic-cover">
        <span className="generic-cover-initial">{initial}</span>
      </div>
    );
  }
  return <img src={src} alt={alt} className="book-cover" onError={handleError} />;
};

function LibraryView() {
  const [books, setBooks] = useState([]);
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearchTerm = useDebounce(searchTerm, 300);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [isMobile, setIsMobile] = useState(false);
  const [editingBook, setEditingBook] = useState(null);
  const [convertingId, setConvertingId] = useState(null); // Estado para el libro en conversión

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleAuthorClick = (author) => {
    setSearchTerm('');
    setSearchParams({ author: author });
  };

  const handleCategoryClick = (category) => {
    setSearchParams({ category: category });
  };

  const fetchBooks = useCallback(async () => {
    setLoading(true);
    setError('');
    const params = new URLSearchParams();
    const category = searchParams.get('category');
    const author = searchParams.get('author');

    if (category) params.append('category', category);
    if (author) {
      params.append('author', author);
    } else if (debouncedSearchTerm) {
      params.append('search', debouncedSearchTerm);
    }

    const url = `${API_URL}/books/?${params.toString()}`;

    try {
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        setBooks(data);
      } else {
        setError('No se pudieron cargar los libros.');
      }
    } catch (err) {
      setError('Error de conexión al cargar la biblioteca.');
    } finally {
      setLoading(false);
    }
  }, [debouncedSearchTerm, searchParams]);

  useEffect(() => {
    fetchBooks();
  }, [fetchBooks]);

  const handleDeleteBook = async (bookId) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este libro?')) {
      try {
        const response = await fetch(`${API_URL}/books/${bookId}`, { method: 'DELETE' });
        if (response.ok) {
          setBooks(prevBooks => prevBooks.filter(b => b.id !== bookId));
        } else {
          alert('No se pudo eliminar el libro.');
        }
      } catch (err) {
        alert('Error de conexión al intentar eliminar el libro.');
      }
    }
  };

  const handleConvertToPdf = async (bookId) => {
    if (window.confirm('¿Quieres convertir este EPUB a PDF? Esta acción añadirá un nuevo libro a tu biblioteca.')) {
      setConvertingId(bookId);
      try {
        const response = await fetch(`${API_URL}/api/books/${bookId}/convert`, { method: 'POST' });
        if (response.ok) {
          const newBook = await response.json();
          setBooks(prevBooks => [...prevBooks, newBook].sort((a, b) => b.id - a.id)); // Añadir y ordenar
          alert(`'${newBook.title}' se ha convertido a PDF y añadido a la biblioteca.`);
        } else {
          const errData = await response.json();
          alert(`Error al convertir el libro: ${errData.detail || 'Error desconocido'}`);
        }
      } catch (err) {
        alert('Error de conexión al intentar convertir el libro.');
      } finally {
        setConvertingId(null);
      }
    }
  };

  const handleEditClick = (book) => {
    setEditingBook(book);
  };

  const handleCloseModal = () => {
    setEditingBook(null);
  };

  const handleBookUpdated = (updatedBook) => {
    setBooks(prevBooks => 
      prevBooks.map(b => b.id === updatedBook.id ? updatedBook : b)
    );
  };

  return (
    <div className="library-container">
      <h2>Mi Biblioteca</h2>

      <div className="controls-container">
        <input
          type="text"
          placeholder="Buscar por título, autor o categoría..."
          className="search-bar"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {error && <p className="error-message">{error}</p>}
      {loading && <p>Cargando libros...</p>}
      {!loading && books.length === 0 && !error && <p>No se encontraron libros que coincidan con tu búsqueda.</p>}

      <div className="book-grid">
        {books.map((book) => {
          // Lógica para decidir si el botón de conversión debe mostrarse
          const isEpub = book.file_path.toLowerCase().endsWith('.epub');
          let showConvertButton = false;
          if (isEpub) {
            console.log(`--- Debugging EPUB: ${book.title} ---`);
            const lastDotIndex = book.file_path.lastIndexOf('.');
            const basePath = (lastDotIndex === -1) ? book.file_path : book.file_path.substring(0, lastDotIndex);
            const expectedPdfPath = `${basePath}.pdf`;
            
            // NORMALIZACIÓN: Reemplazar \ por / para una comparación consistente
            const normalizedExpectedPath = expectedPdfPath.replace(/\\/g, '/').toLowerCase();
            console.log(`[EPUB] Expected Normalized Path: ${normalizedExpectedPath}`);

            const pdfVersionExists = books.some(b => {
                const normalizedBookPath = b.file_path.replace(/\\/g, '/').toLowerCase();
                if (normalizedBookPath.endsWith('.pdf')) {
                    console.log(`[PDF Check] Comparing: ${normalizedBookPath} WITH ${normalizedExpectedPath}`);
                    if (normalizedBookPath === normalizedExpectedPath) {
                        console.log(`[PDF Check] Found a match! Hiding button.`);
                        return true;
                    }
                }
                return false;
            });
            
            showConvertButton = !pdfVersionExists;
            console.log(`>>> Show Convert Button for ${book.title}? ${showConvertButton}`);
            console.log(`------------------------------------`);
          }

          return (
            <div key={book.id} className="book-card">
              <div className="book-card-buttons">
                {showConvertButton && (
                  <button 
                    onClick={() => handleConvertToPdf(book.id)} 
                    className="convert-book-btn" 
                    title="Convertir a PDF"
                    disabled={convertingId === book.id}
                  >
                    {convertingId === book.id ? '...' : 'PDF'}
                  </button>
                )}
                <button onClick={() => handleEditClick(book)} className="edit-book-btn" title="Editar libro">✎</button>
                <button onClick={() => handleDeleteBook(book.id)} className="delete-book-btn" title="Eliminar libro">×</button>
              </div>
              <BookCover
                src={book.cover_image_url ? `${API_URL}/${book.cover_image_url}` : ''}
                alt={`Portada de ${book.title}`}
                title={book.title}
              />
              <div className="book-card-info">
                <h3>{book.title}</h3>
                <p className="clickable-text" onClick={() => handleAuthorClick(book.author)}>{book.author}</p>
                <span className="clickable-text" onClick={() => handleCategoryClick(book.category)}>{book.category}</span>
              </div>
              {book.file_path.toLowerCase().endsWith('.pdf') ? (
                <>
                  <a
                    href={`${API_URL}/books/download/${book.id}`}
                    className="download-button"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Abrir PDF
                  </a>
                  {isMobile && (
                    <a
                      href={`${API_URL}/books/download/${book.id}`}
                      className="download-button"
                      download // This attribute suggests download
                    >
                      Descargar PDF
                    </a>
                  )}
                </>
              ) : (
                <>
                  <Link to={`/leer/${book.id}`} className="download-button">
                    Leer EPUB
                  </Link>
                  {isMobile && (
                    <a
                      href={`${API_URL}/books/download/${book.id}`}
                      className="download-button"
                      download // This attribute suggests download
                    >
                      Descargar EPUB
                    </a>
                  )}
                </>
              )}
            </div>
          );
        })}
      </div>

      {editingBook && (
        <EditBookModal 
          book={editingBook} 
          onClose={handleCloseModal} 
          onBookUpdated={handleBookUpdated} 
        />
      )}

    </div>
  );
}

export default LibraryView;
