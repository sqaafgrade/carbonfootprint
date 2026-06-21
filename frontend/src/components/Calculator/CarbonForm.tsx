/**
 * Carbon footprint input form.
 *
 * Full label/aria-describedby pairing for screen reader accessibility.
 * Every input has an associated <label> element.
 */

import React from 'react';
import { useCarbonStore } from '../../store/carbonStore';
import { LoadingSpinner } from '../shared/LoadingSpinner';

const TRANSPORT_OPTIONS = [
  { value: 'car_petrol', label: '⛽ Petrol car' },
  { value: 'car_diesel', label: '🛢️ Diesel car' },
  { value: 'car_electric', label: '⚡ Electric car' },
  { value: 'bus', label: '🚌 Bus' },
  { value: 'train', label: '🚆 Train' },
  { value: 'flight_short_haul', label: '✈️ Short-haul flight' },
  { value: 'flight_long_haul', label: '🌍 Long-haul flight' },
] as const;

const DIET_OPTIONS = [
  { value: 'meat_heavy', label: '🥩 Heavy meat eater' },
  { value: 'meat_medium', label: '🍗 Moderate meat' },
  { value: 'vegetarian', label: '🥬 Vegetarian' },
  { value: 'vegan', label: '🌱 Vegan' },
] as const;

const CONSUMPTION_OPTIONS = [
  { value: 'high', label: '🛍️ High consumption' },
  { value: 'medium', label: '📦 Moderate consumption' },
  { value: 'low', label: '♻️ Low consumption' },
] as const;

