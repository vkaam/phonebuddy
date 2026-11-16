import { expect, test } from '@playwright/test';

test('workspace stays behind the sign-in configuration gate', async ({ page }) => {
  await page.route('**/config.json', route => route.abort());
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Sign-in is not configured' })).toBeVisible();
  await expect(page.getByRole('navigation', { name: 'Main navigation' })).toHaveCount(0);
  await expect(page.getByLabel('Phone number')).toHaveCount(0);
});

test('sign-in setup message is readable on reload', async ({ page }) => {
  await page.route('**/config.json', route => route.abort());
  await page.goto('/');
  await expect(page.getByText('Add the public Entra and API settings to config.json to enable secure sign-in.')).toBeVisible();
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Sign-in is not configured' })).toBeVisible();
});
