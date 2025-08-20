import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import RagView from './RagView';
import API_URL from './config';


jest.mock('./config', () => ({
  __esModule: true,
  default: 'http://test-api.com'
}));

jest.mock('react-router-dom', () => ({
  useParams: () => ({ bookId: undefined })
}));


const mockFetch = jest.spyOn(global, 'fetch');

afterEach(() => {
  mockFetch.mockClear();
});

const mockBook = {id: '1', title: 'Test Book', author: 'Test Author', category: 'Test Category'};
const mockBooks = [mockBook];


describe('RagView', () => {
  it('renders without crashing', () => {
    render(<RagView />);
  });

  it('fetches library books on mount', async () => {
    mockFetch.mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(mockBooks) });
    render(<RagView />);
    expect(mockFetch).toHaveBeenCalledTimes(1);
    expect(mockFetch).toHaveBeenCalledWith('http://test-api.com/books/', expect.any(Object));
    });


  it('updates search results', async () => {
    mockFetch.mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(mockBooks) });
    render(<RagView />);
    const searchInput = screen.getByPlaceholderText('Buscar por título, autor o categoría...');
    fireEvent.change(searchInput, { target: { value: 'Test' } });
    await waitFor(() => expect(screen.getByText(mockBook.title)).toBeInTheDocument())
  });

  it('handles search with no results', async () => {
    mockFetch.mockResolvedValueOnce({ ok: true, json: () => Promise.resolve([]) });
    render(<RagView />);
    const searchInput = screen.getByPlaceholderText('Buscar por título, autor o categoría...');
    fireEvent.change(searchInput, { target: { value: 'NonExistentBook' } });
    await waitFor(() => expect(screen.getByText('Sin resultados')).toBeInTheDocument());
  });


  it('selects a book and checks RAG status', async () => {
    mockFetch.mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(mockBooks) })
      .mockResolvedValueOnce({ok: true, json: () => Promise.resolve({indexed: true, vector_count: 100})});
    render(<RagView />);
    const bookItem = screen.getByText(mockBook.title);
    fireEvent.click(bookItem);
    await waitFor(() => expect(screen.getByText('RAG listo (100)')).toBeInTheDocument());
  });

  it('indexes a book', async () => {
    mockFetch.mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(mockBooks) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({}) });
    render(<RagView />);
    const bookItem = screen.getByText(mockBook.title);
    fireEvent.click(bookItem);
    const indexButton = screen.getByText('Indexar antes de charlar');
    fireEvent.click(indexButton);
    await waitFor(() => expect(screen.getByText('Libro indexado')).toBeInTheDocument());

  });

  it('submits a query', async () => {
    mockFetch.mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(mockBooks) })
    .mockResolvedValueOnce({ok: true, json: () => Promise.resolve({indexed: true, vector_count: 100})})
    .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ response: 'Test response' }) });
    render(<RagView />);
    const bookItem = screen.getByText(mockBook.title);
    fireEvent.click(bookItem);
    const queryInput = screen.getByPlaceholderText('Haz una pregunta sobre el libro...');
    fireEvent.change(queryInput, { target: { value: 'Test query' } });
    fireEvent.submit(screen.getByRole('form'));
    await waitFor(() => expect(screen.getByText('Test response')).toBeInTheDocument());
  });

  it('handles query error', async () => {
    mockFetch.mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(mockBooks) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ indexed: true, vector_count: 100 }) })
      .mockResolvedValueOnce({ ok: false, json: () => Promise.resolve({ detail: 'Test error' }) });
    render(<RagView />);
    const bookItem = screen.getByText(mockBook.title);
    fireEvent.click(bookItem);
    const queryInput = screen.getByPlaceholderText('Haz una pregunta sobre el libro...');
    fireEvent.change(queryInput, { target: { value: 'Test query' } });
    fireEvent.submit(screen.getByRole('form'));
    await waitFor(() => expect(screen.getByText('Error: Test error')).toBeInTheDocument());
  });


  it('handles fetch errors gracefully', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'));
    render(<RagView />);
    // No debería haber errores de renderizado
  });

    it('displays the correct mode', () => {
    render(<RagView />);
    const modeRadios = screen.queryAllByRole('radio');
    expect(modeRadios.length).toBe(3);
    expect(screen.getByLabelText('Equilibrado (recomendado)')).toBeChecked();

    fireEvent.click(screen.getByLabelText('Solo libro'))
    expect(screen.getByLabelText('Solo libro')).toBeChecked();
    
    fireEvent.click(screen.getByLabelText('Abierto'))
    expect(screen.getByLabelText('Abierto')).toBeChecked();
  });
});