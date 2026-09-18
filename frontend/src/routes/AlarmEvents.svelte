<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '../lib/api';
  import { alarmLevelLabel } from '../lib/labels';
  import { refreshUnackedAlarms } from '../lib/alarms';
  import type { Mill, ViscosityAlarmEvent } from '../lib/types';

  let rows: ViscosityAlarmEvent[] = [];
  let mills: Mill[] = [];
  let error = '';
  let filterMillId = '';
  let filterAcked = '';

  async function load() {
    error = '';
    try {
      const params = new URLSearchParams();
      if (filterMillId) params.set('millId', filterMillId);
      if (filterAcked) params.set('acked', filterAcked);
      const qs = params.toString();
      [rows, mills] = await Promise.all([
        api<ViscosityAlarmEvent[]>(`/viscosity-alarm-events${qs ? `?${qs}` : ''}`),
        mills.length ? Promise.resolve(mills) : api<Mill[]>('/mills'),
      ]);
    } catch (e) {
      error = e instanceof Error ? e.message : '加载失败';
    }
  }

  onMount(load);

  function millLabel(id: number | null): string {
    if (id == null) return '—';
    const m = mills.find((x) => x.id === id);
    return m ? `${m.millCode} (#${m.id})` : `#${id}`;
  }

  async function ack(id: number) {
    try {
      await api(`/viscosity-alarm-events/${id}/ack`, { method: 'POST' });
      await load();
      await refreshUnackedAlarms();
    } catch (e) {
      error = e instanceof Error ? e.message : '确认失败';
    }
  }
</script>

<header class="page-head">
  <h1>粘度告警事件</h1>
  <p>取样越界自动生成的告警记录，可按研磨机与确认状态筛选</p>
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
          <option value={String(m.id)}>{m.millCode}</option>
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

  <table class="data-table">
    <thead>
      <tr>
        <th>ID</th>
        <th>研磨机</th>
        <th>级别</th>
        <th>告警内容</th>
        <th>取样 ID</th>
        <th>触发时间</th>
        <th>状态</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      {#each rows as row}
        <tr>
          <td>{row.id}</td>
          <td>{millLabel(row.millId)}</td>
          <td><span class="badge {row.level}">{alarmLevelLabel[row.level]}</span></td>
          <td>{row.message}</td>
          <td>{row.sampleId}</td>
          <td>{row.triggeredAt}</td>
          <td>{row.acked ? '已确认' : '未确认'}</td>
          <td class="ops">
            {#if !row.acked}
              <button class="link-btn" on:click={() => ack(row.id)}>确认</button>
            {/if}
          </td>
        </tr>
      {:else}
        <tr><td colspan="8">暂无数据</td></tr>
      {/each}
    </tbody>
  </table>
</section>

<style>
  .filters {
    display: flex;
    gap: 1rem;
    margin-bottom: 0.9rem;
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
    padding: 0.45rem 0.6rem;
    min-width: 10rem;
  }
</style>
