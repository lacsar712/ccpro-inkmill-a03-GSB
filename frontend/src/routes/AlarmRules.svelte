<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '../lib/api';
  import type { Mill, ViscosityAlarmRule } from '../lib/types';

  let rows: ViscosityAlarmRule[] = [];
  let mills: Mill[] = [];
  let error = '';
  let editingId: number | null = null;

  let form = {
    millId: '',
    minPaS: '10',
    maxPaS: '14',
    active: true,
  };

  async function load() {
    error = '';
    try {
      [rows, mills] = await Promise.all([
        api<ViscosityAlarmRule[]>('/viscosity-alarm-rules'),
        api<Mill[]>('/mills'),
      ]);
      if (!form.millId && mills[0]) form.millId = String(mills[0].id);
    } catch (e) {
      error = e instanceof Error ? e.message : '加载失败';
    }
  }

  onMount(load);

  function millLabel(id: number): string {
    const m = mills.find((x) => x.id === id);
    return m ? `${m.millCode} · ${m.pigmentBase}` : `#${id}`;
  }

  function reset() {
    form = {
      millId: mills[0] ? String(mills[0].id) : '',
      minPaS: '10',
      maxPaS: '14',
      active: true,
    };
    editingId = null;
  }

  function edit(row: ViscosityAlarmRule) {
    editingId = row.id;
    form = {
      millId: String(row.millId),
      minPaS: String(row.minPaS),
      maxPaS: String(row.maxPaS),
      active: row.active,
    };
  }

  async function save() {
    error = '';
    const minPaS = Number(form.minPaS);
    const maxPaS = Number(form.maxPaS);
    if (!Number.isFinite(minPaS) || !Number.isFinite(maxPaS)) {
      error = '上下限必须为数字';
      return;
    }
    if (minPaS <= 0 || maxPaS <= 0) {
      error = '粘度上下限必须大于 0';
      return;
    }
    if (minPaS >= maxPaS) {
      error = '下限必须小于上限';
      return;
    }
    const payload = {
      millId: Number(form.millId),
      minPaS,
      maxPaS,
      active: form.active,
    };
    try {
      if (editingId) {
        await api(`/viscosity-alarm-rules/${editingId}`, {
          method: 'PUT',
          body: JSON.stringify(payload),
        });
      } else {
        await api('/viscosity-alarm-rules', { method: 'POST', body: JSON.stringify(payload) });
      }
      reset();
      await load();
    } catch (e) {
      error = e instanceof Error ? e.message : '保存失败';
    }
  }

  async function remove(id: number) {
    if (!confirm('确认删除该告警规则？其历史告警事件将一并删除。')) return;
    try {
      await api(`/viscosity-alarm-rules/${id}`, { method: 'DELETE' });
      await load();
    } catch (e) {
      error = e instanceof Error ? e.message : '删除失败';
    }
  }
</script>

<header class="page-head">
  <h1>粘度告警规则</h1>
  <p>规则挂在研磨机上；取样粘度越过 [下限, 上限] 即自动产生告警事件</p>
</header>

{#if error}
  <div class="err">{error}</div>
{/if}

<section class="panel">
  <h2>{editingId ? '编辑规则' : '新增规则'}</h2>
  <div class="fields">
    <div class="field">
      <label>研磨机
        <select bind:value={form.millId}>
          {#each mills as m}
            <option value={String(m.id)}>{m.millCode} · {m.pigmentBase}</option>
          {/each}
        </select>
      </label>
    </div>
    <div class="field"><label>下限 Pa·s<input type="number" step="0.0001" min="0.0001" bind:value={form.minPaS} /></label></div>
    <div class="field"><label>上限 Pa·s<input type="number" step="0.0001" min="0.0001" bind:value={form.maxPaS} /></label></div>
    <div class="field check">
      <label><input type="checkbox" bind:checked={form.active} /> 启用（active）</label>
    </div>
  </div>
  <div class="actions">
    <button class="btn-primary" on:click={save}>{editingId ? '保存' : '创建'}</button>
    {#if editingId}
      <button class="btn-ghost" on:click={reset}>取消</button>
    {/if}
  </div>
</section>

<section class="panel">
  <table class="data-table">
    <thead>
      <tr>
        <th>ID</th>
        <th>研磨机</th>
        <th>下限 Pa·s</th>
        <th>上限 Pa·s</th>
        <th>状态</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      {#each rows as row}
        <tr>
          <td>{row.id}</td>
          <td>{millLabel(row.millId)}</td>
          <td>{row.minPaS}</td>
          <td>{row.maxPaS}</td>
          <td>
            <span class="badge {row.active ? 'on' : 'off'}">{row.active ? '启用中' : '已停用'}</span>
          </td>
          <td class="ops">
            <button class="link-btn" on:click={() => edit(row)}>编辑</button>
            <button class="link-btn danger" on:click={() => remove(row.id)}>删除</button>
          </td>
        </tr>
      {:else}
        <tr><td colspan="6">暂无规则</td></tr>
      {/each}
    </tbody>
  </table>
</section>

<style>
  .field.check label {
    grid-auto-flow: column;
    justify-content: start;
    align-items: center;
    gap: 0.45rem;
    height: 100%;
    color: var(--mist);
  }

  .badge.on {
    border-color: var(--vermillion-700);
    color: var(--vermillion-400);
  }

  .badge.off {
    color: var(--steel);
  }
</style>
