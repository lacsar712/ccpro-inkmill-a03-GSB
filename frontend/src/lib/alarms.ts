import { writable } from 'svelte/store';
import { api } from './api';
import type { ViscosityAlarmEvent } from './types';

/** 未确认告警条数 —— 始终来自后端 /viscosity-alarm-events，前端不生成假告警。 */
export const unackedAlarmCount = writable(0);

export async function refreshUnackedCount(): Promise<void> {
  try {
    const rows = await api<ViscosityAlarmEvent[]>('/viscosity-alarm-events?acked=false');
    unackedAlarmCount.set(Array.isArray(rows) ? rows.length : 0);
  } catch {
    // 计数刷新失败不阻断页面操作
  }
}
