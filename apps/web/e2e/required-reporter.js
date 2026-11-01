// Fail closed if a required browser test was skipped or never completed.
export default class RequiredReporter {
  total = 0;
  completed = new Set();
  skipped = 0;

  onBegin(_config, suite) {
    this.total = suite.allTests().length;
  }

  onTestEnd(test, result) {
    this.completed.add(test.id);
    if (result.status === 'skipped') this.skipped += 1;
  }

  async onEnd(result) {
    if (this.total === 0 || this.skipped > 0 || this.completed.size !== this.total) {
      console.error(`Required browser tests incomplete: ${this.completed.size}/${this.total} completed, ${this.skipped} skipped.`);
      return { status: 'failed' };
    }
    return { status: result.status };
  }
}
