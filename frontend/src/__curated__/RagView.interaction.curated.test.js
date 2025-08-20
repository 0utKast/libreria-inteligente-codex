import React from 'react';
import { render, screen } from '@testing-library/react';
import RagView from '../RagView';

beforeEach(() => {
  global.fetch = jest.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve([]) }));
});

afterEach(() => {
  global.fetch && global.fetch.mockRestore && global.fetch.mockRestore();
});

test('No hay botón "Enviar" y "Chatear" está deshabilitado hasta estar listo', async () => {
  render(<RagView />);
  // En estado inicial no se muestra la sección de chat, por lo que no existe el botón "Enviar"
  expect(screen.queryByRole('button', { name: /enviar/i })).toBeNull();
  // El CTA principal para iniciar el chat debe estar deshabilitado
  const chatButton = await screen.findByRole('button', { name: /chatear/i });
  expect(chatButton).toBeDisabled();
});
