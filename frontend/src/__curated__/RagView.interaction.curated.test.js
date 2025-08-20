import React from 'react';
import { render, screen } from '@testing-library/react';
import RagView from '../RagView';

beforeEach(() => {
  global.fetch = jest.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve([]) }));
});

afterEach(() => {
  global.fetch && global.fetch.mockRestore && global.fetch.mockRestore();
});

test('Enviar está deshabilitado cuando el chat no está listo', async () => {
  render(<RagView />);
  const sendButton = await screen.findByRole('button', { name: /enviar/i });
  expect(sendButton).toBeDisabled();
});

