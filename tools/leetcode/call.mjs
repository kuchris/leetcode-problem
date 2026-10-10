import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { join } from 'node:path';

// Arguments are read from a JSON file; credentials stay in the local launcher.
const [toolName, argumentsFile] = process.argv.slice(2);
if (!toolName) {
  console.error('Usage: node tools/leetcode/call.mjs TOOL [ARGUMENTS_JSON_FILE]');
  process.exit(1);
}
const client = new Client({ name: 'leetcode-practice-cli', version: '1.0.0' });
const transport = new StdioClientTransport({
  command: join(process.env.SystemRoot, 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe'),
  args: ['-NoLogo', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', fileURLToPath(new URL('./start.ps1', import.meta.url))],
  env: { ...process.env },
  stderr: 'pipe',
});
transport.stderr?.on('data', () => {});

try {
  const args = argumentsFile ? JSON.parse(await readFile(argumentsFile, 'utf8')) : {};
  await client.connect(transport);
  const result = await client.callTool({ name: toolName, arguments: args }, undefined, { timeout: 180000 });
  if (result.isError) throw new Error(`${toolName} failed.`);
  const value = JSON.parse(result.content.filter(item => item.type === 'text').map(item => item.text).join('\n'));
  if (value.error) {
    // Avoid echoing HTTP error bodies that could contain authentication headers.
    throw new Error(`${toolName} returned an API error. Check the connection and session.`);
  }
  console.log(JSON.stringify(value, null, 2));
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
} finally {
  await client.close();
}
