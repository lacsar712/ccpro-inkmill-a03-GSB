<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '../lib/api';
  import { refreshUnackedCount } from '../lib/alarms';
  import { alarmLevelLabel } from '../lib/labels';
  import type { Mill, ViscosityAlarmEvent } from '../lib/types';

  let rows: ViscosityAlarmEvent[] = [];
  let mills: Mill[] = [];
  let error = '';

  let filterMillId = '';
  let filterAcked = '';

  async function load() {
    error = '';
    const params = new URLSearchParams();
    if (filterMillId) params.set('millId', filterMillId);
    if (filterAcked !== '') params.set('acked', filterAcked);
    const query = params.toString() ? `?${params.toString()}` : '';
    try {
      rows = await api<ViscosityAlarmEvent[]>(`/viscosity-alarm-events${query}`);
    } catch (e) {
      error = e instanceof Error ? e.message : '加载失败';
    }
  }

  onMount(async () => {
    try {
      mills = await api<Mill[]>('/mills');
    } catch (e) {
      error = e instanceof Error ? e.message : '加载失败';
    }
    await load();
  });

  function millLabel(id: number | null): string {
    if (id == null) return '—';
    const m = mills.find((x) => x.id === id);
    return m ? `${m.millCode} · ${m.pigmentBase}` : `#${id}`;
  }

  async function ack(row: ViscosityAlarmEvent) {
    try {
      await api(`/viscosity-alarm-events/${row.id}/ack`, { method: 'POST' });
      await Promise.all([load(), refreshUnackedCount()]);
    } catch (e) {
      error = e instanceof Error ? e.message : '确认失败';
    }
  }
</script>

<header class="page-head">
  <h1>粘度告警事件</h1>
  <p>取样越界时由后端按 active 规则自动生成；越出区间过半记为严重（critical）</p>
</header>

{#if error}
  <div class="err">{error}</div>
{/if}

<section class="panel">
  <div class="filters">
    <label>研磨机
      <select bind:value={filterMillId} on:change={load}>
        <option value="">全部</option>
        {#each mills as m}
          <option value={String(m.id)}>{m.millCode} · {m.pigmentBase}</option>
        {/each}
      </select>
    </label>
    <label>确认状态
      <select bind:value={filterAcked} on:change={load}>
        <option value="">全部</option>
        <option value="false">未确认</option>
        <option value="true">已确认</option>
      </select>
    </label>
  </div>
</section>

<section class="panel">
  <table class="data-table">
    <thead>
      <tr>
        <th>ID</th>
        <th>级别</th>
        <th>研磨机</th>
        <th>触发时间</th>
        <th>实测 Pa·s</th>
        <th>告警信息</th>
        <th>状态</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      {#each rows as row}
        <tr class:unacked={!row.acked}>
          <td>{row.id}</td>
          <td><span class="badge {row.level}">{alarmLevelLabel[row.level]}</span></td>
          <td>{millLabel(row.millId)}</td>
          <td>{row.triggeredAt}</td>
          <td>{row.viscosityPaS ?? '—'}</td>
          <td>{row.message}</td>
          <td>
            <span class="badge {row.acked ? 'acked' : 'open'}">{row.acked ? '已确认' : '未确认'}</span>
          </td>
          <td class="ops">
            {#if !row.acked}
              <button class="link-btn" on:click={() => ack(row)}>确认</button>
            {:else}
              —
            {/if}
          </td>
        </tr>
      {:else}
        <tr><td colspan="8">暂无告警事件</td></tr>
      {/each}
    </tbody>
  </table>
</section>

<style>
  .filters {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .filters label {
    display: grid;
    gap: 0.3rem;
    font-size: 0.8rem;
    color: var(--steel);
  }

  .filters select {
    border: 1px solid var(--line);
    background: rgba(0, 0, 0, 0.35);
    color: white;
    padding: 0.5rem 0.6rem;
    min-width: 180px;
  }

  tr.unacked {
    background: rgba(192, 57, 43, 0.07);
  }

  .badge.warn {
    border-color: rgba(240, 235, 227, 0.4);
    color: var(--paper);
  }

  .badge.critical {
    border-color: var(--vermillion-500);
    color: var(--vermillion-400);
    background: rgba(231, 76, 60, 0.12);
  }

  .badge.open {
    border-color: var(--vermillion-700);
    color: var(--vermillion-400);
  }

  .badge.acked {
    color: var(--steel);
  }
</style>
