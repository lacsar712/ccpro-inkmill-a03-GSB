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
    minPaS: '8',
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
    return m ? `${m.millCode} (#${m.id})` : `#${id}`;
  }

  function reset() {
    form = {
      millId: mills[0] ? String(mills[0].id) : '',
      minPaS: '8',
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
    const payload = {
      millId: Number(form.millId),
      minPaS: Number(form.minPaS),
      maxPaS: Number(form.maxPaS),
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
    if (!confirm('确认删除该粘度告警规则？')) return;
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
  <p>按研磨机设定 Pa·s 上下限（下限必须小于上限），启用后取样越界自动生成告警事件</p>
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
            <option value={String(m.id)}>{m.millCode}</option>
          {/each}
        </select>
      </label>
    </div>
    <div class="field"><label>下限 Pa·s<input type="number" step="0.0001" min="0.0001" bind:value={form.minPaS} /></label></div>
    <div class="field"><label>上限 Pa·s<input type="number" step="0.0001" min="0.0001" bind:value={form.maxPaS} /></label></div>
    <div class="field check">
      <label><input type="checkbox" bind:checked={form.active} /> 启用该规则</label>
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
          <td><span class="badge {row.active ? 'ok' : ''}">{row.active ? '启用' : '停用'}</span></td>
          <td class="ops">
            <button class="link-btn" on:click={() => edit(row)}>编辑</button>
            <button class="link-btn danger" on:click={() => remove(row.id)}>删除</button>
          </td>
        </tr>
      {:else}
        <tr><td colspan="6">暂无数据</td></tr>
      {/each}
    </tbody>
  </table>
</section>

<style>
  .check label {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    color: var(--steel);
    font-size: 0.85rem;
    padding-top: 1.1rem;
  }
</style>
