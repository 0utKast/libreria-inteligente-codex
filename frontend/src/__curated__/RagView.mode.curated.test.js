import React from 'react';
import { render, screen } from '@testing-library/react';
import RagView from '../RagView';

beforeEach(() => {
  global.fetch = jest.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve([]) }));
});

afterEach(() => {
  global.fetch && global.fetch.mockRestore && global.fetch.mockRestore();
});

test('renderiza la tarjeta de modo y opciones', async () => {
  render(<RagView />);
  expect(await screen.findByText('Preferencia de respuesta')).toBeInTheDocument();
  expect(screen.getByText(/Equilibrado/i)).toBeInTheDocument();
  expect(screen.getByText(/Solo libro/i)).toBeInTheDocument();
  expect(screen.getByText(/Abierto/i)).toBeInTheDocument();
});

