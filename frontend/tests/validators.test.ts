import { describe, it, expect } from 'vitest';
import { validateCarbonInput } from '../src/utils/validators';

describe('Validators', () => {
  const validData = {
    transport_mode: 'car_petrol',
    distance_km: 100,
    trips_per_year: 50,
    electricity_kwh: 200,
    gas_kwh: 100,
    diet_type: 'vegan',
    consumption_level: 'low',
  };

  it('validates a correct payload', () => {
    const result = validateCarbonInput(validData);
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.transport_mode).toBe('car_petrol');
    }
  });

  it('fails validation on negative numbers', () => {
    const result = validateCarbonInput({
      ...validData,
      distance_km: -10,
    });
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.errors.length).toBeGreaterThan(0);
      expect(result.errors[0]).toContain('Distance must be non-negative');
    }
  });

  it('fails validation on excessive numbers', () => {
    const result = validateCarbonInput({
      ...validData,
      distance_km: 100001,
    });
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.errors[0]).toContain('Distance cannot exceed 100,000 km');
    }
  });

  it('fails validation on invalid enum values', () => {
    const result = validateCarbonInput({
      ...validData,
      diet_type: 'invalid-diet-type',
    });
    expect(result.success).toBe(false);
  });
});
