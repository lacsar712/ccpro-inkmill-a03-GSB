import { writable } from 'svelte/store';
import { api } from './api';
import type { DashboardStats } from './types';

/** 未确认粘度告警数，由仪表盘/告警事件页刷新，侧栏角标订阅。 */
export const unackedAlarms = writable(0);

export async function refreshUnackedAlarms(): Promise<void> {
  try {
    const stats = await api<DashboardStats>('/dashboard');
    unackedAlarms.set(stats.unackedAlarms);
  } catch {
    // 忽略角标刷新失败，不打断页面
  }
}
