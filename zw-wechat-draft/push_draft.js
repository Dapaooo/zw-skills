#!/usr/bin/env node
/**
 * 微信公众号草稿箱推送工具
 * 将文章 HTML 内容 + 封面图推送到公众号草稿箱
 *
 * 用法:
 *   node push_draft.js --content <html路径> --cover <图片路径> --title <标题> \
 *     [--author <作者>] [--digest <摘要>] [--embed-image <图片路径>]
 *
 * 配置文件: ~/.workbuddy/wechat_config.json
 *   { "appId": "wx...", "appSecret": "..." }
 */

const fs = require('fs');
const path = require('path');

const CONFIG_PATH = path.join(process.env.HOME, '.workbuddy/wechat_config.json');

function loadConfig() {
  if (!fs.existsSync(CONFIG_PATH)) {
    console.error('❌ 配置文件不存在:', CONFIG_PATH);
    console.error('   请创建配置文件: { "appId": "你的AppID", "appSecret": "你的AppSecret" }');
    process.exit(1);
  }
  const raw = fs.readFileSync(CONFIG_PATH, 'utf8');
  let config;
  try {
    config = JSON.parse(raw);
  } catch (e) {
    console.error('❌ 配置文件 JSON 格式错误:', e.message);
    process.exit(1);
  }
  if (!config.appId || !config.appSecret || config.appSecret === 'YOUR_APP_SECRET') {
    console.error('❌ 请先填写 appId 和 appSecret:', CONFIG_PATH);
    process.exit(1);
  }
  return config;
}

// 1. 获取 access_token
async function getAccessToken(appId, appSecret) {
  const url = `https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=${appId}&secret=${appSecret}`;
  const res = await fetch(url);
  const data = await res.json();
  if (data.errcode) {
    if (data.errcode === 40164) {
      // 微信 errmsg 格式: "invalid ip 182.102.83.83 ipv6 ::ffff:182.102.83.83, not in whitelist"
      const ipMatch = data.errmsg.match(/invalid ip (\S+)/);
      const actualIp = ipMatch ? ipMatch[1] : '未知';
      throw new Error(
        `IP不在白名单 [40164]\n` +
        `   微信看到的实际IP: ${actualIp}\n` +
        `   请将此IP加入白名单: developers.weixin.qq.com/platform → 公众号 → 接口管理 → API IP白名单`
      );
    }
    if (data.errcode === 40113) {
      throw new Error(`AppSecret不正确 [40113]，请检查配置文件中的 appSecret`);
    }
    throw new Error(`获取access_token失败 [${data.errcode}]: ${data.errmsg}`);
  }
  return data.access_token;
}

// 2. 上传封面图（永久素材）
async function uploadCoverImage(accessToken, imagePath) {
  const url = `https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=${accessToken}&type=image`;
  const buffer = fs.readFileSync(imagePath);
  const ext = path.extname(imagePath).toLowerCase();
  const mimeType = ext === '.png' ? 'image/png' : 'image/jpeg';
  const blob = new Blob([buffer], { type: mimeType });
  const formData = new FormData();
  formData.append('media', blob, path.basename(imagePath));

  const res = await fetch(url, { method: 'POST', body: formData });
  const data = await res.json();
  if (data.errcode) {
    throw new Error(`上传封面图失败 [${data.errcode}]: ${data.errmsg}`);
  }
  return data.media_id;
}

// 3. 上传正文内图片（获取可在content中使用的URL）
async function uploadContentImage(accessToken, imagePath) {
  const url = `https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token=${accessToken}`;
  const buffer = fs.readFileSync(imagePath);
  const ext = path.extname(imagePath).toLowerCase();
  const mimeType = ext === '.png' ? 'image/png' : 'image/jpeg';
  const blob = new Blob([buffer], { type: mimeType });
  const formData = new FormData();
  formData.append('media', blob, path.basename(imagePath));

  const res = await fetch(url, { method: 'POST', body: formData });
  const data = await res.json();
  if (data.errcode) {
    throw new Error(`上传正文图片失败 [${data.errcode}]: ${data.errmsg}`);
  }
  return data.url;
}

