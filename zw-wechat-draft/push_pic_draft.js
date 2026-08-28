#!/usr/bin/env node
/**
 * push_pic_draft.js — 推送图片消息（newspic）草稿到公众号草稿箱
 * 接收图片文件夹路径 → 上传所有图片为永久素材 → 创建 newspic 草稿
 *
 * 用法:
 *   node push_pic_draft.js --title <标题> --dir <图片文件夹> \
 *     [--digest <摘要>] [--author <作者>]
 *
 * 配置文件: ~/.workbuddy/wechat_config.json
 *   { "appId": "wx...", "appSecret": "..." }
 */

const fs = require('fs');
const path = require('path');

const CONFIG_PATH = path.join(process.env.HOME, '.workbuddy/wechat_config.json');
const IMG_EXTS = ['.png', '.jpg', '.jpeg'];

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

// 获取 access_token
async function getAccessToken(appId, appSecret) {
  const url = `https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=${appId}&secret=${appSecret}`;
  const res = await fetch(url);
  const data = await res.json();
  if (data.errcode) {
    if (data.errcode === 40164) {
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

// 上传图片为永久素材（material/add_material, type=image）
async function uploadImage(accessToken, imagePath) {
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
    throw new Error(`上传图片失败 [${data.errcode}]: ${data.errmsg}  (${path.basename(imagePath)})`);
  }
  return data.media_id;
}

// 新增图片消息草稿（newspic）
async function addPicDraft(accessToken, article) {
  const url = `https://api.weixin.qq.com/cgi-bin/draft/add?access_token=${accessToken}`;
  const body = { articles: [article] };
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (data.errcode) {
    throw new Error(`新增图片消息草稿失败 [${data.errcode}]: ${data.errmsg}`);
  }
  return data.media_id;
}

// 更新已有图片消息草稿（按 media_id 覆盖，articles 为对象而非数组）
async function updatePicDraft(accessToken, mediaId, article) {
  const url = `https://api.weixin.qq.com/cgi-bin/draft/update?access_token=${accessToken}`;
  const body = { media_id: mediaId, index: 0, articles: article };
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (data.errcode) {
    throw new Error(`更新图片消息草稿失败 [${data.errcode}]: ${data.errmsg}`);
  }
  return mediaId;
}

function parseArgs() {
  const args = process.argv.slice(2);
  const params = {};
  for (let i = 0; i < args.length; i += 2) {
    if (!args[i].startsWith('--')) {
      console.error('❌ 参数格式错误:', args[i]);
      process.exit(1);
    }
    params[args[i].replace(/^--/, '')] = args[i + 1];
  }
  return params;
}

function listImages(dir) {
  return fs.readdirSync(dir)
    .filter(f => IMG_EXTS.includes(path.extname(f).toLowerCase()))
    .sort()
    .map(f => path.join(dir, f));
}

async function main() {
  const params = parseArgs();
  const { title, dir, digest, author, content, update } = params;
  let contentText = content || '';
  if (params['content-file']) {
    const cf = params['content-file'];
    if (!fs.existsSync(cf)) {
      console.error('❌ 内容文件不存在:', cf);
      process.exit(1);
    }
    contentText = fs.readFileSync(cf, 'utf8');
  }

  if (!title || !dir) {
    console.error(
      '用法: push_pic_draft.js --title <标题> --dir <图片文件夹> ' +
      '[--content <描述文字> | --content-file <描述文件>] [--digest <摘要>] [--author <作者>] [--update <media_id>]'
    );
    process.exit(1);
  }

  if (!fs.existsSync(dir) || !fs.statSync(dir).isDirectory()) {
    console.error('❌ 图片文件夹不存在:', dir);
    process.exit(1);
  }

  if (title.length > 32) {
    console.warn(`⚠️ 标题 ${title.length} 字超过 32 字上限，建议精简`);
  }

  let imagePaths = listImages(dir);
  if (imagePaths.length === 0) {
    console.error('❌ 文件夹内未找到 png/jpg/jpeg 图片');
    process.exit(1);
  }
  if (imagePaths.length > 20) {
    console.warn(`⚠️ 图片 ${imagePaths.length} 张超过 20 张上限，仅取前 20 张`);
    imagePaths = imagePaths.slice(0, 20);
  }

  const config = loadConfig();

  console.log(`1/3 获取 access_token ...`);
  const token = await getAccessToken(config.appId, config.appSecret);
  console.log('   ✓ 成功');

  console.log(`2/3 上传 ${imagePaths.length} 张图片为永久素材 ...`);
  const image_list = [];
  for (let i = 0; i < imagePaths.length; i++) {
    const p = imagePaths[i];
    console.log(`   [${i + 1}/${imagePaths.length}] ${path.basename(p)}`);
    const mediaId = await uploadImage(token, p);
    image_list.push({ image_media_id: mediaId });
    console.log(`        ✓ ${mediaId}`);
  }

  if (image_list.length > 1 && digest) {
    console.warn('⚠️ 微信限制：多图消息（>1 张）的摘要（digest）不生效，仅单图消息支持摘要；如要带文字说明请用 --content。');
  }

  const mode = update ? '更新' : '新增';
  console.log(`3/3 ${mode}图片消息草稿 (newspic) ...`);
  const article = {
    article_type: 'newspic',
    title,
    author: author || '',
    digest: digest || '',
    content: contentText || '',
    image_info: { image_list },
    need_open_comment: 0,
    only_fans_can_comment: 0,
  };
  const mediaId = update
    ? await updatePicDraft(token, update, article)
    : await addPicDraft(token, article);
  console.log(`   ✓ 草稿 media_id: ${mediaId}`);
  console.log(`\n✅ 已${mode}到公众号草稿箱 (图片消息)`);
  console.log('   前往 mp.weixin.qq.com → 内容管理 → 草稿箱 查看');
}

main().catch((err) => {
  console.error('❌', err.message);
  process.exit(1);
});