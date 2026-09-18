import { writable } from 'svelte/store';

export type PageId =
  | 'dashboard'
  | 'workshops'
  | 'mills'
  | 'samples'
  | 'passes'
  | 'alarm-rules'
  | 'alarm-events';

export const page = writable<PageId>('dashboard');
