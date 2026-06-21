/**
 * Single insight card component.
 */

import React from 'react';
import type { Insight } from '../../types';
import { categoryLabel, severityColor } from '../../utils/formatters';

interface InsightCardProps {
  insight: Insight;
  index: number;
}

const SEVERITY_BADGES: Record<string, { bg: string; label: string }> = {
  high: { bg: 'bg-red-500/20 text-red-300', label: 'High Impact' },
  medium: { bg: 'bg-yellow-500/20 text-yellow-300', label: 'Medium Impact' },
  low: { bg: 'bg-green-500/20 text-green-300', label: 'Low Impact' },
};

export const InsightCard: React.FC<InsightCardProps> = ({
  insight,
  index,
}) => {
  const badge = SEVERITY_BADGES[insight.severity] ?? SEVERITY_BADGES.low;

  return (
    <article
      className="animate-slide-up rounded-2xl border border-slate-700/50 bg-slate-800/50 p-6 backdrop-blur transition-all hover:border-slate-600/50 hover:bg-slate-800/70"
      style={{ animationDelay: `${index * 100}ms` }}
      aria-label={`Insight ${index + 1}: ${insight.tip}`}
      id={`insight-card-${index}`}
    >
      <div className="mb-3 flex items-center justify-between">
        <span className={`text-sm font-medium ${severityColor(insight.severity)}`}>
          {categoryLabel(insight.category)}
        </span>
        <span
          className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${badge.bg}`}
        >
          {badge.label}
        </span>
      </div>
      <p className="text-sm leading-relaxed text-slate-300">{insight.tip}</p>
    </article>
  );
};
