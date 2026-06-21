/**
 * API client for communicating with the Carbon Platform backend.
 *
 * Centralises fetch logic, error handling, and response parsing.
 */

import type { CarbonInput, CarbonResult, HistoryEntry } from '../types';

const API_BASE = '/api';

class ApiClientError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiClientError';
    this.status = status;
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorBody = await response.text();
    let message = `API error: ${response.status}`;
    try {
      const parsed = JSON.parse(errorBody) as { detail?: string };
      if (parsed.detail) {
        message = parsed.detail;
      }
    } catch {
      // Use raw text if not JSON
      if (errorBody) message = errorBody;
    }
    throw new ApiClientError(message, response.status);
  }

  return response.json() as Promise<T>;
}

export async function calculateFootprint(
  input: CarbonInput,
): Promise<CarbonResult> {
  return request<CarbonResult>('/calculate', {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

export async function getHistory(
  deviceId: string,
  limit = 20,
): Promise<HistoryEntry[]> {
  return request<HistoryEntry[]>(
    `/entries?device_id=${encodeURIComponent(deviceId)}&limit=${limit}`,
  );
}

export async function healthCheck(): Promise<{ status: string }> {
  return request<{ status: string }>('/health');
}

export { ApiClientError };
