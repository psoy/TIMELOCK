/**
 * React Query hooks for User management
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, User, NotificationPreferences } from '@/lib/api/client';
import { useAuthStore } from '@/lib/store/authStore';

// Query key factory
export const userKeys = {
  all: ['user'] as const,
  me: () => [...userKeys.all, 'me'] as const,
  notifications: () => [...userKeys.all, 'notifications'] as const,
};

// Get current user
export function useMe() {
  const setUser = useAuthStore((state) => state.setUser);
  const clearUser = useAuthStore((state) => state.clearUser);

  return useQuery({
    queryKey: userKeys.me(),
    queryFn: async () => {
      try {
        const user = await apiClient.getMe();
        setUser(user);
        return user;
      } catch (error) {
        clearUser();
        throw error;
      }
    },
    staleTime: 10 * 60 * 1000, // 10 minutes
    retry: 1,
  });
}

// Update user
export function useUpdateUser() {
  const queryClient = useQueryClient();
  const setUser = useAuthStore((state) => state.setUser);

  return useMutation({
    mutationFn: (data: Partial<User>) => apiClient.updateMe(data),
    onSuccess: (data) => {
      queryClient.setQueryData(userKeys.me(), data);
      setUser(data);
    },
  });
}

// Get notification preferences
export function useNotificationPreferences() {
  return useQuery({
    queryKey: userKeys.notifications(),
    queryFn: () => apiClient.getNotificationPreferences(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Update notification preferences
export function useUpdateNotificationPreferences() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<NotificationPreferences>) =>
      apiClient.updateNotificationPreferences(data),
    onMutate: async (newData) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: userKeys.notifications() });

      // Snapshot previous value
      const previousPrefs = queryClient.getQueryData(userKeys.notifications());

      // Optimistically update
      queryClient.setQueryData<NotificationPreferences>(
        userKeys.notifications(),
        (old) => {
          if (!old) return old;
          return { ...old, ...newData };
        }
      );

      return { previousPrefs };
    },
    onError: (_err, _variables, context) => {
      // Rollback on error
      if (context?.previousPrefs) {
        queryClient.setQueryData(userKeys.notifications(), context.previousPrefs);
      }
    },
    onSuccess: (data) => {
      queryClient.setQueryData(userKeys.notifications(), data);
    },
  });
}
