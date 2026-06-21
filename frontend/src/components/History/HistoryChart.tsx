/**
 * History chart showing carbon footprint trends over time.
 */

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import type { HistoryEntry } from '../../types';
import { formatDate } from '../../utils/formatters';

interface HistoryChartProps {
  entries: HistoryEntry[];
}

export const HistoryChart: React.FC<HistoryChartProps> = ({ entries }) => {
  if (entries.length === 0) {
    return null;
  }

  const data = [...entries]
    .reverse()
    .map((entry) => ({
      date: formatDate(entry.created_at),
      total: Math.round(entry.total_kg),
    }));

  return (
    <div className="rounded-2xl border border-slate-700/50 bg-slate-800/50 p-6 backdrop-blur">
      <h3 className="mb-4 text-lg font-semibold text-white">
        📈 Footprint Trend
      </h3>
      <div className="h-56" aria-hidden="true">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis
              dataKey="date"
              stroke="#cbd5e1"
              tick={{ fontSize: 12 }}
            />
            <YAxis
              stroke="#cbd5e1"
              tick={{ fontSize: 12 }}
              tickFormatter={(v: number) => `${v} kg`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #334155',
                borderRadius: '12px',
                color: '#e2e8f0',
              }}
              formatter={(value: number) => [`${value} kg CO₂e`, 'Total']}
            />
            <Line
              type="monotone"
              dataKey="total"
              stroke="#22c55e"
              strokeWidth={3}
              dot={{ fill: '#22c55e', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: '#fff', strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      {/* Screen reader accessible description */}
      <p className="sr-only">
        Line chart showing {data.length} carbon footprint calculations over time,
        ranging from {data[0]?.total ?? 0} to {data[data.length - 1]?.total ?? 0} kg CO₂e.
      </p>
    </div>
  );
};
