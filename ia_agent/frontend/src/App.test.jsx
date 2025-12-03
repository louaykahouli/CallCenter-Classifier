import { render, screen } from '@testing-library/react';
import App from './App';
import '@testing-library/jest-dom'; // <- add this line

test('renders without crashing', () => {
  render(<App />);
  expect(screen.getByText(/Classification/i)).toBeInTheDocument();
});
