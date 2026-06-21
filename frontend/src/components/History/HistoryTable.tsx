/**
 * History table showing past calculations.
 */

import React from 'react';
import type { HistoryEntry } from '../../types';
import { formatDate, formatKg } from '../../utils/formatters';

interface HistoryTableProps {
  entries: HistoryEntry[];
}

export const HistoryTable: React.FC<HistoryTableProps> = ({ entries }) => {
  if (entries.length === 0) {
    return (
      <div className="rounded-2xl border border-slate-700/50 bg-slate-800/50 p-8 text-center backdrop-blur">
        <p className="text-slate-400">
          No history yet. Calculate your first footprint to get started!
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-700/50 bg-slate-800/50 backdrop-blur">
      <table
        className="w-full text-left text-sm"
        role="table"
        aria-label="Calculation history"
        id="history-table"
      >
        <thead>
          <tr className="border-b border-slate-700/50 bg-slate-800/80">
            <th scope="col" className="px-6 py-4 font-medium text-slate-300">
              Date
            </th>
            <th scope="col" className="px-6 py-4 font-medium text-slate-300">
              Total
            </th>
            <th scope="col" className="hidden px-6 py-4 font-medium text-slate-300 sm:table-cell">
              Transport
            </th>
            <th scope="col" className="hidden px-6 py-4 font-medium text-slate-300 md:table-cell">
              Home
            </th>
            <th scope="col" className="hidden px-6 py-4 font-medium text-slate-300 lg:table-cell">
              Source
            </th>
          </tr>
        </thead>
        <tbody>
          {entries.map((entry) => (
            <tr
              key={entry.id}
              className="border-b border-slate-700/30 transition-colors hover:bg-slate-700/20"
            >
              <td className="px-6 py-4 text-slate-300">
                {formatDate(entry.created_at)}
              </td>
              <td className="px-6 py-4 font-medium text-white">
                {formatKg(entry.total_kg)}
              </td>
              <td className="hidden px-6 py-4 text-slate-400 sm:table-cell">
                {formatKg(entry.breakdown?.transport ?? 0)}
              </td>
              <td className="hidden px-6 py-4 text-slate-400 md:table-cell">
                {formatKg(entry.breakdown?.home ?? 0)}
              </td>
              <td className="hidden px-6 py-4 lg:table-cell">
                <span
                  className={`rounded-full px-2 py-0.5 text-xs ${
                    entry.insights_source === 'gemini'
                      ? 'bg-blue-500/20 text-blue-300'
                      : 'bg-slate-700 text-slate-400'
                  }`}
                >
                  {entry.insights_source}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
