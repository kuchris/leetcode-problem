import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { fileURLToPath } from 'node:url';
import { join } from 'node:path';

const client = new Client({ name: 'leetcode-practice-check', version: '1.0.0' });
const transport = new StdioClientTransport({
  command: join(process.env.SystemRoot, 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe'),
  args: ['-NoLogo', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', fileURLToPath(new URL('./start.ps1', import.meta.url))],
  env: { ...process.env },
  stderr: 'pipe',
});
// Server logs can contain request diagnostics. Do not echo them or credentials.
transport.stderr?.on('data', () => {});

async function call(name, args = {}) {
  const result = await client.callTool({ name, arguments: args }, undefined, { timeout: 45000 });
  if (result.isError) throw new Error(`${name} returned an error; check connectivity and login.`);
  const text = result.content.filter(item => item.type === 'text').map(item => item.text).join('\n');
  const value = JSON.parse(text);
  if (value.error) throw new Error(`${name} returned an API error.`);
  return value;
}

try {
  await client.connect(transport);
  const { tools } = await client.listTools();
  const names = tools.map(tool => tool.name);
  const required = ['get_problem', 'get_daily_challenge'];
  if (process.env.LEETCODE_SESSION) required.push('get_user_status', 'run_code', 'submit_solution');
  for (const name of required) {
    if (!names.includes(name)) throw new Error(`Missing tool: ${name}`);
  }
  console.log(`MCP connected: ${names.length} tools; required tools present.`);
  const problem = await call('get_problem', { titleSlug: 'two-sum' });
  if (problem.problem?.titleSlug !== 'two-sum' || !problem.problem?.content) {
    throw new Error('get_problem did not return the requested problem description.');
  }
  console.log(`Problem: ${problem.problem.title}; description and ${problem.problem.codeSnippets.length} code templates received.`);
  const daily = await call('get_daily_challenge');
  if (!daily.date || !daily.problem?.question?.content) throw new Error('Daily challenge response is incomplete.');
  console.log(`Daily: ${daily.date} - ${daily.problem.question.questionFrontendId}. ${daily.problem.question.title}`);
  if (process.env.LEETCODE_SESSION) {
    const status = await call('get_user_status');
    const isSignedIn = status.status?.isSignedIn === true;
    console.log(JSON.stringify({ check: 'get_user_status', isSignedIn }));
    if (!isSignedIn) throw new Error('Session was not accepted. Run login.ps1 with a current LEETCODE_SESSION value.');
  } else {
    console.log('Authentication: not configured. Website run/submit not tested.');
  }
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
} finally {
  await client.close();
}
