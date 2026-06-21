/**
 * Hook for accessing insights from the latest calculation result.
 */

import { useCarbonStore } from '../store/carbonStore';

export function useInsights() {
  const result = useCarbonStore((state) => state.result);

  return {
    insights: result?.insights ?? [],
    source: result?.source ?? 'rules',
    hasInsights: (result?.insights?.length ?? 0) > 0,
  };
}
