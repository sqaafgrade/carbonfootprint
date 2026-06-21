/**
 * Tests for the CarbonForm component.
 *
 * Verifies form rendering, label associations, accessibility,
 * and form submission behavior.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { CarbonForm } from '../src/components/Calculator/CarbonForm';

// Mock the store
const mockCalculate = vi.fn();
const mockClearError = vi.fn();

vi.mock('../src/store/carbonStore', () => ({
  useCarbonStore: () => ({
    transportMode: 'car_petrol',
    distanceKm: 20,
    tripsPerYear: 250,
    electricityKwh: 300,
    gasKwh: 150,
    dietType: 'meat_medium',
    consumptionLevel: 'medium',
    isLoading: false,
    error: null,
    setTransportMode: vi.fn(),
    setDistanceKm: vi.fn(),
    setTripsPerYear: vi.fn(),
    setElectricityKwh: vi.fn(),
    setGasKwh: vi.fn(),
    setDietType: vi.fn(),
    setConsumptionLevel: vi.fn(),
    calculate: mockCalculate,
    clearError: mockClearError,
  }),
}));

describe('CarbonForm', () => {
  it('renders the form with all required inputs', () => {
    render(<CarbonForm />);

    expect(screen.getByLabelText(/primary transport mode/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/weekly distance/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/trips per year/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/monthly electricity/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/monthly gas/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/dietary pattern/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/consumption level/i)).toBeInTheDocument();
  });

  it('renders the submit button', () => {
    render(<CarbonForm />);
    expect(screen.getByRole('button', { name: /calculate my footprint/i })).toBeInTheDocument();
  });

  it('has an accessible form label', () => {
    render(<CarbonForm />);
    expect(screen.getByRole('form', { name: /carbon footprint calculator/i })).toBeInTheDocument();
  });

  it('has aria-describedby hints for key inputs', () => {
    render(<CarbonForm />);
    const transportSelect = screen.getByLabelText(/primary transport mode/i);
    expect(transportSelect).toHaveAttribute('aria-describedby', 'transport-mode-hint');
  });

  it('calls calculate on form submission', async () => {
    const user = userEvent.setup();
    render(<CarbonForm />);
    const button = screen.getByRole('button', { name: /calculate my footprint/i });
    await user.click(button);
    expect(mockCalculate).toHaveBeenCalled();
  });

  it('renders all transport mode options', () => {
    render(<CarbonForm />);
    const select = screen.getByLabelText(/primary transport mode/i) as HTMLSelectElement;
    const options = Array.from(select.options).map((o) => o.value);
    expect(options).toContain('car_petrol');
    expect(options).toContain('train');
    expect(options).toContain('flight_long_haul');
  });

  it('has unique IDs on interactive elements', () => {
    render(<CarbonForm />);
    expect(document.getElementById('transport-mode')).toBeTruthy();
    expect(document.getElementById('distance-km')).toBeTruthy();
    expect(document.getElementById('trips-year')).toBeTruthy();
    expect(document.getElementById('electricity-kwh')).toBeTruthy();
    expect(document.getElementById('gas-kwh')).toBeTruthy();
    expect(document.getElementById('diet-type')).toBeTruthy();
    expect(document.getElementById('consumption-level')).toBeTruthy();
    expect(document.getElementById('calculate-button')).toBeTruthy();
  });
});
