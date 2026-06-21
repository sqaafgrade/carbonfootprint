/**
 * Hook for carbon footprint calculation.
 */

import { useCarbonStore } from '../store/carbonStore';

export function useCarbon() {
  const {
    result,
    isLoading,
    error,
    calculate,
    clearError,
    clearResult,
  } = useCarbonStore();

  return {
    result,
    isLoading,
    error,
    calculate,
    clearError,
    clearResult,
  };
}
