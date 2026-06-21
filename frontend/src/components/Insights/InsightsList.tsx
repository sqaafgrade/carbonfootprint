/**
 * Insights list with aria-live for screen reader announcements.
 *
 * When new insights are loaded, screen readers announce the update.
 */

import React from 'react';
import type { Insight } from '../../types';
import { InsightCard } from './InsightCard';

interface InsightsListProps {
  insights: Insight[];
  source: 'gemini' | 'rules';
}

export const InsightsList: React.FC<InsightsListProps> = ({
  insights,
  source,
}) => {
  if (insights.length === 0) {
    return null;
  }

  return (
    <section
      aria-label="Carbon reduction insights"
      aria-live="polite"
      aria-atomic="true"
      className="space-y-4"
      id="insights-section"
    >
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-white">
          💡 Reduction Insights
        </h2>
        <span
          className={`rounded-full px-3 py-1 text-xs font-medium ${
            source === 'gemini'
              ? 'bg-blue-500/20 text-blue-300'
              : 'bg-slate-700 text-slate-200'
          }`}
        >
          {source === 'gemini' ? '✨ AI-Powered' : '📊 Rule-Based'}
        </span>
      </div>
      <div className="grid gap-4 sm:grid-cols-1 lg:grid-cols-3">
        {insights.map((insight, index) => (
          <InsightCard key={`${insight.category}-${index}`} insight={insight} index={index} />
        ))}
      </div>
    </section>
  );
};
