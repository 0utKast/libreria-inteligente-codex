import React from 'react';
import { render, screen } from '@testing-library/react';
import RagView from '../RagView';

beforeEach(() => {
  // Mock fetch for /books/
  global.fetch = jest.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve([]) }));
});

afterEach(() => {
  global.fetch && global.fetch.mockRestore && global.fetch.mockRestore();
});

test('RagView renders heading', async () => {
  render(<RagView />);
  expect(await screen.findByText('Conversación Inteligente con Libros')).toBeInTheDocument();
});

