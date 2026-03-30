const fs = require('fs');
const vm = require('vm');
const assert = require('assert');

const html = fs.readFileSync('/Users/yangming/datizi/templates/index.html', 'utf8');

function extractFunctionSource(name, nextName) {
  const pattern = new RegExp(
    `function ${name}\\([^]*?\\n  \\}\\n\\n  function ${nextName}`,
    'm'
  );
  const match = html.match(pattern);
  if (!match) {
    throw new Error(`Could not find function ${name}`);
  }
  return match[0].replace(new RegExp(`\\n\\n  function ${nextName}$`), '');
}

const sandbox = {};
vm.createContext(sandbox);

const source = [
  extractFunctionSource('sanitizeMathText', 'splitReportSections'),
  extractFunctionSource('splitReportSections', 'escapeHtml'),
].join('\n\n');

vm.runInContext(source, sandbox);

const input = `## 先讲什么
先抓总数
## 孩子会卡在哪
分母会乱`;
const cleaned = sandbox.sanitizeMathText(input);
assert.ok(
  cleaned.includes('\n##'),
  'sanitizeMathText should preserve line breaks before section headings'
);

const sections = sandbox.splitReportSections(input);
assert.strictEqual(sections.length, 2, 'splitReportSections should return two sections');
assert.strictEqual(sections[0].title, '先讲什么');
assert.strictEqual(sections[1].title, '孩子会卡在哪');

console.log('frontend render tests passed');
