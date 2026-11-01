import { expect, test } from '@playwright/test';

async function validConfig(page) {
  await page.route('**/config.json', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ apiBaseUrl: 'https://example.test' }),
  }));
}

test('routes display their matching workspace', async ({ page }) => {
  await validConfig(page);
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Ready when you are.' })).toBeVisible();
  await page.getByRole('link', { name: 'Call history', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Call history', exact: true })).toBeVisible();
  await page.getByRole('link', { name: 'Settings', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Settings', exact: true })).toBeVisible();
  await page.getByRole('link', { name: 'Dialer', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Ready when you are.' })).toBeVisible();
});

test('missing configuration displays a setup error', async ({ page }) => {
  await page.route('**/config.json', route => route.fulfill({ status: 404, body: 'missing' }));
  await page.goto('/');
  await expect(page.getByRole('alert')).toContainText('Add a public config.json');
  await expect(page.getByRole('button', { name: 'Try again' })).toBeVisible();
});

test('skip link and route navigation work with the keyboard', async ({ page }) => {
  await validConfig(page);
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Ready when you are.' })).toBeVisible();
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', { name: 'Skip to content' })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.locator('main')).toBeFocused();
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Ready when you are.' })).toBeVisible();
  await page.keyboard.press('Tab');
  await page.keyboard.press('Tab');
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', { name: 'Call history', exact: true })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('heading', { name: 'Call history', exact: true })).toBeVisible();
});
