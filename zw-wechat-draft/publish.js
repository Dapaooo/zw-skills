#!/usr/bin/env node
/**
 * publish.js — zw-wechat-draft 统一入口编排器
 * 读取内容 JSON → 渲染公众号 HTML + 封面 →（可选）推送草稿箱
 *
 * 用法:
 *   node publish.js --content <content.json> [--output-dir <dir>] [选项]
 *
 * 选项:
 *   --output-dir <dir>   输出目录（默认当前目录）
 *   --no-push            渲染封面+HTML 但不推送（预览模式）
 *
 * 说明：封面与 HTML 始终生成；仅当不带 --no-push 时调用 push_draft.js 推送。
 * 所有路径（截图脚本、推送脚本）均相对本技能目录，自包含、不依赖其他技能。
 */
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const { renderWechatHtml } = require('./render_wechat');
const { generateCoverHtml } = require('./render_cover');

const SKILL_DIR = path.join(process.env.HOME, '.workbuddy/skills/zw-wechat-draft');
const CAPTURE_SCRIPT = path.join(SKILL_DIR, 'assets/capture.js');
const NODE_BIN = process.execPath;

function parseArgs() {
  const args = process.argv.slice(2);
  const params = {};
  const flags = {};
  for (let i = 0; i < args.length; i++) {
    const key = args[i].replace(/^--/, '');
    if (key === 'no-push' || key === 'check-ip') {
      flags[key] = true;
    } else {
      params[key] = args[++i];
    }
  }
  return { params, flags };
}

