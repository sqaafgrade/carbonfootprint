/**
 * Category chart using Recharts with a data-table fallback for screen readers.
 *
 * The chart is decorative for screen readers; a visually-hidden data table
 * provides the same information in an accessible format.
 */

import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';
import type { CategoryBreakdown } from '../../types';
import { formatKg } from '../../utils/formatters';

interface CategoryChartProps {
  breakdown: CategoryBreakdown;
}

const COLORS = ['#3b82f6', '#f59e0b', '#22c55e', '#a855f7'];
const CATEGORIES = [
  { key: 'transport', label: 'Transport' },
  { key: 'home', label: 'Home Energy' },
  { key: 'diet', label: 'Diet' },
  { key: 'consumption', label: 'Consumption' },
] as const;

export const CategoryChart: React.FC<CategoryChartProps> = ({ breakdown }) => {
  const data = CATEGORIES.map((cat, idx) => ({
    name: cat.label,
    value: breakdown[cat.key],
    color: COLORS[idx],
  }));

  const total = Object.values(breakdown).reduce((sum, v) => sum + v, 0);

  return (
    <div className="rounded-2xl border border-slate-700/50 bg-slate-800/50 p-6 backdrop-blur">
      <h3 className="mb-4 text-lg font-semibold text-white">
        Emissions Distribution
      </h3>

      {/* Visual chart — hidden from screen readers */}
      <div aria-hidden="true" className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={90}
              paddingAngle={4}
              dataKey="value"
              stroke="none"
            >
              {data.map((entry, index) => (
                <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              formatter={(value: number) => formatKg(value)}
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #334155',
                borderRadius: '12px',
                color: '#e2e8f0',
              }}
            />
            <Legend
              formatter={(value: string) => (
                <span className="text-sm text-slate-300">{value}</span>
              )}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Screen-reader accessible data table */}
      <table className="sr-only" role="table" aria-label="Emissions breakdown by category">
        <caption>Carbon emissions breakdown</caption>
        <thead>
          <tr>
            <th scope="col">Category</th>
            <th scope="col">Emissions (kg CO₂e)</th>
            <th scope="col">Percentage</th>
          </tr>
        </thead>
        <tbody>
          {CATEGORIES.map((cat) => {
            const value = breakdown[cat.key];
            const pct = total > 0 ? ((value / total) * 100).toFixed(1) : '0.0';
            return (
              <tr key={cat.key}>
                <td>{cat.label}</td>
                <td>{Math.round(value)}</td>
                <td>{pct}%</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
