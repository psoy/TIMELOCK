/**
 * React Query hooks for Timer Session management
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, TimerSession } from '@/lib/api/client';

// Query key factory
export const timerKeys = {
  all: ['timer-sessions'] as const,
  byDate: (date: string) => [...timerKeys.all, date] as const,
};

// Get timer sessions
export function useTimerSessions(date?: string) {
  return useQuery({
    queryKey: date ? timerKeys.byDate(date) : timerKeys.all,
    queryFn: () => apiClient.getTimerSessions(date),
    staleTime: 1 * 60 * 1000, // 1 minute
  });
}

// Start timer
export function useStartTimer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { time_block_id?: number; scheduled_duration: number }) =>
      apiClient.startTimer(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: timerKeys.all });
    },
  });
}

// Update timer
export function useUpdateTimer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: number;
      data: {
        elapsed_time?: number;
        status?: 'running' | 'paused' | 'completed' | 'cancelled';
      };
    }) => apiClient.updateTimer(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: timerKeys.all });
    },
  });
}
