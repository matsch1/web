// Execute the actual filter controller against a small DOM fixture.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const categories = ['all', 'development', 'self-hosting', 'travel'];
const buttons = categories.map(filter => ({
  dataset: { filter },
  classList: { toggle() {} },
  setAttribute(name, value) { this[name] = value; },
  addEventListener(event, handler) { this.click = handler; },
}));
const n8n = { dataset: { category: 'development', categories: 'development self-hosting' } };
const legacy = { dataset: { category: 'development' } };
const hosting = { dataset: { category: 'self-hosting', categories: 'self-hosting' } };
const entries = [n8n, legacy, hosting];
const empty = {};
const filters = { querySelectorAll: () => buttons, nextElementSibling: empty };
const document = { querySelectorAll: selector => selector === '[data-content-filters]' ? [filters] : entries };
vm.runInNewContext(fs.readFileSync('assets/js/content-filters.js', 'utf8'), { document });
buttons[2].click();
assert.deepEqual(entries.map(entry => entry.hidden), [false, true, false]);
assert.equal(empty.hidden, true);
assert.equal(buttons[2]['aria-pressed'], 'true');
buttons[1].click();
assert.deepEqual(entries.map(entry => entry.hidden), [false, false, true]);
buttons[3].click();
assert.deepEqual(entries.map(entry => entry.hidden), [true, true, true]);
assert.equal(empty.hidden, false);
buttons[0].click();
assert.deepEqual(entries.map(entry => entry.hidden), [false, false, false]);
console.log('Multi-category, fallback, empty-state and reset checks passed.');
