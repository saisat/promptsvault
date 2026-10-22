// Renderer tests: pulls inline()/md() out of template.html and checks them.
// Run from the skill folder: node tests/test_renderer.js
const fs = require("fs");
const path = require("path");

const html = fs.readFileSync(path.join(__dirname, "..", "template.html"), "utf8");
const js = html.match(/<script>([\s\S]*)<\/script>/)[1];
const segment = js.slice(js.indexOf("const esc"), js.indexOf("function matches"));
const DATA = { prompts: [{ slug: "be-my-ruthless-mentor", title: "Be my ruthless mentor", aliases: ["Ruthless mentor alias"] }] };
const { md, fillPrompt } = new Function("DATA", `${segment}; return { md, inline, fillPrompt };`)(DATA);

// Whitespace between tags is not significant, so compare without it.
const render = (input) => md(input).replace(/>\s*\n\s*</g, "><").replace(/\n</g, "<");

let failures = 0;
function check(name, input, predicate) {
  const out = render(input);
  const ok = predicate(out);
  if (!ok) failures++;
  console.log(`${ok ? "PASS" : "FAIL"} ${name.padEnd(28)}${ok ? "" : "  -> " + out.replace(/\n/g, "\\n")}`);
}

check("alias link", "[[Ruthless mentor alias]]", (o) => o.includes('data-go="be-my-ruthless-mentor"') && o.includes(">Ruthless mentor alias<"));
check("title link, any case", "[[be my RUTHLESS mentor]]", (o) => o.includes('data-go="be-my-ruthless-mentor"'));
check("display text", "[[be-my-ruthless-mentor|click me]]", (o) => o.includes(">click me</a>"));
check("unresolved link", "[[nope]]", (o) => o === "<p>nope</p>");
check("embed of a prompt", "![[be-my-ruthless-mentor]]", (o) => o.includes('class="embed"') && o.includes("data-go"));
check("embed of other file", "![[diagram.png]]", (o) => o.includes('class="embed">↪ diagram.png<'));
check("table", "| a | b |\n|---|:-:|\n| 1 | 2 |", (o) => o.includes("<th>a</th>") && o.includes("<td>2</td>") && !o.includes("|"));
check("table, 3 columns", "| h1 | h2 | h3 |\n|:--|:-:|--:|\n| 1 | 2 | 3 |", (o) => o.includes("<th>h3</th>") && o.includes("<td>3</td>"));
check("pipe line + rule is no table", "a | b\n---", (o) => !o.includes("<table>") && o.includes("<hr>"));
check("italic with stars", "an *italic* word", (o) => o.includes("<em>italic</em>"));
check("italic with underscores", "an _italic_ word", (o) => o.includes("<em>italic</em>"));
check("snake_case is not italic", "use question_id and some_other_id", (o) => !o.includes("<em>"));
check("bold", "**bold**", (o) => o.includes("<strong>bold</strong>"));
check("bold and italic together", "**bold** and *it*", (o) => o.includes("<strong>bold</strong>") && o.includes("<em>it</em>"));
check("highlight", "==marked==", (o) => o.includes("<mark>marked</mark>"));
check("block id hidden", "A paragraph. ^my-id", (o) => o === "<p>A paragraph.</p>");
check("footnote", "text[^1]\n\n[^1]: the note", (o) => o.includes("<sup>1</sup>") && o.includes('<ol class="fn"><li>the note</li></ol>'));
check("nested list", "- a\n  - b\n- c", (o) => o === "<ul><li>a<ul><li>b</li></ul></li><li>c</li></ul>");
check("ordered list with sub-bullet", "1. one\n2. two\n   - sub", (o) => o.startsWith("<ol><li>one</li><li>two<ul><li>sub</li></ul></li></ol>"));
check("horizontal rule", "above\n\n---\n\nbelow", (o) => o.includes("<hr>"));
check("callout", "> [!warning] Careful\n> body **x**", (o) => o.includes("callout-warning") && o.includes("<strong>x</strong>"));
check("blockquote", "> plain quote", (o) => o.includes("<blockquote>"));
check("code fence is verbatim", "```\n%%keep%% <b>&\n```", (o) => o.includes("%%keep%% &lt;b&gt;&amp;"));
check("inline code is not formatted", "`*not italic*`", (o) => o.includes("<code>*not italic*</code>"));
check("external link", "[x](https://a.com/?q=1&r=2)", (o) => o.includes('href="https://a.com/?q=1&amp;r=2"'));
check("XSS: script tag", "<script>alert(1)</script>", (o) => !o.includes("<script>"));
check("XSS: link label", "[[x<img src=x onerror=alert(1)>]]", (o) => !o.includes("<img"));
check("XSS: table cell", "| <b>x</b> |\n|---|\n| <i>y</i> |", (o) => !o.includes("<b>") && !o.includes("<i>"));

// fillPrompt must match fill() in the prompt-find skill (tests/test_find.py has the same cases).
function same(name, actual, expected) {
  const ok = actual === expected;
  if (!ok) failures++;
  console.log(`${ok ? "PASS" : "FAIL"} ${name.padEnd(28)}${ok ? "" : "\n  got:      " + JSON.stringify(actual) + "\n  expected: " + JSON.stringify(expected)}`);
}
same("fill: inline + wrappers",
  fillPrompt("Industry: <industry>\nProduct: <product>\n\nMiddle line.\n\n<industry>\n</industry>\n\n<product>\n</product>", [["<industry>", "Banking"], ["<product>", "Wallet"]]),
  "Industry: Banking\nProduct: Wallet\n\nMiddle line.\n\n<industry>Banking</industry>\n\n<product>Wallet</product>");
same("fill: no swallowed text", fillPrompt("Start <x> middle one.\nMiddle two.\n<x>hint</x>\nEnd.", [["<x>", "V"]]), "Start V middle one.\nMiddle two.\n<x>V</x>\nEnd.");
same("fill: wrapper hint text", fillPrompt("About the <cat> market.\n<cat>Name the category (for example: X)</cat>", [["<cat>", "Pets"]]), "About the Pets market.\n<cat>Pets</cat>");
same("fill: bracket field", fillPrompt("Company:\n[Company name]", [["[Company name]", "Acme"]]), "Company:\nAcme");
same("fill: nothing to fill", fillPrompt("Keep <x> as is.", []), "Keep <x> as is.");
same("fill: value with $ and regex chars", fillPrompt("Cost: <c>\n<c>\n</c>", [["<c>", "$1 (x+y)*"]]), "Cost: $1 (x+y)*\n<c>$1 (x+y)*</c>");
same("fill: name with regex chars", fillPrompt("A <a.b> B\n<a.b></a.b>", [["<a.b>", "V"]]), "A V B\n<a.b>V</a.b>");

console.log(failures ? `FAILED: ${failures}` : "ALL PASS");
process.exit(failures ? 1 : 0);
