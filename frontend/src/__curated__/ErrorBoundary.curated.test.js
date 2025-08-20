import React from 'react';
import { render, screen } from '@testing-library/react';
import ErrorBoundary from '../ErrorBoundary';

test('ErrorBoundary shows fallback and message', () => {
  const Boom = () => { throw new Error('Custom error'); };
  render(
    <ErrorBoundary>
      <Boom />
    </ErrorBoundary>
  );
  expect(screen.getByText('Ocurrió un error en la interfaz')).toBeInTheDocument();
  expect(screen.getByText('Custom error')).toBeInTheDocument();
});

