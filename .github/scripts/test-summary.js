module.exports = async ({ core }) => {
  const fs = require('fs');
  const outputFile = `${process.env.RUNNER_TEMP}/tofu-test.txt`;
  const output = fs.existsSync(outputFile) ? fs.readFileSync(outputFile, 'utf8') : '';

  if (!output.trim()) { return; }

  const errorMatch = output.match(/Error:.+/);

  // Parse per-run results: track current file, then match run lines
  const runs = [];
  let currentFile = '';
  for (const line of output.split('\n')) {
    const fileMatch = line.match(/^(\S+\.tftest\.hcl)\.\.\./);
    const runMatch  = line.match(/^\s+run "(.+)"\.\.\. (pass|fail)/);
    if (fileMatch) currentFile = fileMatch[1];
    if (runMatch)  runs.push({ file: currentFile, run: runMatch[1], result: runMatch[2] });
  }

  const lines = [
    '#### 🔨 OpenTofu Test',
    '',
  ];

  if (runs.length) {
    lines.push('| Result | File | Run |', '|---|---|---|');
    for (const r of runs) {
      const icon = r.result === 'pass' ? '✅' : '❌';
      lines.push(`| ${icon} | \`${r.file}\` | \`${r.run}\` |`);
    }
    lines.push('');
  }

  if (errorMatch) {
    lines.push(`> ❌ ${errorMatch[0]}`, '');
  }

  lines.push(
    '<details>',
    '<summary>Full Test Output</summary>',
    '',
    '```hcl',
    output,
    '```',
    '',
    '</details>',
  );

  await core.summary.addRaw(lines.join('\n')).write();
};
