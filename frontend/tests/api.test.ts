/**
 * Tests for the API client.
 *
 * Mocks fetch to test request/response handling without network calls.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { calculateFootprint, healthCheck, ApiClientError } from '../src/api/client';
import type { CarbonInput, CarbonResult } from '../src/types';

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

const validInput: CarbonInput = {
  device_id: 'test-device-001',
  transport_mode: 'car_petrol',
  distance_km: 30,
  trips_per_year: 250,
  electricity_kwh: 300,
  gas_kwh: 150,
  diet_type: 'meat_medium',
  consumption_level: 'medium',
};

describe('API Client', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('calculateFootprint sends correct POST request', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResult),
    });

    const result = await calculateFootprint(validInput);
    expect(result.total_kg).toBe(5000);
    expect(globalThis.fetch).toHaveBeenCalledWith(
      '/api/calculate',
      expect.objectContaining({ method: 'POST' }),
    );
  });

  it('healthCheck sends GET request', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ status: 'healthy' }),
    });

    const result = await healthCheck();
    expect(result.status).toBe('healthy');
  });

  it('throws ApiClientError on non-ok response', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 422,
      text: () => Promise.resolve(JSON.stringify({ detail: 'Validation error' })),
    });

    await expect(calculateFootprint(validInput)).rejects.toThrow(ApiClientError);
  });

  it('ApiClientError includes status code', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 429,
      text: () => Promise.resolve('Rate limited'),
    });

    try {
      await calculateFootprint(validInput);
    } catch (err) {
      expect(err).toBeInstanceOf(ApiClientError);
      expect((err as ApiClientError).status).toBe(429);
    }
  });

  it('handles non-JSON error response', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      text: () => Promise.resolve('Internal Server Error'),
    });

    await expect(calculateFootprint(validInput)).rejects.toThrow('Internal Server Error');
  });
});
