// frontend/src/__tests__/SentimentCard.test.tsx
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { SentimentCard } from '../SentimentCard';

test('muestra los valores correctos para el sentimiento positivo', () => {
  render(<SentimentCard type="positive" count={20} percentage={60} uniqueUsers={15} />);
  expect(screen.getByText(/Positivo/i)).toBeInTheDocument();
  expect(screen.getByText('20')).toBeInTheDocument();
  expect(screen.getByText('15')).toBeInTheDocument();
  // Usa toHaveTextContent si deseas verificar el formato del porcentaje
  expect(screen.getByText(/60.0%/i)).toBeInTheDocument();
});
