/**
 * Zod validation schemas for form inputs.
 *
 * Mirrors backend Pydantic constraints for client-side validation.
 */

import { z } from 'zod';

export const carbonInputSchema = z.object({
  transport_mode: z.enum([
    'car_petrol',
    'car_diesel',
    'car_electric',
    'bus',
    'train',
    'flight_short_haul',
    'flight_long_haul',
  ]),
  distance_km: z
    .number()
    .min(0, 'Distance must be non-negative')
    .max(100000, 'Distance cannot exceed 100,000 km'),
  trips_per_year: z
    .number()
    .int('Must be a whole number')
    .min(0, 'Trips must be non-negative')
    .max(1000, 'Trips cannot exceed 1,000'),
  electricity_kwh: z
    .number()
    .min(0, 'Electricity must be non-negative')
    .max(10000, 'Electricity cannot exceed 10,000 kWh'),
  gas_kwh: z
    .number()
    .min(0, 'Gas must be non-negative')
    .max(10000, 'Gas cannot exceed 10,000 kWh'),
  diet_type: z.enum(['meat_heavy', 'meat_medium', 'vegetarian', 'vegan']),
  consumption_level: z.enum(['high', 'medium', 'low']),
});

export type CarbonInputForm = z.infer<typeof carbonInputSchema>;

/**
 * Validate form inputs and return errors (if any).
 */
export function validateCarbonInput(
  data: Record<string, unknown>,
): { success: true; data: CarbonInputForm } | { success: false; errors: string[] } {
  const result = carbonInputSchema.safeParse(data);
  if (result.success) {
    return { success: true, data: result.data };
  }
  const errors = result.error.issues.map(
    (issue) => `${issue.path.join('.')}: ${issue.message}`,
  );
  return { success: false, errors };
}
