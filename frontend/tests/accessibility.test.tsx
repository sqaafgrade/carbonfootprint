/**
 * Accessibility tests using jest-axe.
 *
 * Verifies every major component has zero axe-core violations.
 */

import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { CarbonForm } from '../src/components/Calculator/CarbonForm';
import { ResultsDisplay } from '../src/components/Calculator/ResultsDisplay';
import { InsightsList } from '../src/components/Insights/InsightsList';
import { SkipLink } from '../src/components/shared/SkipLink';
import { LoadingSpinner } from '../src/components/shared/LoadingSpinner';
import type { CarbonResult, Insight } from '../src/types';

expect.extend(toHaveNoViolations);

// Mock the store for CarbonForm
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
    calculate: vi.fn(),
    clearError: vi.fn(),
  }),
}));

const mockResult: CarbonResult = {
  total_kg: 5000,
  breakdown: { transport: 2000, home: 1000, diet: 1500, consumption: 500 },
  vs_global_average_pct: 25.0,
  vs_paris_target_pct: 150.0,
  ranked_categories: [
    { category: 'transport', kg: 2000 },
    { category: 'diet', kg: 1500 },
    { category: 'home', kg: 1000 },
    { category: 'consumption', kg: 500 },
  ],
  insights: [],
  source: 'rules',
};

const mockInsights: Insight[] = [
  { category: 'transport', tip: 'Consider cycling for trips under 5km instead of driving', severity: 'high' },
  { category: 'diet', tip: 'Try having meatless meals twice a week for your diet', severity: 'medium' },
  { category: 'home', tip: 'Switch to LED light bulbs throughout your entire home', severity: 'low' },
];

describe('Accessibility (axe-core)', () => {
  it('CarbonForm has no accessibility violations', async () => {
    const { container } = render(<CarbonForm />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('ResultsDisplay has no accessibility violations', async () => {
    const { container } = render(<ResultsDisplay result={mockResult} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('InsightsList has no accessibility violations', async () => {
    const { container } = render(
      <InsightsList insights={mockInsights} source="rules" />,
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('SkipLink has no accessibility violations', async () => {
    const { container } = render(<SkipLink />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('LoadingSpinner has no accessibility violations', async () => {
    const { container } = render(<LoadingSpinner />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
