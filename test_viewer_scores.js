// Exercise the viewer's real score/sort/render functions without a browser.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const html = fs.readFileSync(`${__dirname}/viewer/index.html`, "utf8");
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
new vm.Script(script); // Compile the whole viewer, including unrelated routes.
const section = (start, end) => script.slice(script.indexOf(start), script.indexOf(end));
const context = vm.createContext({
  SCORER_LABELS: { claude: "Claude", chatgpt: "ChatGPT" },
  tree: { scorers: ["claude", "chatgpt"], conjectures: [] },
  escapeHtml: s => s.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])),
});
vm.runInContext(section("/* ---------- scores ---------- */", "/* ---------- navigation ---------- */")
  + section("function cardHtml", "function catalogMatches")
  + section("/* ---------- score page ---------- */", "/* ---------- routing ---------- */"), context);
const data = {
  assessment: { targets: ["004", "004-3"], label: "004 · 004-3 <통합>" },
  claude: { score: 58, version: "0.6", reason: "old" },
  chatgpt: { score: 62, version: "0.11", targets: ["004-3", "004"], reason: "bundle" },
};
const card = { id: "004", dir: "conjectures/004-test", title: "Test", version: "0.11",
  scores: data, assessment: data.assessment, average: 62 };
context.card = card;
context.tree.conjectures = [card];
assert.equal(vm.runInContext("scoreOf(card, 'claude')", context), null);
assert.equal(vm.runInContext("scoreOf(card, 'chatgpt')", context), 62);
assert.equal(vm.runInContext("gapOf(card)", context), null);
const scorePage = context.renderScorePage(JSON.stringify(data), `${card.dir}/score.json`);
assert.match(scorePage, /hero-num">62/);
assert.match(scorePage, /Claude/);
assert.match(scorePage, /sc-num">58/);
assert.match(scorePage, /다른 대상의 평가, 평균 제외/);
assert.match(scorePage, /&lt;통합&gt;/);
assert.doesNotMatch(scorePage, /<통합>/);
assert.match(context.cardHtml(card, 1), /다른 대상/);
assert.match(context.cardHtml(card, 1), /004 · 004-3/);
const legacy = { id: "005", scores: { claude: { score: 60 }, chatgpt: { score: 64 } }, average: 62 };
context.legacy = legacy;
assert.equal(vm.runInContext("scoreOf(legacy, 'claude')", context), 60);
assert.equal(vm.runInContext("gapOf(legacy)", context), 4);
const sortedIds = vm.runInContext("sorted([card, legacy], 'claude').map(c => c.id).join(',')", context);
assert.equal(sortedIds, "005,004");
const unscored = { ...data, chatgpt: null };
const emptyPage = context.renderScorePage(JSON.stringify(unscored), `${card.dir}/score.json`);
assert.match(emptyPage, /현재 평가 대상에 매긴 점수가 아직 없습니다/);
console.log("Viewer score scope, sorting, preservation and rendering checks passed.");
