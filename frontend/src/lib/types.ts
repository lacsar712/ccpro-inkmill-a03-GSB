export type UserRole = 'admin' | 'grinder';

export interface AuthUser {
  id: number;
  username: string;
  displayName: string;
  role: UserRole | string;
}

export interface Workshop {
  id: number;
  name: string;
  site: string | null;
  notes: string | null;
}

export type MillStatus = 'grinding' | 'idle' | 'wash';

export interface Mill {
  id: number;
  workshopId: number;
  millCode: string;
  pigmentBase: string;
  bowlLiters: number;
  status: MillStatus;
}

export interface ViscositySample {
  id: number;
  millId: number;
  sampledAt: string;
  viscosityPaS: number;
  tempC: number | null;
  notes: string | null;
}

export interface GrindPass {
  id: number;
  millId: number;
  startedAt: string;
  passNo: number;
  durationMin: number;
  mediaType: string;
  operatorName: string;
}

export interface ViscosityAlarmRule {
  id: number;
  millId: number;
  minPaS: number;
  maxPaS: number;
  active: boolean;
}

export type AlarmLevel = 'warn' | 'critical';

export interface ViscosityAlarmEvent {
  id: number;
  ruleId: number;
  sampleId: number;
  millId: number | null;
  triggeredAt: string;
  level: AlarmLevel;
  message: string;
  acked: boolean;
  viscosityPaS: number | null;
}

export interface DashboardStats {
  workshopTotal: number;
  grindingMillCount: number;
  samplesLast24h: number;
  passesLast7d: number;
  unackedAlarmCount: number;
}
