/**
 * Tests for the ResultsDisplay component.
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ResultsDisplay } from '../src/components/Calculator/ResultsDisplay';
import type { CarbonResult } from '../src/types';

const mockResult: CarbonResult = {
  total_kg: 7500,
  breakdown: {
    transport: 3000,
    home: 1500,
    diet: 2000,
    consumption: 1000,
  },
  vs_global_average_pct: 87.5,
  vs_paris_target_pct: 275.0,
  ranked_categories: [
    { category: 'transport', kg: 3000 },
    { category: 'diet', kg: 2000 },
    { category: 'home', kg: 1500 },
    { category: 'consumption', kg: 1000 },
  ],
  insights: [],
  source: 'rules',
};

describe('ResultsDisplay', () => {
  it('renders the total emissions', () => {
    render(<ResultsDisplay result={mockResult} />);
    expect(screen.getByText('7.5 tonnes')).toBeInTheDocument();
  });

  it('shows vs global average comparison', () => {
    render(<ResultsDisplay result={mockResult} />);
    expect(screen.getByText('+87.5%')).toBeInTheDocument();
  });

  it('shows vs Paris target comparison', () => {
    render(<ResultsDisplay result={mockResult} />);
    expect(screen.getByText('+275.0%')).toBeInTheDocument();
  });

  it('renders all category breakdown bars', () => {
    render(<ResultsDisplay result={mockResult} />);
    expect(screen.getByText('transport')).toBeInTheDocument();
    expect(screen.getByText('diet')).toBeInTheDocument();
    expect(screen.getByText('home')).toBeInTheDocument();
    expect(screen.getByText('consumption')).toBeInTheDocument();
  });

  it('has progress bars with ARIA attributes', () => {
    render(<ResultsDisplay result={mockResult} />);
    const progressBars = screen.getAllByRole('progressbar');
    expect(progressBars.length).toBe(4);
    expect(progressBars[0]).toHaveAttribute('aria-valuenow');
    expect(progressBars[0]).toHaveAttribute('aria-valuemin', '0');
    expect(progressBars[0]).toHaveAttribute('aria-valuemax', '100');
  });

  it('has an accessible section label', () => {
    render(<ResultsDisplay result={mockResult} />);
    expect(screen.getByRole('region', { name: /calculation results/i })).toBeInTheDocument();
  });

  it('shows source badge', () => {
    render(<ResultsDisplay result={mockResult} />);
    expect(screen.getByText(/rule-based insights/i)).toBeInTheDocument();
  });
});
