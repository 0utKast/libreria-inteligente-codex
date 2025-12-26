import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import API_URL from './config';
import './LibraryView.css';
import EditBookModal from './EditBookModal'; // Importar el modal

const PAGE_SIZE = 20;

const normalizePath = (path = '') => path.replace(/\\/g, '/').toLowerCase();

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
const BookCover = React.memo(({ src, alt, title }) => {
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
  return (
    <img
      src={src}
      alt={alt}
      className="book-cover"
      onError={handleError}
      loading="lazy"
      decoding="async"
    />
  );
});

const BookCard = React.memo(({ book, isMobile, handleAuthorClick, handleCategoryClick, handleDeleteBook, handleConvertToPdf, handleEditClick, convertingId, showConvertButton }) => {
  return (
    <div className="book-card">
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
});


function LibraryView() {
  const [books, setBooks] = useState([]);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearchTerm = useDebounce(searchTerm, 500);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [searchMode, setSearchMode] = useState('exact'); // 'exact' o 'semantic'
  const [ragStats, setRagStats] = useState({ total_documents: 0 });
  const [editingBook, setEditingBook] = useState(null);
  const [convertingId, setConvertingId] = useState(null);

  const observer = useRef();
  const isFetchingRef = useRef(false);

  const lastBookElementRef = useCallback(node => {
    if (observer.current) observer.current.disconnect();
    observer.current = new IntersectionObserver(entries => {
      const [entry] = entries;
      if (entry.isIntersecting && hasMore && !loading && !isFetchingRef.current) {
        isFetchingRef.current = true;
        setPage(prevPage => prevPage + 1);
      }
    });
    if (node) observer.current.observe(node);
  }, [hasMore, loading]);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleAuthorClick = useCallback((author) => {
    setSearchTerm('');
    setSearchParams({ author: author });
  }, [setSearchParams]);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${API_URL}/rag/stats`);
        if (response.ok) {
          const data = await response.json();
          setRagStats(data);
        }
      } catch (err) {
        console.error('Error fetching RAG stats:', err);
      }
    };
    fetchStats();
  }, [searchMode]);

  const handleCategoryClick = useCallback((category) => {
    setSearchParams({ category: category });
  }, [setSearchParams]);

  // Effect to reset list when search/filters change
  useEffect(() => {
    setBooks([]);
    setPage(0);
    setHasMore(true);
    isFetchingRef.current = false;
  }, [debouncedSearchTerm, searchParams, searchMode]);

  // Main effect for fetching books
  useEffect(() => {
    if (!hasMore) {
      return;
    }

    const params = new URLSearchParams();
    const category = searchParams.get('category');
    const author = searchParams.get('author');

    let url;
    if (searchMode === 'semantic' && debouncedSearchTerm) {
      params.append('q', debouncedSearchTerm);
      url = `${API_URL}/api/books/search/semantic?${params.toString()}`;
    } else {
      if (category) params.append('category', category);
      if (author) {
        params.append('author', author);
      } else if (debouncedSearchTerm) {
        params.append('search', debouncedSearchTerm);
      }
      params.append('skip', page * PAGE_SIZE);
      params.append('limit', PAGE_SIZE);
      url = `${API_URL}/books/?${params.toString()}`;
    }

    let cancelled = false;

    const fetchBooks = async () => {
      try {
        isFetchingRef.current = true;
        setLoading(true);
        setError('');
        const response = await fetch(url);
        if (response.ok) {
          const data = await response.json();
          if (!cancelled) {
            setBooks(prevBooks => page === 0 ? data : [...prevBooks, ...data]);
            setHasMore(searchMode === 'semantic' ? false : data.length === PAGE_SIZE);
          }
        } else if (!cancelled) {
          setError('No se pudieron cargar los libros.');
        }
      } catch (err) {
        if (!cancelled) {
          setError('Error de conexión al cargar la biblioteca.');
        }
      } finally {
        isFetchingRef.current = false;
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchBooks();

    return () => {
      cancelled = true;
    };

  }, [page, debouncedSearchTerm, searchParams, hasMore, searchMode]);


  const handleDeleteBook = useCallback(async (bookId) => {
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
  }, []);

  const handleConvertToPdf = useCallback(async (bookId) => {
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
  }, []);

  const handleEditClick = useCallback((book) => {
    setEditingBook(book);
  }, []);

  const handleCloseModal = useCallback(() => {
    setEditingBook(null);
  }, []);

  const handleBookUpdated = useCallback((updatedBook) => {
    setBooks(prevBooks =>
      prevBooks.map(b => b.id === updatedBook.id ? updatedBook : b)
    );
  }, []);

  const convertibilityMap = useMemo(() => {
    if (!books.length) {
      return new Map();
    }

    const normalizedPaths = new Set();
    books.forEach(({ file_path }) => {
      if (file_path) {
        normalizedPaths.add(normalizePath(file_path));
      }
    });

    const map = new Map();
    books.forEach((book) => {
      const rawPath = book.file_path || '';
      if (!rawPath.toLowerCase().endsWith('.epub')) {
        map.set(book.id, false);
        return;
      }
      const lastDotIndex = rawPath.lastIndexOf('.');
      const basePath = lastDotIndex === -1 ? rawPath : rawPath.substring(0, lastDotIndex);
      const expectedPdfPath = `${basePath}.pdf`;
      const normalizedExpectedPath = normalizePath(expectedPdfPath);
      map.set(book.id, !normalizedPaths.has(normalizedExpectedPath));
    });

    return map;
  }, [books]);

  const handleReindex = async () => {
    if (window.confirm('¿Quieres indexar toda la biblioteca para habilitar la búsqueda IA? Esto puede tardar varios minutos dependiendo del número de libros.')) {
      try {
        const response = await fetch(`${API_URL}/rag/reindex/all`, { method: 'POST' });
        if (response.ok) {
          alert('El indexado ha comenzado en segundo plano. Los libros irán apareciendo en la búsqueda IA a medida que se procesen.');
        } else {
          alert('No se pudo iniciar el reindexado.');
        }
      } catch (err) {
        alert('Error de conexión.');
      }
    }
  };

  const bookGrid = useMemo(() => (
    <div className="book-grid">
      {books.map((book, index) => {
        const ref = (books.length === index + 1) ? lastBookElementRef : null;
        return (
          <div ref={ref} key={book.id}>
            <BookCard
              book={book}
              isMobile={isMobile}
              handleAuthorClick={handleAuthorClick}
              handleCategoryClick={handleCategoryClick}
              handleDeleteBook={handleDeleteBook}
              handleConvertToPdf={handleConvertToPdf}
              handleEditClick={handleEditClick}
              convertingId={convertingId}
              showConvertButton={Boolean(convertibilityMap.get(book.id))}
            />
          </div>
        );
      })}
    </div>
  ), [books, convertibilityMap, isMobile, handleAuthorClick, handleCategoryClick, handleDeleteBook, handleConvertToPdf, handleEditClick, convertingId, lastBookElementRef]);


  return (
    <div className="library-container">
      <h2>Mi Biblioteca</h2>

      <div className="controls-container">
        <div className="search-box">
          <input
            type="text"
            placeholder={searchMode === 'exact' ? "Buscar por título, autor o categoría..." : "Pregunta algo sobre tus libros o busca por temática..."}
            className="search-bar"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <div className="search-mode-selector">
            <button
              className={searchMode === 'exact' ? 'active' : ''}
              onClick={() => setSearchMode('exact')}
              title="Búsqueda por coincidencia exacta"
            >
              Exacta
            </button>
            <button
              className={searchMode === 'semantic' ? 'active' : ''}
              onClick={() => setSearchMode('semantic')}
              title="Búsqueda inteligente por IA"
            >
              IA 🪄
            </button>
          </div>
        </div>
      </div>

      {error && <p className="error-message">{error}</p>}

      {searchMode === 'semantic' && ragStats.total_documents === 0 && (
        <div className="rag-warning">
          <p>⚠️ <strong>Búsqueda IA no disponible:</strong> Tu biblioteca aún no ha sido indexada por la inteligencia artificial.</p>
          <button onClick={handleReindex} className="index-btn">Indexar mi biblioteca ahora</button>
        </div>
      )}

      {bookGrid}

      {loading && (
        <div className="book-grid">
          {[...Array(PAGE_SIZE)].map((_, i) => (
            <div key={`sk-${i}`} className="skeleton skeleton-card" />
          ))}
        </div>
      )}
      {!loading && !hasMore && books.length > 0 && <p className="end-of-results">Fin de los resultados</p>}
      {!loading && books.length === 0 && !error && (
        <p className="no-results">
          {searchMode === 'semantic'
            ? "La IA no ha encontrado libros con esa temática. Intenta con otra pregunta."
            : "No se encontraron libros que coincidan con tu búsqueda."}
        </p>
      )}


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
