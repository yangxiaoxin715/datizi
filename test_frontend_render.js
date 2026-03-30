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
  extractFunctionSource('normalizeReportStructure', 'extractConclusionBlock'),
  extractFunctionSource('extractConclusionBlock', 'splitReportSections'),
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

const messy = `【结论】
状态：可以按当前水平讲
先抓：总数不变
开口：先问总共有多少本
##1.先别急着讲，这题先抓什么先抓“总数不变”。
##2.孩子最可能卡在哪卡在分母会变。`;

const normalized = sandbox.normalizeReportStructure(messy);
assert.ok(normalized.includes('\n## 1. 先别急着讲，这题先抓什么\n'));
assert.ok(normalized.includes('\n## 2. 孩子最可能卡在哪\n'));

const conclusion = sandbox.extractConclusionBlock(normalized);
assert.strictEqual(conclusion.status, '可以按当前水平讲');
assert.strictEqual(conclusion.focus, '总数不变');
assert.strictEqual(conclusion.opening, '先问总共有多少本');

const structuredSections = sandbox.splitReportSections(normalized);
assert.strictEqual(structuredSections.length, 2, 'structured markdown should still split into two sections');

console.log('frontend render tests passed');
