/**
 * Results display for carbon footprint calculation.
 *
 * Shows total emissions, comparison vs global average / Paris target,
 * and per-category breakdown with visual indicators.
 */

import React from 'react';
import { formatKg, formatPercentage } from '../../utils/formatters';
import type { CarbonResult } from '../../types';

interface ResultsDisplayProps {
  result: CarbonResult;
}

export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ result }) => {
  const isAboveGlobal = result.vs_global_average_pct > 0;
  const isAboveParis = result.vs_paris_target_pct > 0;

  return (
    <section
      className="animate-fade-in space-y-6"
      aria-label="Calculation results"
      id="results-display"
    >
      {/* Total emissions hero */}
      <div className="rounded-2xl border border-slate-700/50 bg-gradient-to-br from-slate-800/80 to-slate-900/80 p-8 text-center backdrop-blur">
        <p className="mb-2 text-sm font-medium uppercase tracking-wider text-slate-300">
          Your Annual Carbon Footprint
        </p>
        <p className="text-5xl font-extrabold text-white" id="total-emissions">
          {formatKg(result.total_kg)}
        </p>
        <p className="mt-1 text-sm text-slate-300">CO₂ equivalent per year</p>
      </div>

      {/* Comparison cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div
          className={`rounded-2xl border p-6 backdrop-blur transition-colors ${
            isAboveGlobal
              ? 'border-red-500/30 bg-red-500/5'
              : 'border-carbon-500/30 bg-carbon-500/5'
          }`}
          id="vs-global"
        >
          <p className="mb-1 text-xs font-medium uppercase tracking-wider text-slate-300">
            vs Global Average
          </p>
          <p
            className={`text-2xl font-bold ${
              isAboveGlobal ? 'text-red-400' : 'text-carbon-400'
            }`}
          >
            {formatPercentage(result.vs_global_average_pct)}
          </p>
          <p className="mt-1 text-xs text-slate-300">
            {isAboveGlobal ? 'Above' : 'Below'} the 4,000 kg global average
          </p>
        </div>

        <div
          className={`rounded-2xl border p-6 backdrop-blur transition-colors ${
            isAboveParis
              ? 'border-amber-500/30 bg-amber-500/5'
              : 'border-carbon-500/30 bg-carbon-500/5'
          }`}
          id="vs-paris"
        >
          <p className="mb-1 text-xs font-medium uppercase tracking-wider text-slate-300">
            vs Paris Target
          </p>
          <p
            className={`text-2xl font-bold ${
              isAboveParis ? 'text-amber-400' : 'text-carbon-400'
            }`}
          >
            {formatPercentage(result.vs_paris_target_pct)}
          </p>
          <p className="mt-1 text-xs text-slate-300">
            {isAboveParis ? 'Above' : 'Below'} the 2,000 kg Paris target
          </p>
        </div>
      </div>

      {/* Category breakdown bars */}
      <div className="rounded-2xl border border-slate-700/50 bg-slate-800/50 p-6 backdrop-blur">
        <h3 className="mb-4 text-lg font-semibold text-white">
          Breakdown by Category
        </h3>
        <div className="space-y-4" role="list" aria-label="Emission categories">
          {result.ranked_categories.map((cat) => {
            const pct =
              result.total_kg > 0
                ? (cat.kg / result.total_kg) * 100
                : 0;
            const colors: Record<string, string> = {
              transport: 'bg-blue-500',
              home: 'bg-amber-500',
              diet: 'bg-green-500',
              consumption: 'bg-purple-500',
            };
            return (
              <div key={cat.category} role="listitem">
                <div className="mb-1 flex justify-between text-sm">
                  <span className="font-medium capitalize text-slate-300">
                    {cat.category}
                  </span>
                  <span className="text-slate-300">
                    {formatKg(cat.kg)} ({pct.toFixed(1)}%)
                  </span>
                </div>
                <div
                  className="h-3 overflow-hidden rounded-full bg-slate-700"
                  role="progressbar"
                  aria-valuenow={Math.round(pct)}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label={`${cat.category}: ${pct.toFixed(1)}%`}
                >
                  <div
                    className={`h-full rounded-full transition-all duration-700 ease-out ${
                      colors[cat.category] ?? 'bg-slate-500'
                    }`}
                    style={{ width: `${Math.max(pct, 2)}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Source badge */}
      <div className="text-center">
        <span
          className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-medium ${
            result.source === 'gemini'
              ? 'bg-blue-500/20 text-blue-300'
              : 'bg-slate-700 text-slate-300'
          }`}
        >
          {result.source === 'gemini' ? '✨ AI-powered insights' : '📊 Rule-based insights'}
        </span>
      </div>
    </section>
  );
};
