import { expect, test } from '@playwright/test';

test('routes display their matching workspace', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Ready when you are.' })).toBeVisible();
  await page.getByRole('link', { name: 'Call history', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Call history', exact: true })).toBeVisible();
  await page.getByRole('link', { name: 'Settings', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Settings', exact: true })).toBeVisible();
  await page.getByRole('link', { name: 'Dialer', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Ready when you are.' })).toBeVisible();
});

test('preview starts without configuration and cannot place calls', async ({ page }) => {
  await page.route('**/config.json', route => route.abort());
  await page.goto('/');
  await expect(page.getByText('Preview the workspace. Calling and backend integration are not available yet.')).toBeVisible();
  await expect(page.getByText('Calling not connected')).toBeVisible();
  await expect(page.getByLabel('Phone number')).toBeDisabled();
  await expect(page.getByRole('button', { name: /Start call/ })).toBeDisabled();
});

test('skip link and route navigation work with the keyboard', async ({ page }) => {
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
