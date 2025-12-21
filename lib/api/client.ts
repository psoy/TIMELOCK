/**
 * API Client for TIMELOCK Backend
 * Handles all HTTP requests with automatic JWT token management
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface TokenResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface User {
  id: number;
  email: string;
  username: string;
  oauth_provider?: string;
  profile_image?: string;
  timezone?: string;
  is_premium?: boolean;
  premium_expires_at?: string;
}

export interface DailyPlan {
  id: number;
  date: string;
  priorities: string[];
  brain_dump: string;
  completion_rate: number;
  time_blocks: TimeBlock[];
}

export interface TimeBlock {
  id: number;
  period: 'am' | 'pm';
  hour: number;
  title: string;
  description?: string;
  category?: string;
  planned_duration: number;
  actual_duration?: number;
  is_completed: boolean;
}

export interface TimerSession {
  id: number;
  scheduled_duration: number;
  elapsed_time: number;
  status: 'running' | 'paused' | 'completed' | 'cancelled';
  started_at: string;
  paused_at?: string;
  completed_at?: string;
}

export interface DailyStats {
  date: string;
  total_focus_time: number;
  total_blocks: number;
  completed_blocks: number;
  block_completion_rate: number;
  execution_rate: number;
  category_breakdown: Record<string, number>;
  hourly_breakdown: Array<{
    hour: number;
    focus_time: number;
    blocks: number;
  }>;
}

export interface WeeklyStats {
  start_date: string;
  end_date: string;
  total_focus_time: number;
  average_daily_focus: number;
  total_blocks: number;
  completed_blocks: number;
  block_completion_rate: number;
  execution_rate: number;
  daily_breakdown: Array<{
    date: string;
    focus_time: number;
    blocks: number;
    completed_blocks: number;
  }>;
  category_breakdown: Record<string, number>;
}

export interface MonthlyStats {
  year: number;
  month: number;
  total_focus_time: number;
  average_daily_focus: number;
  total_blocks: number;
  completed_blocks: number;
  block_completion_rate: number;
  execution_rate: number;
  weekly_breakdown: Array<{
    week_start: string;
    week_end: string;
    focus_time: number;
    blocks: number;
  }>;
  category_breakdown: Record<string, number>;
  most_productive_day?: string;
  most_productive_hour?: number;
}

export interface NotificationPreferences {
  sound_enabled: boolean;
  screen_flash_enabled: boolean;
  vibration_enabled: boolean;
  device_flash_enabled: boolean;
  flash_pattern?: {
    duration?: number;
    interval?: number;
    repetitions?: number;
  };
}

class APIClient {
  private axiosInstance: AxiosInstance;
  private refreshPromise: Promise<string> | null = null;

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor - add JWT token
    this.axiosInstance.interceptors.request.use(
      (config) => {
        const token = this.getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - handle token refresh
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as any;

        // If error is 401 and we haven't tried to refresh yet
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const newAccessToken = await this.refreshAccessToken();

            if (newAccessToken && originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
              return this.axiosInstance(originalRequest);
            }
          } catch (refreshError) {
            // Refresh failed, clear tokens and redirect to login
            this.clearTokens();
            if (typeof window !== 'undefined') {
              window.location.href = '/login';
            }
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Token Management
  private getAccessToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('access_token');
  }

  private getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('refresh_token');
  }

  private setTokens(access: string, refresh: string): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
  }

  private clearTokens(): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  private async refreshAccessToken(): Promise<string | null> {
    // Prevent multiple simultaneous refresh requests
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = (async () => {
      try {
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        const response = await axios.post(`${API_BASE_URL}/api/auth/token/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        if (typeof window !== 'undefined') {
          localStorage.setItem('access_token', access);
        }

        return access;
      } finally {
        this.refreshPromise = null;
      }
    })();

    return this.refreshPromise;
  }

  // Authentication
  async loginWithGoogle(idToken: string): Promise<TokenResponse> {
    const response = await this.axiosInstance.post<TokenResponse>('/api/auth/google/', {
      id_token: idToken,
    });
    this.setTokens(response.data.access, response.data.refresh);
    return response.data;
  }

  async loginWithKakao(accessToken: string): Promise<TokenResponse> {
    const response = await this.axiosInstance.post<TokenResponse>('/api/auth/kakao/', {
      access_token: accessToken,
    });
    this.setTokens(response.data.access, response.data.refresh);
    return response.data;
  }

  async logout(): Promise<void> {
    this.clearTokens();
  }

  // User
  async getMe(): Promise<User> {
    const response = await this.axiosInstance.get<User>('/api/auth/me/');
    return response.data;
  }

  async updateMe(data: Partial<User>): Promise<User> {
    const response = await this.axiosInstance.patch<User>('/api/auth/me/', data);
    return response.data;
  }

  async getNotificationPreferences(): Promise<NotificationPreferences> {
    const response = await this.axiosInstance.get<NotificationPreferences>(
      '/api/auth/me/notifications/'
    );
    return response.data;
  }

  async updateNotificationPreferences(
    data: Partial<NotificationPreferences>
  ): Promise<NotificationPreferences> {
    const response = await this.axiosInstance.patch<NotificationPreferences>(
      '/api/auth/me/notifications/',
      data
    );
    return response.data;
  }

  // Daily Plans
  async getDailyPlan(date: string): Promise<DailyPlan | null> {
    try {
      const response = await this.axiosInstance.get<DailyPlan[]>('/api/plans/', {
        params: { date },
      });
      return response.data[0] || null;
    } catch (error) {
      if ((error as AxiosError).response?.status === 404) {
        return null;
      }
      throw error;
    }
  }

  async createDailyPlan(data: {
    date: string;
    priorities?: string[];
    brain_dump?: string;
  }): Promise<DailyPlan> {
    const response = await this.axiosInstance.post<DailyPlan>('/api/plans/', data);
    return response.data;
  }

  async updateDailyPlan(
    id: number,
    data: Partial<{
      priorities: string[];
      brain_dump: string;
      time_blocks: Partial<TimeBlock>[];
    }>
  ): Promise<DailyPlan> {
    const response = await this.axiosInstance.patch<DailyPlan>(`/api/plans/${id}/`, data);
    return response.data;
  }

  async deleteDailyPlan(id: number): Promise<void> {
    await this.axiosInstance.delete(`/api/plans/${id}/`);
  }

  // Timer Sessions
  async startTimer(data: {
    time_block_id?: number;
    scheduled_duration: number;
  }): Promise<TimerSession> {
    const response = await this.axiosInstance.post<TimerSession>('/api/timer-sessions/', data);
    return response.data;
  }

  async updateTimer(
    id: number,
    data: {
      elapsed_time?: number;
      status?: 'running' | 'paused' | 'completed' | 'cancelled';
    }
  ): Promise<TimerSession> {
    const response = await this.axiosInstance.patch<TimerSession>(
      `/api/timer-sessions/${id}/`,
      data
    );
    return response.data;
  }

  async getTimerSessions(date?: string): Promise<TimerSession[]> {
    const response = await this.axiosInstance.get<TimerSession[]>('/api/timer-sessions/', {
      params: date ? { date } : undefined,
    });
    return response.data;
  }

  // Statistics
  async getDailyStats(date: string): Promise<DailyStats> {
    const response = await this.axiosInstance.get<DailyStats>('/api/stats/daily/', {
      params: { date },
    });
    return response.data;
  }

  async getWeeklyStats(startDate?: string): Promise<WeeklyStats> {
    const response = await this.axiosInstance.get<WeeklyStats>('/api/stats/weekly/', {
      params: startDate ? { start_date: startDate } : undefined,
    });
    return response.data;
  }

  async getMonthlyStats(year?: number, month?: number): Promise<MonthlyStats> {
    const response = await this.axiosInstance.get<MonthlyStats>('/api/stats/monthly/', {
      params: { year, month },
    });
    return response.data;
  }

  getHeatmapUrl(year?: number): string {
    const params = year ? `?year=${year}` : '';
    const token = this.getAccessToken();
    return `${API_BASE_URL}/api/stats/heatmap/${params}${
      params ? '&' : '?'
    }token=${token}`;
  }
}

// Export singleton instance
export const apiClient = new APIClient();
