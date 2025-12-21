/**
 * React Query hooks for Daily Plan management
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, DailyPlan, TimeBlock } from '@/lib/api/client';

// Query key factory
export const dailyPlanKeys = {
  all: ['daily-plans'] as const,
  byDate: (date: string) => [...dailyPlanKeys.all, date] as const,
};

// Get daily plan
export function useDailyPlan(date: string) {
  return useQuery({
    queryKey: dailyPlanKeys.byDate(date),
    queryFn: () => apiClient.getDailyPlan(date),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Create daily plan
export function useCreateDailyPlan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { date: string; priorities?: string[]; brain_dump?: string }) =>
      apiClient.createDailyPlan(data),
    onSuccess: (data) => {
      queryClient.setQueryData(dailyPlanKeys.byDate(data.date), data);
      queryClient.invalidateQueries({ queryKey: dailyPlanKeys.all });
    },
  });
}

// Update daily plan
export function useUpdateDailyPlan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: number;
      data: Partial<{
        priorities: string[];
        brain_dump: string;
        time_blocks: Partial<TimeBlock>[];
      }>;
    }) => apiClient.updateDailyPlan(id, data),
    onSuccess: (data) => {
      queryClient.setQueryData(dailyPlanKeys.byDate(data.date), data);
      queryClient.invalidateQueries({ queryKey: dailyPlanKeys.all });
    },
  });
}

// Delete daily plan
export function useDeleteDailyPlan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => apiClient.deleteDailyPlan(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: dailyPlanKeys.all });
    },
  });
}
