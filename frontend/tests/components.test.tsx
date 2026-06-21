import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { CategoryChart } from '../src/components/Calculator/CategoryChart';
import { HistoryTable } from '../src/components/History/HistoryTable';
import { HistoryChart } from '../src/components/History/HistoryChart';
import { ErrorBoundary } from '../src/components/shared/ErrorBoundary';
import App from '../src/App';

// Mock Recharts to avoid jsdom measurement errors
vi.mock('recharts', async () => {
  const original = (await vi.importActual('recharts')) as Record<string, unknown>;
  return {
    ...original,
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
      <div style={{ width: '800px', height: '600px' }} data-testid="responsive-container">
        {children}
      </div>
    ),
  };
});

// Mock Zustand store for App component tests
vi.mock('../src/store/carbonStore', () => {
  const mockStore = {
    transportMode: 'car_petrol',
    distanceKm: 20,
    tripsPerYear: 250,
    electricityKwh: 300,
    gasKwh: 150,
    dietType: 'meat_medium',
    consumptionLevel: 'medium',
    result: null,
    history: [],
    isLoading: false,
    isHistoryLoading: false,
    error: null,
    setTransportMode: vi.fn(),
    setDistanceKm: vi.fn(),
    setTripsPerYear: vi.fn(),
    setElectricityKwh: vi.fn(),
    setGasKwh: vi.fn(),
    setDietType: vi.fn(),
    setConsumptionLevel: vi.fn(),
    calculate: vi.fn(),
    fetchHistory: vi.fn(),
    clearError: vi.fn(),
    clearResult: vi.fn(),
  };
  return {
    useCarbonStore: vi.fn((selector) => {
      if (selector) return selector(mockStore);
      return mockStore;
    }),
  };
});

describe('CategoryChart', () => {
  const breakdown = { transport: 1000, home: 2000, diet: 1500, consumption: 500 };

  it('renders the chart container and elements', () => {
    const { container } = render(<CategoryChart breakdown={breakdown} />);
    expect(screen.getByText('Emissions Distribution')).toBeInTheDocument();
    // Verify the fallback table for screen readers is rendered
    expect(container.querySelector('caption')).toHaveTextContent('Carbon emissions breakdown');
  });
});

describe('HistoryTable', () => {
  const entries = [
    {
      id: 'entry-1',
      device_id: 'device-1',
      total_kg: 5000,
      breakdown: { transport: 2000, home: 1500, diet: 1000, consumption: 500 },
      created_at: '2026-06-21T10:00:00Z',
      insights_source: 'gemini',
    },
  ];

  it('renders empty history message when entries are empty', () => {
    render(<HistoryTable entries={[]} />);
    expect(screen.getByText(/No history yet/)).toBeInTheDocument();
  });

  it('renders history table with data', () => {
    render(<HistoryTable entries={entries} />);
    expect(screen.getByRole('table')).toBeInTheDocument();
    expect(screen.getByText('5.0 tonnes')).toBeInTheDocument(); // total_kg format
    expect(screen.getByText('gemini')).toBeInTheDocument();
  });
});

describe('HistoryChart', () => {
  const entries = [
    {
      id: 'entry-1',
      device_id: 'device-1',
      total_kg: 5000,
      breakdown: { transport: 2000, home: 1500, diet: 1000, consumption: 500 },
      created_at: '2026-06-21T10:00:00Z',
      insights_source: 'gemini',
    },
  ];

  it('returns null on empty entries', () => {
    const { container } = render(<HistoryChart entries={[]} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders trend chart with entries', () => {
    render(<HistoryChart entries={entries} />);
    expect(screen.getByText('Footprint Trend', { exact: false })).toBeInTheDocument();
  });
});

describe('ErrorBoundary', () => {
  const ProblematicComponent = () => {
    throw new Error('Test rendering error');
  };

  it('catches rendering errors and displays fallback UI', () => {
    // Suppress console.error in tests for this block
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {});

    render(
      <ErrorBoundary>
        <ProblematicComponent />
      </ErrorBoundary>,
    );

    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByText('Test rendering error')).toBeInTheDocument();

    // Trigger retry
    const retryBtn = screen.getByRole('button', { name: 'Try Again' });
    fireEvent.click(retryBtn);

    spy.mockRestore();
  });
});

describe('App Layout', () => {
  it('renders semantic landmarks and subcomponents', () => {
    render(<App />);
    // Check main layout areas
    expect(screen.getByRole('banner')).toBeInTheDocument(); // header
    expect(screen.getByRole('main')).toBeInTheDocument(); // main
    expect(screen.getByRole('contentinfo')).toBeInTheDocument(); // footer
  });
});
