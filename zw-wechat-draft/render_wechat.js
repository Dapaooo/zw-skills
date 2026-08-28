#!/usr/bin/env node
/**
 * render_wechat.js — 公众号 HTML 渲染器
 * 读取内容 JSON → 输出公众号版 HTML（纯 inline CSS，16px 正文，自适应）
 *
 * 用法: node render_wechat.js <content.json> [output.html]
 *   不指定 output 则输出到 stdout
 */
const fs = require('fs');
const path = require('path');
const { getPalette } = require('./palettes');

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function renderBlock(block, p) {
  switch (block.type) {
    case 'intro':
      return `<p style="margin:0 0 20px;font-size:16px;line-height:1.8;color:${p.text};">${escapeHtml(block.text)}</p>`;

    case 'section': {
      let html = `<h2 style="margin:28px 0 14px;font-size:20px;font-weight:600;color:${p.text};letter-spacing:-0.02em;">${escapeHtml(block.title)}</h2>`;
      if (block.body) {
        const paras = block.body.split('\n\n').filter(s => s.trim());
        for (const para of paras) {
          html += `<p style="margin:0 0 16px;font-size:16px;line-height:1.8;color:${p.text};">${escapeHtml(para.trim())}</p>`;
        }
      }
      return html;
    }

    case 'highlight':
      return `<blockquote style="margin:24px 0;padding:12px 0 12px 16px;border-left:3px solid ${p.accent};font-size:17px;font-weight:500;color:${p.text};line-height:1.7;">${escapeHtml(block.text)}</blockquote>`;

    case 'quote':
      // 引用块（区别于 highlight 金句）：强调色文字 + 左边线，置于章节顶部或叙事流中
      return `<blockquote style="margin:24px 0;padding:12px 0 12px 16px;border-left:3px solid ${p.accent};font-size:16px;color:${p.accent};line-height:1.7;">${escapeHtml(block.text)}</blockquote>`;

    case 'divider':
      return `<hr style="border:none;border-top:1px solid ${p.rule};margin:28px 0;">`;

    case 'list': {
      const items = (block.items || []).map(item =>
        `<li style="font-size:16px;line-height:1.8;color:${p.text};margin-bottom:6px;">${escapeHtml(item)}</li>`
      ).join('');
      return `<ul style="margin:0 0 16px;padding-left:20px;list-style:none;">${items}</ul>`;
    }

    case 'item':
      return `<section style="margin-bottom:20px;"><p style="margin:0 0 4px;font-size:16px;font-weight:500;color:${p.text};">${escapeHtml(block.label)}</p><p style="margin:0;font-size:15px;line-height:1.7;color:${p.textMid};">${escapeHtml(block.body || '')}</p></section>`;

    case 'subtitle':
      return `<p style="margin:0 0 20px;font-size:13px;color:${p.textDim};letter-spacing:0.1em;text-transform:uppercase;">${escapeHtml(block.text)}</p>`;

    case 'footer':
      return `<p style="margin-top:32px;padding-top:20px;border-top:1px solid ${p.rule};font-size:16px;line-height:1.8;color:${p.text};">${escapeHtml(block.text)}</p>`;

    case 'endmark':
      return `<p style="text-align:right;font-size:14px;color:${p.accent};opacity:0.4;margin-top:20px;">${escapeHtml(block.text || '∎')}</p>`;

    default:
      return '';
  }
}

function renderWechatHtml(content) {
  const p = getPalette(content);
  const blocks = content.blocks || [];

  let bodyHtml = '';
  for (const block of blocks) {
    bodyHtml += renderBlock(block, p) + '\n';
  }

  // 外层容器：自适应宽度，手机阅读优化
  return `<section style="max-width:677px;margin:0 auto;padding:20px 16px;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Helvetica Neue',sans-serif;font-size:16px;line-height:1.8;color:${p.text};">
${bodyHtml}</section>`;
}

// CLI
function main() {
  const args = process.argv.slice(2);
  if (!args[0]) {
    console.error('用法: render_wechat.js <content.json> [output.html]');
    process.exit(1);
  }
  const jsonPath = path.resolve(args[0]);
  if (!fs.existsSync(jsonPath)) {
    console.error('文件不存在:', jsonPath);
    process.exit(1);
  }
  const content = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
  const html = renderWechatHtml(content);

  if (args[1]) {
    fs.writeFileSync(path.resolve(args[1]), html, 'utf8');
    console.log('OK:', path.resolve(args[1]));
  } else {
    process.stdout.write(html);
  }
}

module.exports = { renderWechatHtml };

if (require.main === module) main();
