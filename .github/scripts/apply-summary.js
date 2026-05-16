module.exports = async ({ core }) => {
  const output = process.env.OPENTOFU_OUTPUT || '';

  if (!output.trim()) { return; }

  const applyMatch = output.match(/Apply complete! Resources: (\d+) added, (\d+) changed, (\d+) destroyed/);
  const errorMatch = output.match(/Error:.+/);

  // Track resources that started and those that completed
  const started = {};
  const completed = new Set();
  const durations = {};

  for (const line of output.split('\n')) {
    const creating   = line.match(/^(.+): Creating\.\.\./);
    const modifying  = line.match(/^(.+): Modifying\.\.\./);
    const destroying = line.match(/^(.+): Destroying\.\.\./);
    const created    = line.match(/^(.+): Creation complete after (\S+)/);
    const modified   = line.match(/^(.+): Modifications complete after (\S+)/);
    const destroy    = line.match(/^(.+): Destruction complete after (\S+)/);
    if (creating)   started[creating[1].trim()]   = 'added';
    if (modifying)  started[modifying[1].trim()]  = 'changed';
    if (destroying) started[destroying[1].trim()] = 'destroyed';
    if (created)  { completed.add(created[1].trim());  durations[created[1].trim()]  = created[2]; }
    if (modified) { completed.add(modified[1].trim()); durations[modified[1].trim()] = modified[2]; }
    if (destroy)  { completed.add(destroy[1].trim());  durations[destroy[1].trim()]  = destroy[2]; }
  }

  const actionOrder = { destroyed: 0, changed: 1, added: 2 };
  const actionLabel = { added: '➕ Add', changed: '🔄 Change', destroyed: '🗑️ Destroy' };

  const rows = Object.entries(started).sort(([, a], [, b]) => actionOrder[a] - actionOrder[b]);

  const lines = ['#### 🚀 OpenTofu Apply', ''];

  if (rows.length) {
    lines.push('| Action | Resource | Duration | Status |', '|---|---|---|---|');
    for (const [r, action] of rows) {
      const ok  = completed.has(r);
      const dur = durations[r] ? durations[r] : '—';
      lines.push(`| ${actionLabel[action]} | \`${r}\` | ${dur} | ${ok ? '✅' : '❌'} |`);
    }
    lines.push('');
  }

  if (!applyMatch && !errorMatch && !rows.length) {
    lines.push('**✅ No changes.** Your infrastructure matches the configuration.', '');
  }

  if (errorMatch) {
    lines.push(`> ❌ ${errorMatch[0]}`, '');
  }

  // Parse outputs section
  const outputsStart = output.indexOf('\nOutputs:\n');
  if (outputsStart !== -1) {
    const outputsBlock = output.slice(outputsStart + '\nOutputs:\n'.length).trim();
    const outputEntries = [];
    for (const line of outputsBlock.split('\n')) {
      const m = line.match(/^(\S+)\s*=\s*(.+)$/);
      if (m) outputEntries.push({ name: m[1], value: m[2].trim() });
    }
    if (outputEntries.length) {
      lines.push('**Outputs**', '');
      lines.push('| Name | Value |', '|---|---|');
      for (const { name, value } of outputEntries) {
        lines.push(`| \`${name}\` | \`${value}\` |`);
      }
      lines.push('');
    }
  }

  lines.push(
    '<details>',
    '<summary>Full Apply Output</summary>',
    '',
    '```hcl',
    output,
    '```',
    '',
    '</details>',
  );

  await core.summary.addRaw(lines.join('\n')).write();
};
