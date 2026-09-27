import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';
import { test } from 'node:test';

const navbarSource = readFileSync(
  new URL('../src/components/Navbar.jsx', import.meta.url),
  'utf8'
);

test('AI search results panel fits one event card and keeps internal scrolling', () => {
  const resultsPanelMatch = navbarSource.match(
    /<div className="([^"]*bg-gray-50[^"]*)">\s*\{isAiSearching/s
  );

  assert.ok(resultsPanelMatch, 'AI results panel container was not found');

  const classes = resultsPanelMatch[1];

  const classList = classes.split(/\s+/);

  assert.ok(classList.includes('h-[34rem]'));
  assert.ok(classList.includes('overflow-y-auto'));
  assert.ok(!classList.includes('max-h-[60vh]'));
});