function safeName(name) {
  return (name || 'article').replace(/[<>:"/\\|?*\n]/g, '_').slice(0, 60);
}

function screenshot(html, outPng, width, height, fullpage) {
  const tmpHtml = path.join('/tmp', `pub_${Date.now()}_${Math.random().toString(36).slice(2, 6)}.html`);
  fs.writeFileSync(tmpHtml, html, 'utf8');
  const fp = fullpage ? ' fullpage' : '';
  try {
    execSync(`"${NODE_BIN}" "${CAPTURE_SCRIPT}" "${tmpHtml}" "${outPng}" ${width} ${height}${fp}`, {
      stdio: 'pipe',
      timeout: 60000,
    });
  } finally {
    if (fs.existsSync(tmpHtml)) fs.unlinkSync(tmpHtml);
  }
}

const CONFIG_PATH = path.join(process.env.HOME, '.workbuddy/wechat_config.json');

// 直接请求微信 token 接口来探测当前出口 IP 是否命中 API 白名单。
// 比本地 curl ipify 更准：微信看到的「实际 IP」常与本机探测到的不同（经 VPN/代理时尤甚）。
function getEgressStatus() {
  let cfg;
  try {
    cfg = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
  } catch (e) {
    return { ok: false, reason: 'no-config', detail: e.message };
  }
  const { appId, appSecret } = cfg || {};
  if (!appId || !appSecret) {
    return { ok: false, reason: 'no-config' };
  }
  const url = `https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=${encodeURIComponent(appId)}&secret=${encodeURIComponent(appSecret)}`;
  let out;
  try {
    out = execSync(`curl -s --max-time 15 "${url}"`, { stdio: 'pipe', timeout: 20000 }).toString();
  } catch (e) {
    return { ok: false, reason: 'network', detail: e.message };
  }
  let data;
  try {
    data = JSON.parse(out);
  } catch {
    return { ok: false, reason: 'bad-response', detail: out.slice(0, 200) };
  }
  if (data.access_token) return { ok: true };
  if (data.errcode === 40164) {
    const m = (data.errmsg || '').match(/invalid ip\s+([\d.]+)/i);
    return { ok: false, reason: 'ip-not-whitelisted', ip: m ? m[1] : null, errmsg: data.errmsg };
  }
  return { ok: false, reason: 'other', errcode: data.errcode, errmsg: data.errmsg };
}

async function main() {
  const { params, flags } = parseArgs();

  // --check-ip 模式：仅校验白名单，不渲染不推送
  if (flags['check-ip']) {
    console.log('[IP预检] 探测微信 API 白名单命中情况 ...');
    const st = getEgressStatus();
    if (st.ok) {
      console.log('  ✓ 当前出口 IP 已命中白名单，可直接推送。');
      process.exit(0);
    }
    if (st.reason === 'ip-not-whitelisted') {
      console.log(`  ✗ 当前出口 IP ${st.ip} 不在白名单`);
      console.log('  → 加入: developers.weixin.qq.com/platform → 公众号 → 接口管理 → API IP 白名单');
      console.log('  → 加好后重跑 `node publish.js --check-ip` 复验，或重跑完整推送命令。');
      process.exit(2);
    }
    console.log('  ✗ 预检异常:', st.reason, st.errmsg || st.detail || '');
    process.exit(2);
  }

  const contentPath = params.content;
  if (!contentPath) {
    console.error('用法: publish.js --content <content.json> [--output-dir <dir>] [--no-push]');
    process.exit(1);
  }

  const content = JSON.parse(fs.readFileSync(path.resolve(contentPath), 'utf8'));
  const outDir = params['output-dir'] ? path.resolve(params['output-dir']) : process.cwd();
  fs.mkdirSync(outDir, { recursive: true });

  const baseName = safeName(content.title);
  const doPush = !flags['no-push'];

  const results = {};

  console.log('[A1] 渲染公众号 HTML ...');
  const html = renderWechatHtml(content);
  const htmlPath = path.join(outDir, `${baseName}_wechat.html`);
  fs.writeFileSync(htmlPath, html, 'utf8');
  results.wechatHtml = htmlPath;
  console.log('     ✓', htmlPath);

  console.log('[A2] 生成封面 ...');
  const coverPath = path.join(outDir, `${baseName}_cover.png`);
  const coverHtml = generateCoverHtml(content);
  screenshot(coverHtml, coverPath, 900, 500, false);
  results.cover = coverPath;
  console.log('     ✓', coverPath);

  if (doPush) {
    console.log('[A0] IP 白名单预检 ...');
    const st = getEgressStatus();
    if (!st.ok) {
      if (st.reason === 'ip-not-whitelisted') {
        console.error(`\n❌ 当前出口 IP ${st.ip} 不在微信 API 白名单，推送会被 40164 拦截。`);
        console.error('   请把它加入: developers.weixin.qq.com/platform → 公众号 → 接口管理 → API IP 白名单');
        console.error('   加好后重跑本命令即可（HTML/封面已渲染，无需重做）。');
      } else {
        console.error('\n❌ IP 预检未通过:', st.reason, st.errmsg || st.detail || '');
      }
      process.exit(1);
    }
    console.log('     ✓ 白名单命中，继续推送');

    console.log('[A3] 推送公众号草稿箱 ...');
    const pushScript = path.join(SKILL_DIR, 'push_draft.js');
    const title = (content.title || '').replace(/"/g, '\\"');
    const digest = (content.digest || '').replace(/"/g, '\\"');
    const updateArg = params.update ? ` --update "${params.update}"` : '';
    execSync(
      `"${NODE_BIN}" "${pushScript}" --content "${htmlPath}" --cover "${coverPath}" --title "${title}" --digest "${digest}"${updateArg}`,
      { stdio: 'inherit', timeout: 30000 }
    );
    results.pushed = true;
  }

  console.log('\n=========================');
  console.log('完成:');
  if (results.pushed) console.log('  [公众号] 草稿已推送 → mp.weixin.qq.com 草稿箱');
  if (results.wechatHtml) console.log('  [公众号] HTML:', results.wechatHtml);
  if (results.cover) console.log('  [封面]   PNG:', results.cover);
  console.log('=========================');
}

main().catch(err => {
  console.error('\n❌', err.message);
  process.exit(1);
});
