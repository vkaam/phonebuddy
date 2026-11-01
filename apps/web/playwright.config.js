import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  outputDir: mkdtempSync(join(tmpdir(), 'phonebuddy-browser-')),
  forbidOnly: true,
  reporter: [['list'], ['./e2e/required-reporter.js']],
  use: { browserName: 'chromium', baseURL: 'http://127.0.0.1:4178' },
  webServer: {
    command: 'npm run dev -- --host 127.0.0.1 --port 4178 --strictPort',
    url: 'http://127.0.0.1:4178',
    reuseExistingServer: false,
    timeout: 30000,
  },
});
