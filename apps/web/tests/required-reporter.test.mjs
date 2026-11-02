import assert from 'node:assert/strict';
import test from 'node:test';
import RequiredReporter from '../e2e/required-reporter.js';

function reporterWithTests(ids) {
  const reporter = new RequiredReporter();
  reporter.onBegin({}, { allTests: () => ids.map(id => ({ id })) });
  return reporter;
}

test('required browser reporter preserves success and failure', async () => {
  const reporter = reporterWithTests(['a', 'b']);
  reporter.onTestEnd({ id: 'a' }, { status: 'passed' });
  reporter.onTestEnd({ id: 'b' }, { status: 'passed' });
  assert.deepEqual(await reporter.onEnd({ status: 'passed' }), { status: 'passed' });
  assert.deepEqual(await reporter.onEnd({ status: 'failed' }), { status: 'failed' });
});

test('required browser reporter rejects skipped, empty and incomplete runs', async () => {
  const skipped = reporterWithTests(['a']);
  skipped.onTestEnd({ id: 'a' }, { status: 'skipped' });
  assert.deepEqual(await skipped.onEnd({ status: 'passed' }), { status: 'failed' });
  const expectedFailure = reporterWithTests(['a']);
  expectedFailure.onTestEnd({ id: 'a' }, { status: 'failed' });
  assert.deepEqual(await expectedFailure.onEnd({ status: 'passed' }), { status: 'failed' });
  assert.deepEqual(await reporterWithTests([]).onEnd({ status: 'passed' }), { status: 'failed' });
  assert.deepEqual(await reporterWithTests(['a']).onEnd({ status: 'passed' }), { status: 'failed' });
});
