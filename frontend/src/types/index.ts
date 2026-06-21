/**
 * Types for the Carbon Footprint Awareness Platform.
 *
 * These mirror the backend Pydantic models for type-safe API communication.
 */

export type TransportMode =
  | 'car_petrol'
  | 'car_diesel'
  | 'car_electric'
  | 'bus'
  | 'train'
  | 'flight_short_haul'
  | 'flight_long_haul';

export type DietType = 'meat_heavy' | 'meat_medium' | 'vegetarian' | 'vegan';

export type ConsumptionLevel = 'high' | 'medium' | 'low';

export interface CarbonInput {
  device_id: string;
  transport_mode: TransportMode;
  distance_km: number;
  trips_per_year: number;
  electricity_kwh: number;
  gas_kwh: number;
  diet_type: DietType;
  consumption_level: ConsumptionLevel;
}

export interface CategoryBreakdown {
  transport: number;
  home: number;
  diet: number;
  consumption: number;
}

export interface RankedCategory {
  category: string;
  kg: number;
}

export interface Insight {
  category: string;
  tip: string;
  severity: 'high' | 'medium' | 'low';
}

export interface CarbonResult {
  total_kg: number;
  breakdown: CategoryBreakdown;
  vs_global_average_pct: number;
  vs_paris_target_pct: number;
  ranked_categories: RankedCategory[];
  insights: Insight[];
  source: 'gemini' | 'rules';
}

export interface InsightsResponse {
  insights: Insight[];
  source: 'gemini' | 'rules';
  device_id: string;
}

export interface HistoryEntry {
  id: string;
  device_id: string;
  total_kg: number;
  breakdown: CategoryBreakdown;
  insights_source: string;
  created_at: string;
}

export interface ApiError {
  detail: string;
  status: number;
}
