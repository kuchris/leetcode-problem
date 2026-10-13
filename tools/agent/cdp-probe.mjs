// Run one JavaScript expression in a logged-in LeetCode page over CDP.
//
// A general-purpose probe, built because the MCP bridge returned an empty
// codeSnippets list for SQL problems and there was no other way to ask LeetCode
// which language slugs it actually accepts. It reuses the same launch, cookie
// injection and evaluation path as cdp-submit.mjs, so what it reports is what the
// submit driver will see.
//
//   node cdp-probe.mjs <script.js> [port]
//
// The script file must contain a single expression that evaluates to an async
// function taking no arguments, e.g.:
//
//   async () => {
//     const r = await fetch('/graphql/', { ... });
//     return await r.json();
//   }
//
// The resolved value is printed as JSON. The session is never logged.
//
// Env: LEETCODE_SESSION (required)
import { spawn } from 'node:child_process';
import { mkdir, readFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

const session = process.env.LEETCODE_SESSION;
if (!session) {
  console.error('LEETCODE_SESSION is not set');
  process.exit(2);
}

const [scriptPath] = process.argv.slice(2);
const PORT = Number(process.argv[3] ?? 9224);
if (!scriptPath) {
  console.error('usage: node cdp-probe.mjs <script.js> [port]');
  process.exit(2);
}

const PROFILE = join(tmpdir(), `lc-chrome-probe-${PORT}`);
const BASE = `http://127.0.0.1:${PORT}`;
const expression = await readFile(scriptPath, 'utf8');

class Cdp {
  constructor(ws) {
    this.ws = ws;
    this.nextId = 1;
    this.pending = new Map();
    this.waiters = [];
    ws.onmessage = event => {
      const message = JSON.parse(event.data);
      if (message.id && this.pending.has(message.id)) {
        const { resolve, reject } = this.pending.get(message.id);
        this.pending.delete(message.id);
        if (message.error) reject(new Error(JSON.stringify(message.error)));
        else resolve(message.result);
      }
      if (message.method) {
        for (const waiter of [...this.waiters]) {
          if (waiter.method === message.method) {
            this.waiters.splice(this.waiters.indexOf(waiter), 1);
            clearTimeout(waiter.timer);
            waiter.resolve(message.params);
          }
        }
      }
    };
  }
  send(method, params = {}) {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }
  waitFor(method, timeoutMs = 60000) {
    return new Promise((resolve, reject) => {
      const waiter = { method, resolve, reject };
      waiter.timer = setTimeout(() => {
        this.waiters.splice(this.waiters.indexOf(waiter), 1);
        reject(new Error(`timed out waiting for ${method}`));
      }, timeoutMs);
      this.waiters.push(waiter);
    });
  }
}

const httpJson = async url => (await fetch(url)).json();

await mkdir(PROFILE, { recursive: true });
const chrome = spawn(CHROME, [
  `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${PROFILE}`,
  '--no-first-run',
  '--no-default-browser-check',
  '--disable-background-networking',
  '--disable-sync',
  'about:blank',
], { stdio: 'ignore' });

let cdp = null;
try {
  let version = null;
  for (let attempt = 0; attempt < 60 && !version; attempt++) {
    await sleep(500);
    try { version = await httpJson(`${BASE}/json/version`); } catch { /* not up */ }
  }
  if (!version) throw new Error('Chrome did not expose a CDP endpoint');

  let page = null;
  for (let attempt = 0; attempt < 30 && !page; attempt++) {
    const targets = await httpJson(`${BASE}/json/list`);
    page = targets.find(t => t.type === 'page' && t.webSocketDebuggerUrl);
    if (!page) await sleep(500);
  }
  if (!page) throw new Error('no page target available');

  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    ws.onopen = resolve;
    ws.onerror = () => reject(new Error('WebSocket failed to open'));
  });
  cdp = new Cdp(ws);

  await cdp.send('Page.enable');
  await cdp.send('Runtime.enable');
  await cdp.send('Network.enable');
  await cdp.send('Network.setCookie', {
    name: 'LEETCODE_SESSION',
    value: session,
    domain: '.leetcode.com',
    path: '/',
    httpOnly: true,
    secure: true,
    sameSite: 'Lax',
  });

  const loaded = cdp.waitFor('Page.loadEventFired', 60000);
  await cdp.send('Page.navigate', { url: 'https://leetcode.com/problemset/' });
  await loaded;

  const result = await cdp.send('Runtime.evaluate', {
    expression: `(${expression})()`,
    awaitPromise: true,
    returnByValue: true,
  });

  if (result.exceptionDetails) {
    console.error('page exception:', JSON.stringify(result.exceptionDetails, null, 2));
    process.exitCode = 1;
  } else {
    console.log(JSON.stringify(result.result?.value ?? null, null, 2));
  }
} finally {
  try { cdp?.ws.close(); } catch { /* already closed */ }
  chrome.kill();
}
