import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ErrorBoundary from './ErrorBoundary';

test('renders without crashing', () => {
  render(<ErrorBoundary><div>Test</div></ErrorBoundary>);
});

test('renders fallback UI when error occurs', () => {
  const TestComponent = () => {
    throw new Error('Test error');
  };

  render(
    <ErrorBoundary>
      <TestComponent />
    </ErrorBoundary>
  );

  expect(screen.getByText('Ocurrió un error en la interfaz')).toBeInTheDocument();
  expect(screen.getByRole('textbox')).toBeInTheDocument(); //pre tag is a textbox
});


test('logs error to console', () => {
  const error = new Error('Test error');
  const consoleErrorSpy = jest.spyOn(console, 'error');
  const TestComponent = () => {
    throw error;
  };

  render(
    <ErrorBoundary>
      <TestComponent />
    </ErrorBoundary>
  );

  expect(consoleErrorSpy).toHaveBeenCalledWith('UI error:', error, expect.objectContaining({componentStack: expect.any(String)}));
  consoleErrorSpy.mockRestore();
});

test('renders children when no error', () => {
  render(<ErrorBoundary><div>Test</div></ErrorBoundary>);
  expect(screen.getByText('Test')).toBeInTheDocument();
});

test('handles empty props', () => {
  render(<ErrorBoundary/>);
  expect(screen.queryByText('Ocurrió un error en la interfaz')).not.toBeInTheDocument();

});

test('displays error details', () => {
    const error = new Error('Custom error message');
    const TestComponent = () => { throw error; };
  
    render(
      <ErrorBoundary>
        <TestComponent />
      </ErrorBoundary>
    );
  
    expect(screen.getByText('Custom error message')).toBeInTheDocument();
  });