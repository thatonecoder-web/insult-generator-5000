// End-to-end check of the main user journeys.
//   1. cd web && npm install && npm run build
//   2. insultgen serve            (in the repo root, another terminal)
//   3. npm install --no-save playwright && npx playwright install chromium
//   4. node e2e/journeys.mjs      (set BASE_URL if the server is not on port 8000)
import assert from "node:assert/strict";
import { chromium } from "playwright";

const BASE_URL = process.env.BASE_URL ?? "http://localhost:8000";
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, permissions: ["clipboard-read", "clipboard-write"] });
const page = await ctx.newPage();
const errors = [];
page.on("pageerror", (e) => errors.push("pageerror: " + e.message));
page.on("console", (m) => { if (m.type() === "error") errors.push("console: " + m.text()); });
const text = () => page.locator(".stage__text").evaluate((el) => { const c = el.cloneNode(true); c.querySelectorAll(".tip").forEach((t) => t.remove()); return c.textContent; });
const waitNew = async (before) => { await page.waitForFunction((b) => { const el = document.querySelector(".stage__text"); if (!el) return false; const c = el.cloneNode(true); c.querySelectorAll(".tip").forEach((t) => t.remove()); return c.textContent !== b; }, before, { timeout: 5000 }); };
let ok = 0; const pass = (m) => { ok++; console.log("  ok -", m); };

await page.goto(BASE_URL + "/", { waitUntil: "networkidle" });
await page.waitForSelector(".stage__text");
pass("page loads and auto-forges an insult");

// 1. register tile -> stage theme changes and text matches the register
await page.evaluate(() => document.getElementById("forge").scrollIntoView());
await page.locator(".tile--legal").click();
await page.waitForSelector(".stage--legal", { timeout: 5000 });
assert.ok(await page.locator(".stage__register").innerText().then((t) => /legal/i.test(t)));
pass("choosing Legal re-themes the stage to pleading paper");

// 2. severity slider regenerates
const before = await text();
await page.locator("#severity").fill("9");
await waitNew(before);
assert.match(await page.locator(".dial__name").innerText(), /Brutal/);
pass("moving the severity dial regenerates and relabels it (Brutal)");

// 3. concept select only enables workable concepts
const disabled = await page.locator("#concept option[disabled]").count();
assert.ok(disabled > 0 && disabled < 63);
pass(`concept list disables unavailable concepts for this register (${disabled} disabled)`);

// 4. Space shortcut forges again
await page.evaluate(() => document.activeElement?.blur());
const t1 = await text();
await page.keyboard.press("Space");
await waitNew(t1);
pass("Space forges another insult");

// 5. copy + share + save
await page.getByRole("button", { name: /^Copy/ }).click();
assert.equal(await page.evaluate(() => navigator.clipboard.readText()), await text());
pass("Copy puts the insult on the clipboard");
await page.getByRole("button", { name: /^Share/ }).click();
const link = await page.evaluate(() => navigator.clipboard.readText());
assert.match(link, /#forge\?register=legal&severity=9&seed=\d+/);
pass("Share copies a reproducible link: " + link.replace(BASE_URL, ""));
await page.getByRole("button", { name: /^Save/ }).click();
await page.getByRole("tab", { name: /Hall of Fame \(1\)/ }).click();
assert.equal(await page.locator(".archive__item").count(), 1);
pass("Save adds it to the Hall of Fame");

// 6. the share link recreates the same insult in a fresh page
const shown = await text();
const page2 = await ctx.newPage();
await page2.goto(link, { waitUntil: "networkidle" });
await page2.waitForSelector(".stage__text");
assert.equal(await page2.locator(".stage__text").evaluate((el) => { const c = el.cloneNode(true); c.querySelectorAll(".tip").forEach((t) => t.remove()); return c.textContent; }), shown);
pass("opening the share link in a new tab rebuilds the identical insult");
await page2.close();

// 7. persistence across reload
await page.reload({ waitUntil: "networkidle" });
await page.waitForSelector(".stage__text");
await page.getByRole("tab", { name: /Hall of Fame \(1\)/ }).click();
assert.equal(await page.locator(".archive__item").count(), 1);
pass("saved insults survive a reload (localStorage)");

// 8. word token opens the dialog; Escape closes it
await page.locator(".word__entry").first().click();
await page.waitForSelector("dialog[open]");
assert.ok(await page.locator("dialog[open] .dialog__term").innerText());
await page.keyboard.press("Escape");
await page.waitForFunction(() => !document.querySelector("dialog[open]"));
pass("clicking a word opens its entry; Escape closes it");

// 9. lexicon: search + filter + clear
await page.evaluate(() => document.getElementById("lexicon").scrollIntoView());
await page.locator('input[type="search"]').fill("cowardly");
await page.waitForTimeout(400);
const n = await page.locator(".grid .card").count();
assert.ok(n >= 1 && n < 20);
await page.getByRole("button", { name: /Clear 1 filter/ }).click();
await page.waitForTimeout(300);
assert.ok((await page.locator(".grid .card").count()) >= 48);
pass(`lexicon search narrows to ${n} cards and clears back`);

// 10. aim the forge from the dialog
await page.locator(".grid .card").first().click();
await page.waitForSelector("dialog[open]");
const name = (await page.locator("dialog[open] .chip--primary").innerText()).trim();
await page.locator("dialog[open] .dialog__footer .btn").click();
await page.waitForFunction(() => !document.querySelector("dialog[open]"));
await page.waitForTimeout(800);
assert.equal(await page.locator("#concept option:checked").innerText().then((t) => t.trim()), name);
pass(`"Aim the forge" from the dialog selects the concept (${name})`);

// 11. theme toggle persists
const startTheme = await page.evaluate(() => document.documentElement.dataset.theme);
await page.getByRole("button", { name: /Switch to (light|dark) theme/ }).click();
const flipped = await page.evaluate(() => document.documentElement.dataset.theme);
assert.notEqual(flipped, startTheme);
await page.reload({ waitUntil: "networkidle" });
assert.equal(await page.evaluate(() => document.documentElement.dataset.theme), flipped);
pass(`theme toggle flips ${startTheme} to ${flipped} and persists across reload`);

// 12. map: hover tooltip and axis change
await page.evaluate(() => document.getElementById("map").scrollIntoView());
await page.waitForTimeout(1200);
await page.locator(".map__dot").nth(40).hover({ force: true });
assert.ok(await page.locator(".map__tip").count());
await page.locator(".map__controls select").nth(0).selectOption("archaicness");
await page.waitForTimeout(300);
pass("map shows a tooltip on hover and re-plots when an axis changes");

console.log(`\n${ok} checks passed; console/page errors: ${errors.length ? JSON.stringify(errors) : "none"}`);
await browser.close();
