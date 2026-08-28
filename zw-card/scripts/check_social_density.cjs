const { chromium } = require('playwright');
const path = require('path');
const { pathToFileURL } = require('url');

async function inspect(file) {
  const browser = await chromium.launch({headless: true});
  const page = await browser.newPage({viewport: {width: 1080, height: 2200}, deviceScaleFactor: 1});
  await page.goto(pathToFileURL(path.resolve(file)).href, {waitUntil: 'networkidle'});
  const metrics = await page.evaluate(() => {
    const rect = selector => document.querySelector(selector)?.getBoundingClientRect();
    const quote = rect('.quote');
    const footer = rect('footer');
    const title = rect('h1');
    if (!quote || !footer || !title) throw new Error('missing required social-card elements');
    const gap = Math.round(footer.top - quote.bottom);
    const content = Math.round(quote.bottom - title.top);
    const available = Math.round(footer.top - title.top);
    return {gap, coverage: Math.round(content / available * 100)};
  });
  await browser.close();
  const pass = metrics.gap >= 32 && metrics.gap <= 96 && metrics.coverage >= 80;
  console.log(`${pass ? 'PASS' : 'FAIL'} ${file} gap=${metrics.gap}px coverage=${metrics.coverage}%`);
  return pass;
}

(async () => {
  if (process.argv.length < 3) throw new Error('usage: node check_social_density.cjs <html> [html...]');
  const results = await Promise.all(process.argv.slice(2).map(inspect));
  process.exitCode = results.every(Boolean) ? 0 : 1;
})().catch(error => { console.error(error); process.exit(1); });