export const CarbonForm: React.FC = () => {
  const store = useCarbonStore();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    store.calculate();
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-8"
      aria-label="Carbon footprint calculator"
      id="carbon-form"
    >
      {/* Transport Section */}
      <fieldset className="space-y-4">
        <legend className="text-lg font-semibold text-white flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500/20 text-sm">
            🚗
          </span>
          Transport
        </legend>

        <div>
          <label
            htmlFor="transport-mode"
            className="mb-1 block text-sm font-medium text-slate-300"
          >
            Primary transport mode
          </label>
          <select
            id="transport-mode"
            value={store.transportMode}
            onChange={(e) =>
              store.setTransportMode(
                e.target.value as typeof store.transportMode,
              )
            }
            className="w-full rounded-xl border border-slate-600/50 bg-slate-800/50 px-4 py-3 text-white backdrop-blur transition-colors focus:border-carbon-500 focus:outline-none"
            aria-describedby="transport-mode-hint"
          >
            {TRANSPORT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <p id="transport-mode-hint" className="mt-1 text-xs text-slate-400">
            Select your most-used transport method
          </p>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label
              htmlFor="distance-km"
              className="mb-1 block text-sm font-medium text-slate-300"
            >
              Weekly distance (km)
            </label>
            <input
              id="distance-km"
              type="number"
              min={0}
              max={100000}
              step={1}
              value={store.distanceKm}
              onChange={(e) => store.setDistanceKm(Number(e.target.value))}
              className="w-full rounded-xl border border-slate-600/50 bg-slate-800/50 px-4 py-3 text-white backdrop-blur transition-colors focus:border-carbon-500 focus:outline-none"
              aria-describedby="distance-hint"
            />
            <p id="distance-hint" className="mt-1 text-xs text-slate-400">
              0 – 100,000 km
            </p>
          </div>

          <div>
            <label
              htmlFor="trips-year"
              className="mb-1 block text-sm font-medium text-slate-300"
            >
              Trips per year
            </label>
            <input
              id="trips-year"
              type="number"
              min={0}
              max={1000}
              step={1}
              value={store.tripsPerYear}
              onChange={(e) => store.setTripsPerYear(Number(e.target.value))}
              className="w-full rounded-xl border border-slate-600/50 bg-slate-800/50 px-4 py-3 text-white backdrop-blur transition-colors focus:border-carbon-500 focus:outline-none"
              aria-describedby="trips-hint"
            />
            <p id="trips-hint" className="mt-1 text-xs text-slate-400">
              0 – 1,000 trips
            </p>
          </div>
        </div>
      </fieldset>

      {/* Home Energy Section */}
      <fieldset className="space-y-4">
        <legend className="text-lg font-semibold text-white flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500/20 text-sm">
            🏠
          </span>
          Home Energy
        </legend>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label
              htmlFor="electricity-kwh"
              className="mb-1 block text-sm font-medium text-slate-300"
            >
              Monthly electricity (kWh)
            </label>
            <input
              id="electricity-kwh"
              type="number"
              min={0}
              max={10000}
              step={1}
              value={store.electricityKwh}
              onChange={(e) => store.setElectricityKwh(Number(e.target.value))}
              className="w-full rounded-xl border border-slate-600/50 bg-slate-800/50 px-4 py-3 text-white backdrop-blur transition-colors focus:border-carbon-500 focus:outline-none"
              aria-describedby="electricity-hint"
            />
            <p id="electricity-hint" className="mt-1 text-xs text-slate-400">
              0 – 10,000 kWh/month
            </p>
          </div>

          <div>
            <label
              htmlFor="gas-kwh"
              className="mb-1 block text-sm font-medium text-slate-300"
            >
              Monthly gas (kWh)
            </label>
            <input
              id="gas-kwh"
              type="number"
              min={0}
              max={10000}
              step={1}
              value={store.gasKwh}
              onChange={(e) => store.setGasKwh(Number(e.target.value))}
              className="w-full rounded-xl border border-slate-600/50 bg-slate-800/50 px-4 py-3 text-white backdrop-blur transition-colors focus:border-carbon-500 focus:outline-none"
              aria-describedby="gas-hint"
            />
            <p id="gas-hint" className="mt-1 text-xs text-slate-400">
              0 – 10,000 kWh/month
            </p>
          </div>
        </div>
      </fieldset>

      {/* Diet Section */}
      <fieldset className="space-y-4">
        <legend className="text-lg font-semibold text-white flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-green-500/20 text-sm">
            🥗
          </span>
          Diet
        </legend>

        <div>
          <label
            htmlFor="diet-type"
            className="mb-1 block text-sm font-medium text-slate-300"
          >
            Dietary pattern
          </label>
          <select
            id="diet-type"
            value={store.dietType}
            onChange={(e) =>
              store.setDietType(e.target.value as typeof store.dietType)
            }
            className="w-full rounded-xl border border-slate-600/50 bg-slate-800/50 px-4 py-3 text-white backdrop-blur transition-colors focus:border-carbon-500 focus:outline-none"
          >
            {DIET_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </fieldset>

      {/* Consumption Section */}
      <fieldset className="space-y-4">
        <legend className="text-lg font-semibold text-white flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-500/20 text-sm">
            🛍️
          </span>
          Consumption
        </legend>

        <div>
          <label
            htmlFor="consumption-level"
            className="mb-1 block text-sm font-medium text-slate-300"
          >
            Consumption level
          </label>
          <select
            id="consumption-level"
            value={store.consumptionLevel}
            onChange={(e) =>
              store.setConsumptionLevel(
                e.target.value as typeof store.consumptionLevel,
              )
            }
            className="w-full rounded-xl border border-slate-600/50 bg-slate-800/50 px-4 py-3 text-white backdrop-blur transition-colors focus:border-carbon-500 focus:outline-none"
            aria-describedby="consumption-hint"
          >
            {CONSUMPTION_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <p id="consumption-hint" className="mt-1 text-xs text-slate-400">
            Shopping, electronics, clothing, etc.
          </p>
        </div>
      </fieldset>

      {/* Error display */}
      {store.error && (
        <div
          role="alert"
          className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300"
          id="form-error"
        >
          <strong>Error:</strong> {store.error}
          <button
            type="button"
            onClick={store.clearError}
            className="ml-3 text-red-400 underline hover:text-red-300"
            aria-label="Dismiss error"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Submit */}
      <button
        type="submit"
        disabled={store.isLoading}
        className="w-full rounded-2xl bg-gradient-to-r from-carbon-600 to-carbon-500 px-8 py-4 text-lg font-bold text-white shadow-lg shadow-carbon-500/25 transition-all hover:from-carbon-500 hover:to-carbon-400 hover:shadow-xl hover:shadow-carbon-500/30 disabled:cursor-not-allowed disabled:opacity-50"
        id="calculate-button"
      >
        {store.isLoading ? (
          <LoadingSpinner size="sm" label="Calculating..." />
        ) : (
          '🌍 Calculate My Footprint'
        )}
      </button>
    </form>
  );
};
