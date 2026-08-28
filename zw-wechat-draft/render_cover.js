#!/usr/bin/env node
/**
 * render_cover.js — 简单封面生成器
 * 读取内容 JSON 的 title + palette → 生成 900×500 HTML → 截图为 PNG
 * 独立于长图，秒级生成
 *
 * 用法: node render_cover.js <content.json> <output.png>
 */
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const { getPalette } = require('./palettes');

const SKILL_DIR = path.join(process.env.HOME, '.workbuddy/skills/zw-wechat-draft');
const CAPTURE_SCRIPT = path.join(SKILL_DIR, 'assets/capture.js');
const NODE_BIN = process.execPath;

function escapeHtml(text) {
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// 标题字号自适应：保证标题完整落在 900×500 中央的 1:1 安全区（500×500）内，
// 这样无论微信以横版（大图）还是 1:1（分享/次条小图）裁剪，标题都完整可见。
// 字号基线整体上调，标题越短字号越大，横版更易读；建议标题 ≤ 12 字（见 content-format.md）。
function calcTitleSize(title) {
  let w = 0;
  for (const ch of title) {
    w += ch.charCodeAt(0) > 0xff ? 1 : 0.5;
  }
  if (w <= 8) return 60;
  if (w <= 10) return 56;
  if (w <= 13) return 50;
  if (w <= 16) return 44;
  if (w <= 20) return 40;
  return 36;
}

function generateCoverHtml(content) {
  const p = getPalette(content);
  const title = content.title || '未命名';
  const subtitle = content.subtitle || content.content_type || '';
  const titleSize = calcTitleSize(title);
  const titleWeight = Array.from(title).reduce((s, ch) => s + (ch.charCodeAt(0) > 0xff ? 1 : 0.5), 0);
  if (titleWeight > 16) {
    console.warn(`[封面] 标题偏长（约 ${Math.round(titleWeight)} 字），横版字号会偏小，建议精简到 12 字以内：${title}`);
  }

  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { width: 900px; height: 500px; overflow: hidden; }
  .cover {
    width: 900px;
    height: 500px;
    background: ${p.bg};
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 0 210px;
    position: relative;
  }
  .title {
    font-family: 'Songti SC', 'STSong', 'PingFang SC', serif;
    font-size: ${titleSize}px;
    font-weight: 600;
    color: ${p.text};
    text-align: center;
    letter-spacing: -0.02em;
    line-height: 1.35;
    max-width: 480px;
  }
  .subtitle {
    font-family: 'PingFang SC', system-ui, sans-serif;
    font-size: 17px;
    font-weight: 400;
    color: ${p.textMid};
    margin-top: 18px;
    letter-spacing: 0.08em;
    text-align: center;
    max-width: 480px;
  }
  .corner {
    position: absolute;
    bottom: 32px;
    right: 40px;
    font-family: 'Menlo', 'SF Mono', monospace;
    font-size: 13px;
    color: ${p.textDim};
    letter-spacing: 0.05em;
  }
</style>
</head>
<body>
  <div class="cover">
    <div class="title">${escapeHtml(title)}</div>
    ${subtitle ? `<div class="subtitle">${escapeHtml(subtitle)}</div>` : ''}
    <div class="corner">${escapeHtml(content.author || '')}</div>
  </div>
</body>
</html>`;
}

function main() {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.error('用法: render_cover.js <content.json> <output.png>');
    process.exit(1);
  }
  const jsonPath = path.resolve(args[0]);
  const outPng = path.resolve(args[1]);

  if (!fs.existsSync(jsonPath)) {
    console.error('文件不存在:', jsonPath);
    process.exit(1);
  }

  const content = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
  const html = generateCoverHtml(content);

  // 写临时 HTML
  const tmpHtml = path.join('/tmp', `cover_${Date.now()}.html`);
  fs.writeFileSync(tmpHtml, html, 'utf8');

  // 用 capture.js 截图（900×500，非 fullpage）
  execSync(`"${NODE_BIN}" "${CAPTURE_SCRIPT}" "${tmpHtml}" "${outPng}" 900 500`, {
    stdio: 'pipe',
    timeout: 30000,
  });

  // 清理临时文件
  fs.unlinkSync(tmpHtml);
  console.log('OK:', outPng);
}

module.exports = { generateCoverHtml };

if (require.main === module) main();
