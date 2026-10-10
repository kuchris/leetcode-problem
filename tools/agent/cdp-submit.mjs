// Submit LeetCode solutions through a real Chrome session over CDP.
//
// The MCP server's HTTP path is rate limited; a real browser is the path a
// human uses and tolerates a higher rate, but it is still throttled per account
// (HTTP 429), so this driver skips anything already accepted and backs off when
// it is asked to slow down.
//
// Zero dependencies: Node's built-in fetch and WebSocket are enough.
//
// Single run:
//   node cdp-submit.mjs <tasks.json> <results.json> [interDelayMs] [port] [ledger.json]
//
// Watch mode — keeps scanning the solutions directory and submits whatever is
// not yet accepted, so a submitter never has to wait for a whole batch:
//   node cdp-submit.mjs --watch <solutionsDir> <ledger.json> <questionIds.json> \
//        <results.json> [interDelayMs] [pollMs] [port] [maxMinutes]
//
//   Watch mode stops when maxMinutes elapses or when a file named STOP exists
//   next to the ledger. It reloads the ledger every poll, so the Lead's merges
//   take effect without a restart.
//
// Env: LEETCODE_SESSION (required; never logged)
import { spawn } from 'node:child_process';
import { mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';

const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

const session = process.env.LEETCODE_SESSION;
if (!session) {
  console.error('LEETCODE_SESSION is not set');
  process.exit(2);
}

const watchMode = process.argv[2] === '--watch';
const args = process.argv.slice(watchMode ? 3 : 2);

let tasksFile, solutionsDir, ledgerPath, questionIdsPath, resultsFile;
let interDelayMs, pollMs, PORT, maxMinutes, singleTaskList = null;

if (watchMode) {
  [solutionsDir, ledgerPath, questionIdsPath, resultsFile] = args;
  interDelayMs = Number(args[4] ?? 10000);
  pollMs = Number(args[5] ?? 30000);
  PORT = Number(args[6] ?? 9222);
  maxMinutes = Number(args[7] ?? 90);
} else {
  [tasksFile, resultsFile] = args;
  interDelayMs = Number(args[2] ?? 3000);
  PORT = Number(args[3] ?? 9222);
  ledgerPath = args[4] ?? null;
  singleTaskList = JSON.parse(await readFile(tasksFile, 'utf8'));
}

const PROFILE = join(tmpdir(), `lc-chrome-profile-${PORT}`);
const BASE = `http://127.0.0.1:${PORT}`;
const STOP_FILE = ledgerPath ? join(ledgerPath, '..', 'STOP') : null;

async function readJson(path, fallback) {
  if (!path) return fallback;
  try {
    return JSON.parse(await readFile(path, 'utf8'));
  } catch {
    return fallback;
  }
}

/** Every solution file whose slug is not Accepted and whose id is known. */
async function scanPending(ledger, questionIds) {
  const names = await readdir(solutionsDir);
  const found = [];
  for (const name of names) {
    if (!name.endsWith('.py') || name.startsWith('_')) continue;
    const stem = name.slice(0, -3);
    const dash = stem.indexOf('-');
    if (dash < 0) continue;
    const frontendId = Number(stem.slice(0, dash));
    const slug = stem.slice(dash + 1);
    if (!Number.isFinite(frontendId)) continue;
    if (ledger[slug]?.statusMsg === 'Accepted') continue;
    if (questionIds[slug] === undefined) continue;
    found.push({
      frontendId,
      slug,
      questionId: questionIds[slug],
      path: join(solutionsDir, name),
    });
  }
  found.sort((a, b) => a.frontendId - b.frontendId);
  return found;
}

async function httpJson(url) {
  const response = await fetch(url);
  return response.json();
}

/** Minimal CDP client over the page's WebSocket debugger URL. */
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
        return;
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

async function launchChrome() {
  await mkdir(PROFILE, { recursive: true });
  const child = spawn(CHROME, [
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${PROFILE}`,
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-background-networking',
    '--disable-sync',
    '--window-size=1280,900',
    'about:blank',
  ], { stdio: 'ignore' });

  for (let attempt = 0; attempt < 60; attempt++) {
    await sleep(500);
    try {
      const version = await httpJson(`${BASE}/json/version`);
      if (version.webSocketDebuggerUrl) return child;
    } catch {
      // not up yet
    }
  }
  throw new Error('Chrome did not expose a CDP endpoint');
}

async function connectPage() {
  for (let attempt = 0; attempt < 30; attempt++) {
    const targets = await httpJson(`${BASE}/json/list`);
    const page = targets.find(t => t.type === 'page' && t.webSocketDebuggerUrl);
    if (page) {
      const ws = new WebSocket(page.webSocketDebuggerUrl);
      await new Promise((resolve, reject) => {
        ws.onopen = resolve;
        ws.onerror = () => reject(new Error('WebSocket failed to open'));
      });
      return new Cdp(ws);
    }
    await sleep(500);
  }
  throw new Error('no page target available');
}

const SUBMIT_SCRIPT = `async ([slug, questionId, code]) => {
  const csrf = (document.cookie.match(/(?:^|;\\s*)csrftoken=([^;]+)/) || [])[1] || '';
  const submitResponse = await fetch('/problems/' + slug + '/submit/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-csrftoken': csrf,
      'Referer': 'https://leetcode.com/problems/' + slug + '/',
    },
    body: JSON.stringify({ lang: 'python3', question_id: questionId, typed_code: code }),
  });
  const submitText = await submitResponse.text();
  let submitJson = null;
  try { submitJson = JSON.parse(submitText); } catch (e) {}
  if (submitResponse.status !== 200 || !submitJson || !submitJson.submission_id) {
    return { phase: 'submit', status: submitResponse.status, body: submitText.slice(0, 200) };
  }
  const submissionId = submitJson.submission_id;
  for (let attempt = 0; attempt < 80; attempt++) {
    await new Promise(r => setTimeout(r, 1500));
    const checkResponse = await fetch('/submissions/detail/' + submissionId + '/check/');
    const checkText = await checkResponse.text();
    let checkJson = null;
    try { checkJson = JSON.parse(checkText); } catch (e) {}
    if (checkJson && checkJson.state === 'SUCCESS') {
      return { phase: 'done', submissionId, check: checkJson };
    }
  }
  return { phase: 'timeout', submissionId };
}`;

const LOGIN_SCRIPT = `async () => {
  const csrf = (document.cookie.match(/(?:^|;\\s*)csrftoken=([^;]+)/) || [])[1] || '';
  const response = await fetch('/graphql/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'x-csrftoken': csrf },
    body: JSON.stringify({ query: 'query globalData { userStatus { isSignedIn username } }' }),
  });
  const text = await response.text();
  try { return JSON.parse(text); } catch (e) { return { status: response.status }; }
}`;

const results = [];
let chrome = null;

/**
 * Record an acceptance in the ledger immediately.
 *
 * Without this the driver only ever READS the ledger, so a second watch window
 * starts before the Lead has merged the first one's results and re-submits
 * everything it just accepted. That happened: ten problems were submitted twice
 * and the duplicate traffic was pure waste against a per-account rate limit.
 * Only one submitter runs at a time, so this read-modify-write cannot race.
 */
async function recordAccepted(record) {
  if (!ledgerPath || record.statusMsg !== 'Accepted') return;
  try {
    const ledger = await readJson(ledgerPath, {});
    ledger[record.slug] = {
      statusMsg: 'Accepted',
      totalCorrect: record.totalCorrect,
      totalTestcases: record.totalTestcases,
      submissionId: record.submissionId,
      url: record.url,
      source: 'cdp-submit',
    };
    await writeFile(ledgerPath, JSON.stringify(ledger, null, 1), 'utf8');
  } catch (error) {
    console.error(`ledger write failed for ${record.slug}: ${error.message}`);
  }
}

async function attempt(cdp, task, code) {
  const navigation = cdp.waitFor('Page.loadEventFired', 60000);
  await cdp.send('Page.navigate', { url: `https://leetcode.com/problems/${task.slug}/` });
  await navigation;
  const evaluated = await cdp.send('Runtime.evaluate', {
    expression: `(${SUBMIT_SCRIPT})(${JSON.stringify([task.slug, task.questionId, code])})`,
    awaitPromise: true,
    returnByValue: true,
  });
  return evaluated.result?.value ?? {};
}

