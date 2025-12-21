/**
 * React Query hooks for Statistics
 */

import { useQuery } from '@tanstack/react-query';
import { apiClient, DailyStats, WeeklyStats, MonthlyStats } from '@/lib/api/client';

// Query key factory
export const statsKeys = {
  all: ['stats'] as const,
  daily: (date: string) => [...statsKeys.all, 'daily', date] as const,
  weekly: (startDate: string) => [...statsKeys.all, 'weekly', startDate] as const,
  monthly: (year: number, month: number) => [...statsKeys.all, 'monthly', year, month] as const,
};

// Get daily statistics
export function useDailyStats(date: string) {
  return useQuery({
    queryKey: statsKeys.daily(date),
    queryFn: () => apiClient.getDailyStats(date),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

// Get weekly statistics
export function useWeeklyStats(startDate?: string) {
  const key = startDate || new Date().toISOString().split('T')[0];

  return useQuery({
    queryKey: statsKeys.weekly(key),
    queryFn: () => apiClient.getWeeklyStats(startDate),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Get monthly statistics
export function useMonthlyStats(year?: number, month?: number) {
  const now = new Date();
  const targetYear = year || now.getFullYear();
  const targetMonth = month || now.getMonth() + 1;

  return useQuery({
    queryKey: statsKeys.monthly(targetYear, targetMonth),
    queryFn: () => apiClient.getMonthlyStats(targetYear, targetMonth),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Get heatmap URL (not a query, just a helper)
export function useHeatmapUrl(year?: number): string {
  return apiClient.getHeatmapUrl(year);
}
