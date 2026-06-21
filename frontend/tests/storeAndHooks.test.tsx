import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useCarbonStore } from '../src/store/carbonStore';
import { useCarbon } from '../src/hooks/useCarbon';
import { useHistory } from '../src/hooks/useHistory';
import { useInsights } from '../src/hooks/useInsights';
import * as client from '../src/api/client';

// Mock client functions
vi.mock('../src/api/client', () => ({
  calculateFootprint: vi.fn(),
  getHistory: vi.fn(),
}));

describe('Carbon Store and Hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset Zustand store state
    act(() => {
      useCarbonStore.setState({
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
      });
    });
  });

  it('allows updating form fields', () => {
    const { result } = renderHook(() => useCarbonStore());

    act(() => {
      result.current.setTransportMode('car_electric');
      result.current.setDistanceKm(50);
      result.current.setTripsPerYear(10);
      result.current.setElectricityKwh(400);
      result.current.setGasKwh(200);
      result.current.setDietType('vegetarian');
      result.current.setConsumptionLevel('low');
    });

    expect(result.current.transportMode).toBe('car_electric');
    expect(result.current.distanceKm).toBe(50);
    expect(result.current.tripsPerYear).toBe(10);
    expect(result.current.electricityKwh).toBe(400);
    expect(result.current.gasKwh).toBe(200);
    expect(result.current.dietType).toBe('vegetarian');
    expect(result.current.consumptionLevel).toBe('low');
  });

  it('runs useCarbon and calculate successfully', async () => {
    const mockResult = {
      total_kg: 4000,
      breakdown: { transport: 1500, home: 1000, diet: 1000, consumption: 500 },
      vs_global_average_pct: -5.0,
      vs_paris_target_pct: 120.0,
      ranked_categories: [],
      insights: [{ category: 'diet', tip: 'Eat less meat', severity: 'medium' as const }],
      source: 'rules' as const,
    };

    vi.mocked(client.calculateFootprint).mockResolvedValueOnce(mockResult);

    const { result } = renderHook(() => useCarbon());

    await act(async () => {
      await result.current.calculate();
    });

    expect(client.calculateFootprint).toHaveBeenCalled();
    expect(result.current.result).toEqual(mockResult);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();

    // Clear result
    act(() => {
      result.current.clearResult();
    });
    expect(result.current.result).toBeNull();
  });

  it('handles calculate error in useCarbon', async () => {
    vi.mocked(client.calculateFootprint).mockRejectedValueOnce(new Error('Calculation failed'));

    const { result } = renderHook(() => useCarbon());

    await act(async () => {
      await result.current.calculate();
    });

    expect(result.current.error).toBe('Calculation failed');
    expect(result.current.result).toBeNull();

    // Clear error
    act(() => {
      result.current.clearError();
    });
    expect(result.current.error).toBeNull();
  });

  it('runs useHistory hook and fetches history', async () => {
    const mockHistory = [
      {
        id: '1',
        device_id: 'test',
        total_kg: 5000,
        breakdown: { transport: 2000, home: 1500, diet: 1000, consumption: 500 },
        created_at: '2026-06-21T15:00:00Z',
        insights_source: 'rules',
      },
    ];

    vi.mocked(client.getHistory).mockResolvedValueOnce(mockHistory);

    const { result } = renderHook(() => useHistory());

    expect(result.current.isHistoryLoading).toBe(true);

    // Wait for async effect/fetchHistory
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });

    expect(client.getHistory).toHaveBeenCalled();
    expect(result.current.history).toEqual(mockHistory);
    expect(result.current.isHistoryLoading).toBe(false);
  });

  it('handles getHistory error', async () => {
    vi.mocked(client.getHistory).mockRejectedValueOnce(new Error('Fetch failed'));

    const { result } = renderHook(() => useHistory());

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });

    expect(result.current.history).toEqual([]);
    expect(result.current.isHistoryLoading).toBe(false);
  });

  it('returns insights correctly through useInsights hook', () => {
    // Initial state (no result)
    const { result, rerender } = renderHook(() => useInsights());
    expect(result.current.insights).toEqual([]);
    expect(result.current.source).toBe('rules');
    expect(result.current.hasInsights).toBe(false);

    // Set store state with results
    act(() => {
      useCarbonStore.setState({
        result: {
          total_kg: 3000,
          breakdown: { transport: 1000, home: 1000, diet: 500, consumption: 500 },
          vs_global_average_pct: -10,
          vs_paris_target_pct: 80,
          ranked_categories: [],
          insights: [{ category: 'transport', tip: 'Walk more', severity: 'high' }],
          source: 'gemini',
        },
      });
    });

    rerender();
    expect(result.current.insights).toEqual([{ category: 'transport', tip: 'Walk more', severity: 'high' }]);
    expect(result.current.source).toBe('gemini');
    expect(result.current.hasInsights).toBe(true);
  });
});
