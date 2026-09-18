import type { AlarmLevel, MillStatus } from './types';

export const millStatusLabel: Record<MillStatus, string> = {
  grinding: '研磨中',
  idle: '待机',
  wash: '清洗',
};

export const alarmLevelLabel: Record<AlarmLevel, string> = {
  warn: '警告',
  critical: '严重',
};
