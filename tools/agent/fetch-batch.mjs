// Fetch many problems over ONE MCP session.
// Usage: node fetch-batch.mjs <slugs.json> <out.json>
//
// The MCP SDK and launcher are resolved from this file's own location, so the
// tool works from any checkout rather than only the original one.
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const AGENT_DIR = dirname(fileURLToPath(import.meta.url));
const REPO = resolve(AGENT_DIR, '..', '..');
const SDK = join(REPO, 'tools', 'leetcode', 'node_modules', '@modelcontextprotocol',
  'sdk', 'dist', 'esm', 'client');

const { Client } = await import(pathToFileURL(join(SDK, 'index.js')).href);
const { StdioClientTransport } = await import(pathToFileURL(join(SDK, 'stdio.js')).href);

const [slugsFile, outFile] = process.argv.slice(2);
const slugs = JSON.parse(await readFile(slugsFile, 'utf8'));

const transport = new StdioClientTransport({
  command: join(process.env.SystemRoot, 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe'),
  args: ['-NoLogo', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
    join(REPO, 'tools', 'leetcode', 'start.ps1')],
  env: { ...process.env },
  stderr: 'pipe',
});
transport.stderr?.on('data', () => {});

const client = new Client({ name: 'batch-fetch', version: '1.0.0' });
const results = [];
try {
  await client.connect(transport);
  for (const slug of slugs) {
    try {
      const result = await client.callTool(
        { name: 'get_problem', arguments: { titleSlug: slug } },
        undefined,
        { timeout: 60000 },
      );
      const text = result.content.filter(i => i.type === 'text').map(i => i.text).join('\n');
      const value = JSON.parse(text);
      if (value.error || !value.problem?.content) throw new Error(value.error ?? 'empty content');
      results.push({ slug, ok: true, problem: value.problem });
      process.stderr.write(`ok   ${slug}\n`);
    } catch (error) {
      results.push({ slug, ok: false, error: error.message });
      process.stderr.write(`FAIL ${slug}: ${error.message}\n`);
    }
  }
} finally {
  await client.close();
}
await writeFile(outFile, JSON.stringify(results, null, 1), 'utf8');
const failed = results.filter(r => !r.ok).length;
console.log(`fetched ${results.length - failed}/${results.length}; failures: ${failed}`);
