import { readdirSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';

const directory = resolve(process.argv[2] ?? 'tests');
let files;
try {
  files = readdirSync(directory, { withFileTypes: true })
    .filter(entry => entry.isFile() && entry.name.endsWith('.test.mjs'))
    .map(entry => join(directory, entry.name)).sort();
} catch (error) {
  console.error(`Cannot discover required Node tests: ${error.message}`);
  process.exit(1);
}

if (files.length === 0) {
  console.error('Required Node tests incomplete: no test files found.');
  process.exit(1);
}

const result = spawnSync(process.execPath, ['--test', '--test-reporter=tap', ...files], {
  encoding: 'utf8', maxBuffer: 32 * 1024 * 1024,
});
if (result.stdout) process.stdout.write(result.stdout);
if (result.stderr) process.stderr.write(result.stderr);

const counts = {};
let valid = true;
for (const line of (result.stdout ?? '').split(/\r?\n/)) {
  const match = /^# (tests|pass|fail|cancelled|skipped|todo) (\d+)$/.exec(line);
  if (!match) continue;
  if (Object.hasOwn(counts, match[1])) valid = false;
  counts[match[1]] = Number(match[2]);
}
const keys = ['tests', 'pass', 'fail', 'cancelled', 'skipped', 'todo'];
valid &&= keys.every(key => Number.isSafeInteger(counts[key]));
valid &&= counts.tests > 0 && counts.pass === counts.tests;
valid &&= counts.fail === 0 && counts.cancelled === 0 && counts.skipped === 0 && counts.todo === 0;
if (result.error || result.status !== 0 || !valid) {
  console.error(`Required Node tests incomplete or failed${result.error ? `: ${result.error.message}` : '.'}`);
  process.exit(1);
}
