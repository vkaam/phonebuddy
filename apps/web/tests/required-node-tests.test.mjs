import assert from 'node:assert/strict';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const runner = fileURLToPath(new URL('../scripts/run-required-tests.mjs', import.meta.url));

test('required Node runner rejects incomplete and failing real test runs', () => {
  const cases = [
    ['pass', "test('pass', () => {});", 0],
    ['skip', "test.skip('skip', () => {});", 1],
    ['todo', "test.todo('todo');", 1],
    ['failure', "test('failure', () => { throw new Error('failure'); });", 1],
    ['cancelled', "test('cancelled', { timeout: 1 }, async () => await new Promise(r => setTimeout(r, 100)));", 1],
    ['inconclusive', "test('ambiguous', () => console.log('tests 1'));", 1],
    ['empty', null, 1],
  ];
  for (const [name, source, expected] of cases) {
    const directory = mkdtempSync(join(tmpdir(), 'phonebuddy-node-tests-'));
    try {
      if (source !== null) writeFileSync(join(directory, 'fixture.test.mjs'),
        `import test from 'node:test';\n${source}\n`);
      const env = { ...process.env };
      delete env.NODE_TEST_CONTEXT;
      const result = spawnSync(process.execPath, [runner, directory], {
        encoding: 'utf8', timeout: 15000, env,
      });
      assert.equal(result.status, expected, `${name}: ${result.stdout}\n${result.stderr}`);
      if (expected !== 0) assert.match(result.stderr, /Required Node tests incomplete or failed|no test files found/);
      else assert.match(result.stdout, /# pass 1/);
      if (['skip', 'todo', 'cancelled'].includes(name)) {
        const count = name === 'skip' ? 'skipped' : name;
        assert.match(result.stdout, new RegExp(`# ${count} 1`));
      }
    } finally {
      rmSync(directory, { recursive: true, force: true });
    }
  }
});
