import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { chromium } from "playwright";

import { getStoryboardChapter, walkthroughStoryboard } from "./walkthrough_storyboard.mjs";

const args = process.argv.slice(2);
const options = new Map();
for (let index = 0; index < args.length; index += 2) {
  options.set(args[index], args[index + 1]);
}

const outputPath = options.get("--output");
const frontendUrl = options.get("--url") ?? "http://127.0.0.1:4173/";

if (!outputPath) {
  throw new Error("--output is required");
}

const viewport = { width: 1480, height: 968 };
const capturePlan = walkthroughStoryboard.capturePlan;

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function installCinematicCursor(page) {
  await page.addStyleTag({
    content: `
      html, body {
        cursor: none !important;
      }
      #tta-cursor {
        position: fixed;
        left: 0;
        top: 0;
        width: 36px;
        height: 36px;
        pointer-events: none;
        transform: translate(-4px, -2px);
        z-index: 2147483647;
      }
      #tta-cursor svg {
        width: 100%;
        height: 100%;
        filter: drop-shadow(0 10px 20px rgba(0, 0, 0, 0.28));
      }
      #tta-cursor .arrow-fill {
        fill: #111111;
      }
      #tta-cursor .arrow-stroke {
        fill: none;
        stroke: rgba(255, 255, 255, 0.9);
        stroke-width: 1.4;
        stroke-linejoin: round;
      }
      #tta-cursor-ring {
        position: fixed;
        left: 0;
        top: 0;
        width: 28px;
        height: 28px;
        margin-left: -14px;
        margin-top: -14px;
        border-radius: 999px;
        pointer-events: none;
        z-index: 2147483646;
        opacity: 0;
        transform: scale(0.72);
        border: 2px solid rgba(255, 239, 200, 0.82);
        background: rgba(255, 244, 216, 0.08);
        box-shadow: 0 0 0 12px rgba(255, 244, 216, 0.06);
      }
    `,
  });

  await page.evaluate(() => {
    if (window.__ttaCursorReady) return;

    const cursor = document.createElement("div");
    cursor.id = "tta-cursor";
    cursor.innerHTML = `
      <svg viewBox="0 0 34 34" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <path class="arrow-fill" d="M4 3L4 28L11.2 21.1L16.4 32L21.8 29.5L16.9 18.9L27.9 18.9L4 3Z"/>
        <path class="arrow-stroke" d="M4 3L4 28L11.2 21.1L16.4 32L21.8 29.5L16.9 18.9L27.9 18.9L4 3Z"/>
      </svg>
    `;

    const ring = document.createElement("div");
    ring.id = "tta-cursor-ring";

    document.body.appendChild(ring);
    document.body.appendChild(cursor);

    const move = (x, y) => {
      cursor.style.left = `${x}px`;
      cursor.style.top = `${y}px`;
      ring.style.left = `${x}px`;
      ring.style.top = `${y}px`;
    };

    document.addEventListener("mousemove", (event) => {
      move(event.clientX, event.clientY);
    });

    document.addEventListener("mousedown", () => {
      ring.style.opacity = "0.88";
      ring.style.transform = "scale(1.16)";
    });

    document.addEventListener("mouseup", () => {
      ring.style.opacity = "0";
      ring.style.transform = "scale(0.72)";
    });

    move(220, 180);
    window.__ttaCursorReady = true;
  });
}

async function centerOf(locator) {
  const box = await locator.boundingBox();
  if (!box) {
    throw new Error("Could not resolve locator bounding box");
  }
  return {
    x: box.x + box.width / 2,
    y: box.y + box.height / 2,
  };
}

async function moveTo(page, locator, steps = 24) {
  const { x, y } = await centerOf(locator);
  await page.mouse.move(x, y, { steps });
  return { x, y };
}

async function clickLocator(page, locator, { pauseBefore = 130, pauseAfter = 180, steps = 24 } = {}) {
  await moveTo(page, locator, steps);
  await wait(pauseBefore);
  await locator.click();
  await wait(pauseAfter);
}

