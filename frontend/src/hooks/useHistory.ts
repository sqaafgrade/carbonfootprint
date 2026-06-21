/**
 * Hook for fetching and managing calculation history.
 */

import { useEffect } from 'react';
import { useCarbonStore } from '../store/carbonStore';

export function useHistory() {
  const { history, isHistoryLoading, fetchHistory } = useCarbonStore();

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  return {
    history,
    isHistoryLoading,
    refetch: fetchHistory,
  };
}
