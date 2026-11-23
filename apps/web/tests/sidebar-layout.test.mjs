import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const css = readFileSync(new URL('../src/style.css', import.meta.url), 'utf8');
const main = readFileSync(new URL('../src/main.tsx', import.meta.url), 'utf8');

function declarations(selector) {
  const escaped = selector.replace(/[.*+?^${}()|[\]\\>]/g, '\\$&');
  const match = new RegExp(`(?:^|[};])\\s*${escaped}\\s*\\{([^}]*)\\}`).exec(css);
  assert.ok(match, `missing CSS rule for ${selector}`);
  return Object.fromEntries(match[1].split(';').filter(Boolean).map(item => {
    const index = item.indexOf(':');
    return [item.slice(0, index).trim(), item.slice(index + 1).trim()];
  }));
}

test('the signed-in sidebar renders a sign-out button wired to auth.signOut', () => {
  const sidebarBottom = /<div className="sidebar-bottom">.*?<\/div>/s.exec(main)?.[0] ?? '';
  assert.match(sidebarBottom, /<button className="signout" type="button" onClick=\{\(\) => void session\.auth\?\.signOut\(\)\}>Sign out<\/button>/);
});

test('a long account email cannot push the sign-out button out of the sidebar', () => {
  const text = declarations('.account-text');
  assert.equal(text['min-width'], '0');
  assert.match(text.flex, /^1 1 0/);
  const lines = declarations('.account-text>*');
  assert.equal(lines.overflow, 'hidden');
  assert.equal(lines['text-overflow'], 'ellipsis');
  assert.equal(lines['white-space'], 'nowrap');
  assert.match(main, /className="account-text"><span title=\{session\.account\?\.username\}>/);

  const button = declarations('.signout');
  assert.equal(button['flex-shrink'], '0');
  assert.equal(button['white-space'], 'nowrap');
  assert.equal(declarations('.avatar')['flex-shrink'], '0');
});

test('the sidebar keeps its fixed width and the account block is hidden in the narrow layout', () => {
  const sidebar = declarations('.sidebar');
  assert.equal(sidebar.width, '244px');
  assert.equal(sidebar['flex-shrink'], '0');
  assert.match(css, /@media\(max-width:760px\)\{[^@]*\.sidebar-bottom\{display:none\}|@media\(max-width:760px\)\{.*?\.nav-label,\.sidebar-bottom\{display:none\}/s);
});