async function selectOption(page, selector, value, pace = capturePlan.selection) {
  const locator = page.locator(selector);
  await clickLocator(page, locator, {
    pauseBefore: pace.pauseBeforeMs,
    pauseAfter: pace.pauseAfterMs,
    steps: pace.moveSteps,
  });
  await page.selectOption(selector, value);
  await wait(pace.postSelectHoldMs);
}

async function typeInto(page, selector, value, pace = capturePlan.typedField) {
  const locator = page.locator(selector);
  await moveTo(page, locator, pace.moveSteps);
  await wait(pace.pauseBeforeClickMs);
  await locator.click();
  await wait(pace.pauseAfterClickMs);
  await locator.press("Control+A");
  await locator.press("Delete");
  await page.keyboard.type(value, { delay: pace.keyDelayMs });
  await wait(pace.pauseAfterTypeMs);
}

async function smoothScrollTo(page, locator, settleMs = capturePlan.resultBeat.scrollSettleMs) {
  const handle = await locator.elementHandle();
  if (!handle) {
    throw new Error("Could not resolve element handle for smooth scroll");
  }
  const targetTop = await handle.evaluate((element) => {
    const rect = element.getBoundingClientRect();
    return Math.max(0, window.scrollY + rect.top - 120);
  });
  await page.evaluate((top) => {
    window.scrollTo({ top, behavior: "smooth" });
  }, targetTop);
  await wait(settleMs);
}

async function focusResultChapter(page, chapterId, labelText) {
  const chapter = getStoryboardChapter(chapterId);
  const locator = page.locator(".row-label", { hasText: labelText }).first();

  await smoothScrollTo(page, locator);
  await moveTo(page, locator, capturePlan.resultBeat.focusMoveSteps);
  await wait(chapter.holdMs);
}

async function runSequence(page) {
  await page.goto(frontendUrl, { waitUntil: "networkidle" });
  await page.locator("#guided-payer").waitFor();
  await installCinematicCursor(page);
  await page.mouse.move(capturePlan.intro.initialCursor.x, capturePlan.intro.initialCursor.y, {
    steps: capturePlan.intro.initialCursor.steps,
  });
  await wait(capturePlan.intro.initialHoldMs);

  await selectOption(page, "#guided-payer", "CN");
  await selectOption(page, "#guided-payee", "NL");
  await selectOption(page, "#guided-income-type", "dividends");

  await typeInto(page, "#guided-fact-direct_holding_percentage", "30");
  await typeInto(page, "#guided-fact-payment_date", "2026-03-01");
  await typeInto(page, "#guided-fact-holding_period_months", "14");
  await selectOption(page, "#guided-fact-beneficial_owner_confirmed", "yes", capturePlan.supportingSelect);
  await selectOption(page, "#guided-fact-pe_effectively_connected", "no", capturePlan.supportingSelect);
  await selectOption(page, "#guided-fact-holding_structure_is_direct", "yes", capturePlan.supportingSelect);

  const runButton = page.getByRole("button", { name: "Run Guided Review" });
  await clickLocator(page, runButton, {
    pauseBefore: capturePlan.runAction.pauseBeforeMs,
    pauseAfter: capturePlan.runAction.pauseAfterMs,
    steps: capturePlan.runAction.moveSteps,
  });

  await focusResultChapter(page, "treaty_branch", "Treaty Provision");
  await focusResultChapter(page, "source_chain", "Source Chain");
  await focusResultChapter(page, "workflow_handoff", "Workflow Handoff");
  await focusResultChapter(page, "final_boundary", "What This Review Means");
}

const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), "tta-playwright-video-"));
const browser = await chromium.launch({
  channel: "chrome",
  headless: true,
});

const context = await browser.newContext({
  viewport,
  recordVideo: {
    dir: tempDir,
    size: viewport,
  },
  deviceScaleFactor: 1,
  colorScheme: "light",
});

const page = await context.newPage();
const video = page.video();

try {
  await runSequence(page);
} finally {
  await context.close();
  await browser.close();
}

if (!video) {
  throw new Error("Playwright did not create a walkthrough video");
}

const recordedPath = await video.path();
await fs.copyFile(recordedPath, outputPath);
console.log(outputPath);
