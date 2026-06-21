/**
 * Zustand store for carbon footprint state management.
 *
 * Manages form inputs, calculation results, loading states, and history.
 */

import { create } from 'zustand';
import type {
  CarbonInput,
  CarbonResult,
  HistoryEntry,
  TransportMode,
  DietType,
  ConsumptionLevel,
} from '../types';
import { calculateFootprint, getHistory } from '../api/client';

function getOrCreateDeviceId(): string {
  const stored = localStorage.getItem('carbon-device-id');
  if (stored) return stored;
  const id = crypto.randomUUID();
  localStorage.setItem('carbon-device-id', id);
  return id;
}

interface CarbonState {
  // Form inputs
  transportMode: TransportMode;
  distanceKm: number;
  tripsPerYear: number;
  electricityKwh: number;
  gasKwh: number;
  dietType: DietType;
  consumptionLevel: ConsumptionLevel;

  // Results
  result: CarbonResult | null;
  history: HistoryEntry[];

  // UI state
  isLoading: boolean;
  isHistoryLoading: boolean;
  error: string | null;

  // Actions
  setTransportMode: (mode: TransportMode) => void;
  setDistanceKm: (km: number) => void;
  setTripsPerYear: (trips: number) => void;
  setElectricityKwh: (kwh: number) => void;
  setGasKwh: (kwh: number) => void;
  setDietType: (diet: DietType) => void;
  setConsumptionLevel: (level: ConsumptionLevel) => void;
  calculate: () => Promise<void>;
  fetchHistory: () => Promise<void>;
  clearError: () => void;
  clearResult: () => void;
}

export const useCarbonStore = create<CarbonState>((set, get) => ({
  // Default form values
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

  setTransportMode: (mode) => set({ transportMode: mode }),
  setDistanceKm: (km) => set({ distanceKm: km }),
  setTripsPerYear: (trips) => set({ tripsPerYear: trips }),
  setElectricityKwh: (kwh) => set({ electricityKwh: kwh }),
  setGasKwh: (kwh) => set({ gasKwh: kwh }),
  setDietType: (diet) => set({ dietType: diet }),
  setConsumptionLevel: (level) => set({ consumptionLevel: level }),

  calculate: async () => {
    set({ isLoading: true, error: null });
    const state = get();
    const input: CarbonInput = {
      device_id: getOrCreateDeviceId(),
      transport_mode: state.transportMode,
      distance_km: state.distanceKm,
      trips_per_year: state.tripsPerYear,
      electricity_kwh: state.electricityKwh,
      gas_kwh: state.gasKwh,
      diet_type: state.dietType,
      consumption_level: state.consumptionLevel,
    };

    try {
      const result = await calculateFootprint(input);
      set({ result, isLoading: false });
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Calculation failed';
      set({ error: message, isLoading: false });
    }
  },

  fetchHistory: async () => {
    set({ isHistoryLoading: true });
    try {
      const deviceId = getOrCreateDeviceId();
      const history = await getHistory(deviceId);
      set({ history, isHistoryLoading: false });
    } catch {
      set({ history: [], isHistoryLoading: false });
    }
  },

  clearError: () => set({ error: null }),
  clearResult: () => set({ result: null }),
}));
