import React, { useState, useEffect, useMemo, useRef } from 'react';
import API_URL from './config';
import './RagView.css';

function RagView() {
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [bookId, setBookId] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [currentQuery, setCurrentQuery] = useState('');
  // Soporte opcional: seleccionar libro existente y indexarlo solo cuando se quiera
  const [libraryBooks, setLibraryBooks] = useState([]);
  const [selectedLibraryId, setSelectedLibraryId] = useState('');
  const [libStatus, setLibStatus] = useState({ loading: false, indexed: false, vector_count: 0, error: null });
  const [actionsBusy, setActionsBusy] = useState(false); // bloquea acciones pesadas (index/reindex)
  const [refreshing, setRefreshing] = useState(false);   // refresco de estado (no bloquea chatear)
  const [searchTerm, setSearchTerm] = useState('');
  const [searching, setSearching] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [resultsOpen, setResultsOpen] = useState(false);
  const [mode, setMode] = useState('balanced');
  const qNonEmpty = (s) => String(s || '').trim().length > 0;
  const chatReady = Boolean(selectedLibraryId && libStatus.indexed && String(bookId || '') === String(selectedLibraryId || ''));
  const [selectedBook, setSelectedBook] = useState(null);
  const inputRef = useRef(null);
  const chatHistoryRef = useRef(null);

  const currentBook = useMemo(() => {
    const id = selectedLibraryId || bookId;
    if (!id) return null;
    // Prefer the explicit selection if matches
    if (selectedBook && String(selectedBook.id) === String(id)) return selectedBook;
    return libraryBooks.find(b => String(b.id) === String(id)) || null;
  }, [selectedLibraryId, bookId, selectedBook, libraryBooks]);

  const focusChatInput = () => {
    try { if (inputRef.current) inputRef.current.focus(); } catch (_) {}
  };

  // Auto-scroll al final del chat cuando llegan mensajes o mientras esperamos respuesta
  useEffect(() => {
    try {
      if (chatHistoryRef.current) {
        chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
      }
    } catch (_) {}
  }, [chatHistory, isLoading]);

  useEffect(() => {
    // Cargar lista de libros para permitir seleccionar uno existente
    const fetchBooks = async () => {
      try {
        const res = await fetch(`${API_URL.replace(/\/$/, '')}/books/`);
        if (!res.ok) throw new Error(`Error ${res.status}`);
        const data = await res.json();
        setLibraryBooks(data);
      } catch (e) {
        // Vista opcional: si falla, no bloquea el flujo de subir archivo
      }
    };
    fetchBooks();
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    const q = searchTerm.trim();
    if (!q) {
      setSearchResults([]);
      setResultsOpen(false);
      return;
    }
    const timer = setTimeout(async () => {
      try {
        setSearching(true);
        // Buscar por título o autor usando el parámetro 'search' del endpoint principal
        const url = `${API_URL.replace(/\/$/, '')}/books/?search=${encodeURIComponent(q)}`;
        const res = await fetch(url, { signal: controller.signal });
        if (res.ok) {
          const data = await res.json();
          setSearchResults(data.slice(0, 10));
        }
      } catch (_) {
        // ignore
      } finally {
        setSearching(false);
      }
    }, 250);
    return () => {
      controller.abort();
      clearTimeout(timer);
    };
  }, [searchTerm]);

  // Eliminado: subida directa de archivo en esta vista para simplificar la UI

  const handleQuerySubmit = async (event) => {
    event.preventDefault();
    if (!bookId || !currentQuery.trim() || !chatReady) {
      return;
    }

    const newChatHistory = [...chatHistory, { sender: 'user', text: currentQuery }];
    setChatHistory(newChatHistory);
    setCurrentQuery('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/rag/query/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: currentQuery, book_id: bookId, mode }),
      });

      if (response.ok) {
        const result = await response.json();
        setChatHistory([...newChatHistory, { sender: 'gemini', text: result.response }]);
      } else {
        const result = await response.json();
        setChatHistory([...newChatHistory, { sender: 'gemini', text: `Error: ${result.detail || 'No se pudo obtener respuesta.'}` }]);
      }
    } catch (error) {
      setChatHistory([...newChatHistory, { sender: 'gemini', text: 'Error de conexión al consultar.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const checkLibraryStatus = async (silent = false) => {
    if (!selectedLibraryId) return;
    if (!silent) setRefreshing(true);
    try {
      const res = await fetch(`${API_URL.replace(/\/$/, '')}/rag/status/${selectedLibraryId}`);
      if (!res.ok) throw new Error(`Error ${res.status}`);
      const data = await res.json();
      const isIndexed = !!data.indexed;
      setLibStatus(prev => ({ ...prev, loading: false, indexed: isIndexed, vector_count: data.vector_count || 0, error: null }));
      if (isIndexed) {
        if (String(bookId || '') !== String(selectedLibraryId || '')) {
          setBookId(String(selectedLibraryId));
          setChatHistory([]);
          setMessage(`Conversación reiniciada para "${(currentBook && currentBook.title) || (selectedBook && selectedBook.title) || 'libro seleccionado'}".`);
          if (!silent) { try { if (inputRef && inputRef.current) inputRef.current.focus(); } catch (_) {} }
        } else if (!silent) {
          setMessage(`"${(currentBook && currentBook.title) || (selectedBook && selectedBook.title) || 'Libro'}" listo para chatear.`);
          try { if (inputRef && inputRef.current) inputRef.current.focus(); } catch (_) {}
        }
      } else if (!silent) {
        setMessage(`Sin índice RAG para "${(currentBook && currentBook.title) || (selectedBook && selectedBook.title) || 'libro seleccionado'}". Pulsa "Indexar antes de charlar".`);
      }
    } catch (e) {
      setLibStatus(prev => ({ ...prev, loading: false, indexed: false, vector_count: 0, error: e.message }));
    }
    if (!silent) setRefreshing(false);
  };

  const indexLibraryBook = async (force = false) => {
    if (!selectedLibraryId) return;
    setActionsBusy(true);
    setLibStatus(prev => ({ ...prev, error: null }));
    try {
      setMessage(`Indexando "${selectedBook?.title || 'libro seleccionado'}"...`);
      const res = await fetch(`${API_URL.replace(/\/$/, '')}/rag/index/${selectedLibraryId}?force=${force ? 'true' : 'false'}`, { method: 'POST' });
      if (!res.ok) throw new Error(`Error ${res.status}`);
      // Optimista: marcar como indexado y habilitar chatear de inmediato
      setLibStatus(prev => ({ ...prev, loading: false, indexed: true }));
      setActionsBusy(false);
      setBookId(String(selectedLibraryId));
      setMessage(`"${(currentBook && currentBook.title) || (selectedBook && selectedBook.title) || 'Libro'}" indexado. ¡Listo para chatear!`);
      setChatHistory([]);
      // Refrescar el recuento de vectores sin bloquear UI
      checkLibraryStatus(true);
      try { if (inputRef && inputRef.current) inputRef.current.focus(); } catch (_) {}
    } catch (e) {
      setActionsBusy(false);
      setLibStatus(prev => ({ ...prev, loading: false, error: e.message }));
      setMessage(`Error al indexar "${selectedBook?.title || 'libro seleccionado'}": ${e.message}`);
    }
  };

  // Al seleccionar un libro, comprobar automáticamente su estado RAG
  useEffect(() => {
    if (selectedLibraryId) {
      checkLibraryStatus(false);
    } else {
      setLibStatus({ loading: false, indexed: false, vector_count: 0, error: null });
    }
  }, [selectedLibraryId]);

  return (
    <div className="rag-container">
      <h2>Conversación Inteligente con Libros</h2>
      <p>Elige un libro de tu biblioteca para indexarlo y conversar con la IA.</p>
      <p className="rag-note">El indexado divide el contenido del libro en fragmentos y crea vectores semánticos. Esto permite recuperar pasajes relevantes y mejora la calidad y rapidez de las respuestas.</p>

      {/* Bloque opcional: buscar libro existente en la biblioteca e indexarlo antes de charlar */}
      <div className="upload-section rag-lib-block">
        <div className="rag-lib-row">
          <input
            type="text"
            className="rag-search-input"
            placeholder="Buscar por título, autor o categoría..."
            value={searchTerm}
            onChange={(e) => { setSearchTerm(e.target.value); setResultsOpen(true); }}
          />
          {searching && <span className="rag-search-hint">Buscando…</span>}
        </div>
        {resultsOpen && (searchResults.length > 0 || (!searching && qNonEmpty(searchTerm))) && (
          <ul className="rag-results">
            {searchResults.length > 0 ? (
              searchResults.map(b => (
                <li key={b.id} onClick={() => { setSelectedLibraryId(String(b.id)); setSelectedBook(b); setSearchResults([]); setSearchTerm(`${b.title} — ${b.author} — ${b.category}`); setResultsOpen(false); setMessage(`Comprobando índice para "${b.title}"...`); }}>
                  <div className="rag-result-title">{b.title}</div>
                  <div className="rag-result-author">{b.author}</div>
                  <div className="rag-result-category">{b.category}</div>
                </li>
              ))
            ) : (
              <li className="rag-no-results">Sin resultados</li>
            )}
          </ul>
        )}
        <div className="rag-actions">
          <button className="upload-button" onClick={() => checkLibraryStatus(false)} disabled={!selectedLibraryId || actionsBusy || refreshing}>
            {refreshing ? 'Comprobando…' : 'Comprobar RAG'}
          </button>
          <button className="upload-button" onClick={() => indexLibraryBook(false)} disabled={!selectedLibraryId || actionsBusy}>
            {actionsBusy ? 'Procesando…' : 'Indexar antes de charlar'}
          </button>
          <button className="upload-button" onClick={() => indexLibraryBook(true)} disabled={!selectedLibraryId || actionsBusy}>
            {actionsBusy ? 'Procesando…' : 'Reindexar'}
          </button>
          <button
            className="upload-button"
            onClick={() => { if (selectedLibraryId && libStatus.indexed) { setBookId(String(selectedLibraryId)); setMessage(`Conversación iniciada para "${(currentBook && currentBook.title) || (selectedBook && selectedBook.title) || 'libro seleccionado'}".`); setChatHistory([]); try { if (inputRef && inputRef.current) inputRef.current.focus(); } catch (_) {} } }}
            disabled={!selectedLibraryId || !libStatus.indexed || actionsBusy}
          >
            Chatear
          </button>
          {selectedLibraryId && !libStatus.loading && (
            <span className={`rag-status-pill ${libStatus.indexed ? 'rag-status-ok' : 'rag-status-warn'}`} title={`vectores: ${libStatus.vector_count}`}>
              {libStatus.indexed ? `RAG listo (${libStatus.vector_count})` : 'Sin índice RAG'}
            </span>
          )}
          {libStatus.error && <span className="rag-error">Error: {libStatus.error}</span>}
        </div>
        <div className="rag-mode-card">
          <div className="rag-mode-header">
            <div className="rag-mode-title">Preferencia de respuesta</div>
            <div className="rag-mode-subtitle">Elige cómo combinar el contenido del libro con el conocimiento general</div>
          </div>
          <div className="rag-mode-options">
            <label className={`rag-mode-option ${mode === 'strict' ? 'active' : ''}`}>
              <input
                type="radio"
                name="rag-mode"
                value="strict"
                checked={mode === 'strict'}
                onChange={(e) => setMode(e.target.value)}
              />
              <span className="rag-mode-badge">Solo libro</span>
              <span className="rag-mode-desc">Responde exclusivamente con lo que aparece en el libro. Si falta, lo indica.</span>
            </label>
            <label className={`rag-mode-option ${mode === 'balanced' ? 'active' : ''}`}>
              <input
                type="radio"
                name="rag-mode"
                value="balanced"
                checked={mode === 'balanced'}
                onChange={(e) => setMode(e.target.value)}
              />
              <span className="rag-mode-badge">Equilibrado (recomendado)</span>
              <span className="rag-mode-desc">Prioriza el libro y, si falta información, añade contexto general marcado como “Nota”.</span>
            </label>
            <label className={`rag-mode-option ${mode === 'open' ? 'active' : ''}`}>
              <input
                type="radio"
                name="rag-mode"
                value="open"
                checked={mode === 'open'}
                onChange={(e) => setMode(e.target.value)}
              />
              <span className="rag-mode-badge">Abierto</span>
              <span className="rag-mode-desc">Combina libremente libro y conocimiento general, manteniendo el libro como referencia principal.</span>
            </label>
          </div>
        </div>
        {message && <p className="message">{message}</p>}
      </div>


      {bookId && (
        <div className="chat-section">
          <div className="chat-context">Conversando sobre: <strong>{(currentBook && currentBook.title) || (selectedBook && selectedBook.title) || `Libro #${bookId}`}</strong>{((currentBook && currentBook.author) || (selectedBook && selectedBook.author)) ? ` — ${(currentBook && currentBook.author) || (selectedBook && selectedBook.author)}` : ''}{` • Modo: ${({ strict: 'Solo libro', balanced: 'Equilibrado', open: 'Abierto' }[mode] || 'Equilibrado')}`}</div>
          <h3>Conversación sobre el libro</h3>
          <div className="chat-history" ref={chatHistoryRef}>
            {chatHistory.map((msg, index) => (
              <div key={index} className={`chat-message ${msg.sender}`}>
                <strong>{msg.sender === 'user' ? 'Tú' : 'Gemini'}:</strong> {msg.text}
              </div>
            ))}
            {isLoading && (
              <div className="chat-message gemini pending">
                <strong>Gemini:</strong> Esperando respuesta...
              </div>
            )}
          </div>
          <form onSubmit={handleQuerySubmit} className="chat-input-form">
            <textarea
              value={currentQuery}
              onChange={(e) => { setCurrentQuery(e.target.value); try { const el = e.target; el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 200) + 'px'; } catch(_) {} }}
              onInput={(e) => { try { const el = e.target; el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 200) + 'px'; } catch(_) {} }}
              placeholder="Haz una pregunta sobre el libro..."
              disabled={isLoading || !chatReady}
              ref={inputRef}
              rows={1}
            />
            <button type="submit" disabled={isLoading || !currentQuery.trim() || !chatReady}>
              Enviar
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

export default RagView;