/** Submit one task with 429 backoff; returns the record and prints a line. */
async function submitOne(cdp, task) {
  const code = await readFile(task.path, 'utf8');
  let value = {};
  let backoff = 30000;

  for (let tries = 1; tries <= 6; tries += 1) {
    value = await attempt(cdp, task, code);
    if (!(value.phase === 'submit' && value.status === 429)) break;
    console.log(`429  ${task.slug} attempt ${tries}; sleeping ${backoff}ms`);
    await sleep(backoff);
    backoff = Math.min(backoff * 2, 240000);
  }

  const record = { slug: task.slug, ...value };
  if (value.phase === 'done') {
    const check = value.check ?? {};
    record.statusMsg = check.status_msg ?? null;
    record.totalCorrect = check.total_correct ?? null;
    record.totalTestcases = check.total_testcases ?? null;
    record.url = `https://leetcode.com/submissions/detail/${value.submissionId}/`;
    if (record.statusMsg !== 'Accepted') {
      // A non-Accepted verdict is only actionable if the judge's own
      // diagnostics survive, so keep them for the failure triage step.
      record.lastTestcase = check.last_testcase ?? null;
      record.codeOutput = check.code_output ?? null;
      record.expectedOutput = check.expected_output ?? null;
      record.runtimeError = check.runtime_error ?? check.full_runtime_error ?? null;
      record.compileError = check.compile_error ?? null;
      record.stdOutput = check.std_output ?? null;
    }
    delete record.check;
    console.log(`${record.statusMsg === 'Accepted' ? 'AC  ' : 'FAIL'} ${task.slug} ` +
      `${record.statusMsg} ${record.totalCorrect}/${record.totalTestcases} id=${value.submissionId}`);
  } else {
    console.log(`ERR  ${task.slug} phase=${value.phase} status=${value.status ?? ''}`);
  }
  results.push(record);
  await writeFile(resultsFile, JSON.stringify(results, null, 2), 'utf8');
  await recordAccepted(record);
  return record;
}

