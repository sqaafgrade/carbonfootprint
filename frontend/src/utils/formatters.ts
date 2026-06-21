/**
 * Formatting utilities for display values.
 */

/**
 * Format kg to a human-readable string with unit.
 */
export function formatKg(kg: number): string {
  if (kg >= 1000) {
    return `${(kg / 1000).toFixed(1)} tonnes`;
  }
  return `${Math.round(kg)} kg`;
}

/**
 * Format a percentage with sign indicator.
 */
export function formatPercentage(pct: number): string {
  const sign = pct >= 0 ? '+' : '';
  return `${sign}${pct.toFixed(1)}%`;
}

/**
 * Format an ISO date string to a locale-friendly display.
 */
export function formatDate(isoString: string): string {
  try {
    return new Date(isoString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return isoString;
  }
}

/**
 * Map category keys to display labels.
 */
export function categoryLabel(category: string): string {
  const labels: Record<string, string> = {
    transport: '🚗 Transport',
    home: '🏠 Home Energy',
    diet: '🥩 Diet',
    consumption: '🛍️ Consumption',
    general: '🌍 General',
  };
  return labels[category] ?? category;
}

/**
 * Map severity to color class names.
 */
export function severityColor(severity: string): string {
  switch (severity) {
    case 'high':
      return 'text-red-400';
    case 'medium':
      return 'text-yellow-400';
    case 'low':
      return 'text-green-400';
    default:
      return 'text-slate-400';
  }
}