// 4. 新增草稿
async function addDraft(accessToken, article) {
  const url = `https://api.weixin.qq.com/cgi-bin/draft/add?access_token=${accessToken}`;
  const body = { articles: [article] };
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (data.errcode) {
    throw new Error(`新增草稿失败 [${data.errcode}]: ${data.errmsg}`);
  }
  return data.media_id;
}

// 4b. 更新已有草稿（按 media_id 覆盖，不产生重复草稿）
async function updateDraft(accessToken, mediaId, article) {
  const url = `https://api.weixin.qq.com/cgi-bin/draft/update?access_token=${accessToken}`;
  const body = { media_id: mediaId, index: 0, articles: article };
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (data.errcode) {
    throw new Error(`更新草稿失败 [${data.errcode}]: ${data.errmsg}`);
  }
  return mediaId;
}

// 清理 HTML：去掉注释
function cleanHtml(html) {
  return html.replace(/<!--[\s\S]*?-->/g, '').trim();
}

// 解析命令行参数
function parseArgs() {
  const args = process.argv.slice(2);
  const params = {};
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace(/^--/, '');
    params[key] = args[i + 1];
  }
  return params;
}

async function main() {
  const params = parseArgs();
  const { content: contentPath, cover: coverPath, title, author, digest, embedImage, update } = params;

  if (!contentPath || !coverPath || !title) {
    console.error(
      '用法: push_draft.js --content <html> --cover <img> --title <标题> ' +
      '[--author <作者>] [--digest <摘要>] [--embed-image <图片>]'
    );
    process.exit(1);
  }

  if (!fs.existsSync(contentPath)) {
    console.error('❌ 内容文件不存在:', contentPath);
    process.exit(1);
  }
  if (!fs.existsSync(coverPath)) {
    console.error('❌ 封面图不存在:', coverPath);
    process.exit(1);
  }

  const config = loadConfig();

  console.log('1/5 获取 access_token ...');
  const token = await getAccessToken(config.appId, config.appSecret);
  console.log('   ✓ 成功');

  console.log('2/5 上传封面图 ...');
  const thumbMediaId = await uploadCoverImage(token, coverPath);
  console.log('   ✓ media_id:', thumbMediaId);

  console.log('3/5 处理正文内容 ...');
  let htmlContent = fs.readFileSync(contentPath, 'utf8');
  htmlContent = cleanHtml(htmlContent);

  // 如果指定了内嵌图片，上传并插入到正文末尾
  if (embedImage && fs.existsSync(embedImage)) {
    console.log('   上传内嵌图片 ...');
    const imgUrl = await uploadContentImage(token, embedImage);
    htmlContent += `\n<section style="margin-top:24px;text-align:center;"><img src="${imgUrl}" style="max-width:100%;border-radius:8px;" /></section>`;
    console.log('   ✓ 图片URL:', imgUrl);
  }

  console.log('   ✓ 内容长度:', htmlContent.length, '字符');
  if (htmlContent.length > 20000) {
    console.warn('   ⚠️ 超过2万字符限制，可能被截断');
  }

  console.log('4/5 组装文章数据 ...');
  const article = {
    title: title,
    author: author || '',
    digest: digest || '',
    content: htmlContent,
    thumb_media_id: thumbMediaId,
    content_source_url: '',
    need_open_comment: 0,
    only_fans_can_comment: 0,
    article_type: 'news',
  };

  const mode = update ? '更新' : '新增';
  console.log(`5/5 ${mode}草稿 ...`);
  const mediaId = update
    ? await updateDraft(token, update, article)
    : await addDraft(token, article);
  console.log('   ✓ 草稿 media_id:', mediaId);
  console.log(`\n✅ 已${mode}到公众号草稿箱`);
  console.log('   前往 mp.weixin.qq.com → 内容管理 → 草稿箱 查看');
}

main().catch((err) => {
  console.error('❌', err.message);
  process.exit(1);
});
