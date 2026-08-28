#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');
const { chromium } = require('playwright');

function usage() {
  console.error('Usage: node render_html_deck.cjs <deck.html> <output-dir> [--clean] [--width 1600] [--height 900] [--wait 250]');
  process.exit(1);
}

function option(name, fallback) {
  const i = process.argv.indexOf(name);
  return i >= 0 ? Number(process.argv[i + 1]) : fallback;
}

const inputArg = process.argv[2];
const outputArg = process.argv[3];
if (!inputArg || !outputArg) usage();

const input = path.resolve(inputArg);
const output = path.resolve(outputArg);
const clean = process.argv.includes('--clean');
const width = option('--width', 1600);
const height = option('--height', 900);
const waitMs = option('--wait', 250);

if (!fs.existsSync(input)) throw new Error(`Input not found: ${input}`);
fs.mkdirSync(output, { recursive: true });

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  const pageErrors = [];
  const consoleErrors = [];
  page.on('pageerror', error => pageErrors.push(String(error)));
  page.on('console', message => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });

  const url = new URL(pathToFileURL(input).href);
  if (clean) url.searchParams.set('clean', '1');
  url.hash = '1';
  await page.goto(url.href, { waitUntil: 'load' });
  await page.waitForTimeout(waitMs);

  const slideCount = await page.locator('.slide').count();
  if (!slideCount) throw new Error('No .slide elements found');

  const slides = [];
  const issues = [];

  for (let i = 1; i <= slideCount; i += 1) {
    await page.evaluate(n => { location.hash = String(n); }, i);
    await page.waitForTimeout(waitMs);
    const active = page.locator('.slide.active');
    if (await active.count() !== 1) {
      issues.push({ slide: i, type: 'active-slide-count', count: await active.count() });
      continue;
    }

    const metrics = await active.evaluate((el, viewport) => {
      const box = el.getBoundingClientRect();
      const stage = el.parentElement?.getBoundingClientRect();
      return {
        title: el.dataset.title || '',
        clientWidth: el.clientWidth,
        clientHeight: el.clientHeight,
        scrollWidth: el.scrollWidth,
        scrollHeight: el.scrollHeight,
        box: { x: box.x, y: box.y, width: box.width, height: box.height },
        stage: stage ? { x: stage.x, y: stage.y, width: stage.width, height: stage.height } : null,
        centered: stage ?
          Math.abs(stage.x + stage.width / 2 - viewport.width / 2) <= 2 &&
          Math.abs(stage.y + stage.height / 2 - viewport.height / 2) <= 2 : false
      };
    }, { width, height });

    if (metrics.scrollWidth > metrics.clientWidth + 1 || metrics.scrollHeight > metrics.clientHeight + 1) {
      issues.push({ slide: i, type: 'overflow', ...metrics });
    }
    if (!metrics.centered) issues.push({ slide: i, type: 'stage-not-centered', stage: metrics.stage });

    slides.push({ slide: i, ...metrics });
    await page.screenshot({ path: path.join(output, `page-${String(i).padStart(2, '0')}.png`) });
  }

  const visibleExportUi = clean
    ? await page.locator('.controls:visible,.help:visible,.progress:visible,.notes:visible,.overview:visible').count()
    : null;
  if (clean && visibleExportUi) issues.push({ type: 'visible-export-ui', count: visibleExportUi });

  const report = {
    input,
    output,
    clean,
    viewport: { width, height },
    slideCount,
    visibleExportUi,
    pageErrors,
    consoleErrors,
    issues,
    slides
  };
  fs.writeFileSync(path.join(output, 'render-report.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify({ slideCount, clean, visibleExportUi, pageErrors, consoleErrors, issues }, null, 2));
  await browser.close();
  if (pageErrors.length || issues.length) process.exitCode = 2;
})().catch(error => {
  console.error(error);
  process.exit(1);
});
