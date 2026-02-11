// frontend/src/__tests__/SearchForm.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { SearchForm } from '../SearchForm';

const dateRange = { minString: '2025-01-01', maxString: '2025-12-31' } as any;

test('llama a onSearch con los filtros cuando se envía el formulario', () => {
  const onSearch = jest.fn();
  render(<SearchForm onSearch={onSearch} isLoading={false} dateRange={dateRange} />);

  fireEvent.change(screen.getByPlaceholderText(/ej: daniel/i), { target: { value: 'Noboa' } });
  fireEvent.submit(screen.getByRole('form'));

  expect(onSearch).toHaveBeenCalledWith({ query: 'Noboa', dateFrom: '', dateTo: '' });
});

test('deshabilita el botón cuando no hay consulta o está cargando', () => {
  const { rerender } = render(
    <SearchForm onSearch={() => {}} isLoading={false} dateRange={dateRange} />
  );
  const button = screen.getByRole('button');
  expect(button).toBeDisabled();

  rerender(<SearchForm onSearch={() => {}} isLoading={true} dateRange={dateRange} />);
  expect(button).toBeDisabled();
});