try {
  chrome = await launchChrome();
  const cdp = await connectPage();

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

  const login = await cdp.send('Runtime.evaluate', {
    expression: `(${LOGIN_SCRIPT})()`,
    awaitPromise: true,
    returnByValue: true,
  });
  const status = login.result?.value?.data?.userStatus;
  console.log(`login: ${JSON.stringify(status)}`);
  if (!status?.isSignedIn) throw new Error('the injected session is not signed in');

  if (watchMode) {
    const deadline = Date.now() + maxMinutes * 60000;
    let idlePolls = 0;
    let submittedTotal = 0;
    console.log(`watch: polling every ${pollMs}ms, stopping after ${maxMinutes} min`);

    while (Date.now() < deadline) {
      if (STOP_FILE && existsSync(STOP_FILE)) {
        console.log('watch: STOP file present, exiting');
        break;
      }
      const ledger = await readJson(ledgerPath, {});
      const questionIds = await readJson(questionIdsPath, {});
      const pending = await scanPending(ledger, questionIds);

      if (pending.length === 0) {
        idlePolls += 1;
        console.log(`watch: nothing pending (idle poll ${idlePolls}), submitted ${submittedTotal}`);
        await sleep(pollMs);
        continue;
      }

      idlePolls = 0;
      console.log(`watch: ${pending.length} pending -> ${pending.map(t => t.slug).join(', ')}`);
      for (const task of pending) {
        if (Date.now() >= deadline) break;
        if (STOP_FILE && existsSync(STOP_FILE)) break;
        await submitOne(cdp, task);
        submittedTotal += 1;
        await sleep(interDelayMs);
      }
    }
    console.log(`watch: finished, submitted ${submittedTotal} this session`);
  } else {
    const ledger = await readJson(ledgerPath, {});
    let index = 0;
    for (const task of singleTaskList) {
      if (ledger[task.slug]?.statusMsg === 'Accepted') {
        console.log(`SKIP ${task.slug} (already accepted)`);
        continue;
      }
      if (index > 0) await sleep(interDelayMs);
      index += 1;
      await submitOne(cdp, task);
    }
  }
} catch (error) {
  console.error(`fatal: ${error.message}`);
  process.exitCode = 1;
} finally {
  if (chrome) chrome.kill();
  await writeFile(resultsFile, JSON.stringify(results, null, 2), 'utf8');
}
