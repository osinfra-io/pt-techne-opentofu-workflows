module.exports = async ({ core }) => {
  const output = process.env.OPENTOFU_OUTPUT || '';

  if (!output.trim()) { return; }

  const escape = (s) => String(s).replace(/[`|\\]/g, '\\$&');

  const planMatch= output.match(/Plan: (\d+) to add, (\d+) to change, (\d+) to destroy/);
  const errorMatch = output.match(/Error:.+/);

  const toAdd = [];
  const toChange = [];
  const toDestroy = [];

  for (const line of output.split('\n')) {
    const m = line.match(/# (\S+) will be (created|destroyed|updated in-place)/);
    const r = line.match(/# (\S+).*must be replaced/);
    if (m) {
      if (m[2] === 'created') toAdd.push(m[1]);
      else if (m[2] === 'destroyed') toDestroy.push(m[1]);
      else if (m[2] === 'updated in-place') toChange.push(m[1]);
    } else if (r) {
      toChange.push(r[1]);
    }
  }

  // Parse output-only changes
  const outputChanges = [];
  const outputsIdx = output.indexOf('Changes to Outputs:');
  if (outputsIdx !== -1) {
    const block = output.slice(outputsIdx + 'Changes to Outputs:'.length);
    for (const line of block.split('\n')) {
      if (!line.trim()) continue;
      const m = line.match(/^\s+([+~-])\s+(\S+)\s*=\s*(.+)$/);
      if (!m) break;
      const icon = m[1] === '+' ? '➕' : m[1] === '-' ? '🗑️' : '🔄';
      outputChanges.push({ icon, name: m[2], value: m[3].trim() });
    }
  }

  const lines = ['#### 🔨 OpenTofu Plan', ''];

  if (toDestroy.length || toChange.length || toAdd.length) {
    lines.push('| Action | Resource |', '|---|---|');
    for (const r of toDestroy) lines.push(`| 🗑️ Destroy | \`${escape(r)}\` |`);
    for (const r of toChange)  lines.push(`| 🔄 Change  | \`${escape(r)}\` |`);
    for (const r of toAdd)     lines.push(`| ➕ Add     | \`${escape(r)}\` |`);
    lines.push('');
  }

  if (outputChanges.length) {
    lines.push('**📤 Output changes**', '');
    lines.push('| Action | Output | Value |', '|---|---|---|');
    for (const { icon, name, value } of outputChanges) {
      lines.push(`| ${icon} | \`${escape(name)}\` | \`${escape(value)}\` |`);
    }
    lines.push('');
  }

  if (!planMatch && !errorMatch && !outputChanges.length) {
    lines.push('**✅ No changes.** Your infrastructure matches the configuration.', '');
  }

  if (errorMatch) {
    lines.push(`> ❌ ${errorMatch[0]}`, '');
  }

  lines.push(
    '<details>',
    '<summary>Full Plan Output</summary>',
    '',
    '```hcl',
    output,
    '```',
    '',
    '</details>',
  );

  await core.summary.addRaw(lines.join('\n')).write();
};
