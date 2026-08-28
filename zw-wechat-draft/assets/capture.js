#!/usr/bin/env node

const path = require('path');
const fs = require('fs');

function loadPlaywright() {
  const home = process.env.HOME;
  const candidates = [
    path.join(home, '.workbuddy/binaries/node/workspace/node_modules'),
    path.join(home, '.workbuddy/skills/zw-card/node_modules'),
  ];
  for (const dir of candidates) {
    try {
      const req = require('module').createRequire(path.join(dir, 'index.js'));
      return req('playwright');
    } catch { /* try next */ }
  }
  return require('playwright'); // 最后兜底，失败会抛出明确错误
}

async function main() {
  const args = process.argv.slice(2);
  const htmlPath = args[0];
  const outputPath = args[1];
  const width = parseInt(args[2]) || 1200;
  const height = parseInt(args[3]) || 1600;
  const fullpage = args[4] === 'fullpage';

  if (!htmlPath || !outputPath) {
    console.error('Usage: node capture.js <html> <png> [width] [height] [fullpage]');
    process.exit(1);
  }

  const resolvedHtml = path.resolve(htmlPath);
  const logoUrl = 'file://' + path.resolve(__dirname, 'avatar.png');

  let content = fs.readFileSync(resolvedHtml, 'utf8');
  if (content.includes('{{LOGO}}')) {
    content = content.replace(/\{\{LOGO\}\}/g, logoUrl);
    fs.writeFileSync(resolvedHtml, content, 'utf8');
  }

  let chromium;
  try {
    chromium = loadPlaywright().chromium;
  } catch (e) {
    console.error('Playwright not found. 请先安装: npx playwright install chromium');
    console.error(e.message);
    process.exit(1);
  }

  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width, height: fullpage ? 800 : height });

  const fileUrl = 'file://' + resolvedHtml;
  await page.goto(fileUrl, { waitUntil: 'networkidle' });
  await page.waitForTimeout(500);

  if (fullpage) {
    const bodyHeight = await page.evaluate(() => document.body.scrollHeight);
    await page.setViewportSize({ width, height: bodyHeight });
    await page.waitForTimeout(300);
    await page.screenshot({
      path: path.resolve(outputPath),
      type: 'png',
      clip: { x: 0, y: 0, width, height: bodyHeight }
    });
  } else {
    await page.screenshot({
      path: path.resolve(outputPath),
      type: 'png',
      clip: { x: 0, y: 0, width, height }
    });
  }

  await browser.close();
  console.log('OK: ' + path.resolve(outputPath));
}

main().catch(err => {
  console.error(err.message);
  process.exit(1);
});
