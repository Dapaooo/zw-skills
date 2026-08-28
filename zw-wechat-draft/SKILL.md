---
name: zw-wechat-draft
description: 两个入口——(A) 将文章（URL 或文本）提炼为公众号图文并推送草稿箱；(B) 将卡片/长图 PNG 文件夹直接贴图（图片消息）推送到草稿箱。触发词：推公众号、发到公众号、公众号草稿、做成公众号文章、推送草稿箱、贴图草稿、图片消息草稿。
agent_created: true
version: 1.1.0
---

# zw-wechat-draft — 文章内容提炼并推送到公众号草稿箱

> zw- 家族技能：把任意文章（URL 或文本）提炼为公众号版图文，标注信息来源，一键推送到微信公众号草稿箱。

## 触发场景
- 用户做完卡片/长图后说「推到公众号草稿箱」「发到公众号」
- 用户说「这篇文章做成公众号」「帮我发到公众号」「推公众号草稿」
- 用户给一个链接/文本，要求产出公众号图文并推送

## 两种模式（先判断输入，再动手）

### 模式 A：图文文章（提炼摘要）
输入是 **URL / 文本 / 一篇文章** → 产出「公众号图文摘要」，走下方「核心原则 + 完整流程」，用 `publish.js` 渲染 + 推送。

### 模式 B：贴图草稿（图片消息，不提炼）
输入是**一组卡片 / 长图的 PNG 图片文件夹**（如 zw-card 产出的 `01-cover.png`~`07-card.png`），用户要的是把图**直接贴**进草稿箱，**不是提炼成文章**：
- **不要**提炼 content.json、**不要**走 publish.js 渲染图文。
- 直接用 `push_pic_draft.js` 把整组图作为「图片消息（newspic）」推送：

```bash
/Users/zhangwei/.workbuddy/binaries/node/versions/22.22.2/bin/node \
  ~/.workbuddy/skills/zw-wechat-draft/push_pic_draft.js \
  --title "<标题>" --dir "<图片文件夹>" --author "张伟"
```
- 参数：`--title`（≤32 字）、`--dir`（自动按文件名排序取 .png/.jpg/.jpeg，≤20 张）、`--author`；可选 `--digest`（仅单图生效）、`--content <文字>` / `--content-file <文件>`、`--update <media_id>`（覆盖已有图片草稿，补正文/改图时用它）。
- **正文描述必做**：图片消息的 `content` 是**整条消息的纯文本正文**（微信规定 newspic 的 content 仅支持纯文本，非每图单独说明）。推送时须用 `--content-file` 传正文，不要纯贴图不带文字。正文写法分两类：
  - **原创内容卡片组**（zw-card / Codex 等自产卡片，非第三方来源）：默认用**完整配文**，与小红书同一套正文规则（概括全文核心内容：陷阱/问题 → 方法/路径 → 关键细节 → 收尾升华，600-700 字，可含话题标签）——用户偏好（2026-08-21 实测："小红书的这个配文我比较满意，推到微信公众号的正文也用这个规则"）。**不做精简导语**，除非用户明确要精简。
  - **第三方内容**：提炼成精简导语 + 注明出处（见下条）。
- **导语必须注明出处**：凡图片内容取自第三方（文章/报告/访谈等），导语开头须写明出处——媒体名 + 作者（如 `《Token经济，中国账本》是《财经》杂志2026年8月17日封面报道（文｜吴俊宇 周源）`）。与 zw-card 长图 Footer 的来源标注保持一致，不遗漏、不臆造。
- 第一张图（如 `01-cover.png`）作为该图片消息的封面。
- 踩坑：多图（>1 张）时 `digest` 不生效（微信限制）；图片消息草稿同走 `draft/add`，但 `article_type:"newspic"`。

> 判断口诀：给的是**图（文件夹）**→ 模式 B 贴图；给的是**文章/链接/文本**→ 模式 A 提炼。

## 模式 A 核心原则：先提炼，再推送（不是转录）
本技能产出的是「公众号图文摘要」，**不是原文的复制粘贴**。无论原文多长，都遵循：
1. **提炼骨架（硬要求，不可省略）**：读原文 → 抽取核心论点、章节脉络、关键引述；砍掉寒暄、重复、冗余问答，重组为公众号图文，**不是逐段照搬原文**。提炼产物篇幅下限为原文 1/3；上限不设 1/2 硬顶（提炼可充分展开），但"上限不限制"≠"放全文"，提炼动作必须可见。
2. **拎金句**：把承载核心洞察的短句独立成 `highlight` 块。
3. **标注来源**：每篇必须显式标注信息来源（见 `references/content-format.md`），尊重原作者著作权。
4. **自检**：读起来应像「有人帮你读完并划了重点」——必须经历压缩与重组，不能逐段照搬原文；篇幅下限为原文 1/3，上限不设硬顶但提炼动作不可省略。

## 模式 A 完整流程

### 0. 前置检查（首次或推送失败时才需）
- **凭证**：`~/.workbuddy/wechat_config.json` 含 `appId` + `appSecret`。缺失则提示用户创建（不要替用户写密钥）。
- **IP 白名单**：当前机器出口 IP 须加入微信开发者平台 → 公众号 → 接口管理 → **API IP 白名单**（`developers.weixin.qq.com/platform`）。
  - ⚠️ 开发接口管理已从 `mp.weixin.qq.com` 迁移至 `developers.weixin.qq.com/platform`。
  - 若用 VPN，出口 IP 会变——**以推送报错 40164 中返回的「实际 IP」为准**（不要用 `curl ipify` 查的，二者常不一致）。
  - 推送前可运行 `node publish.js --check-ip` **主动探测白名单**（直接问微信要「实际 IP」，比本地 curl 准）；完整推送命令也会在渲染前自动预检，未命中则直接拦截退出，不浪费截图/上传。
  - 出口 IP 频繁变化的根因与根治方案（固定 IP 部署）见 `references/deploy.md`。

### 1. 获取并提炼原文
- 若是 URL：`WebFetch` 提取完整正文（标题、作者、发布时间、所有段落与小标题）。
- 若是文本：直接读。
- **提炼**：按上面「核心原则」压成骨架 + 金句，同时记录**来源信息**（原作标题、作者/出处、发布日期、链接）。

### 2. 标注信息来源
在 `content.json` 中标注（详见 `references/content-format.md`）：
- `subtitle`：来源 + 日期，如 `易论AI 深度对话 · 2026.07.09`（显示在封面与正文开头）
- ⚠️ **文章末端不放置来源 `footer` 块**（用户偏好，2026-08-15：去掉文章末端内容来源部分）。渲染器仅在 content.json 显式含 `footer` 块时才渲染，规范默认不写。

### 3. 组织 content.json
- 把提炼结果写成 `content.json`（字段见 `references/content-format.md`）。
- `content_type` 选对应色调（思辨/哲学、技术/工程、文学/叙事、科学/研究、商业/管理）。
- 用 `Write` 写到当前工作目录。

### 4. 调用 publish.js 渲染 + 推送
```bash
/Users/zhangwei/.workbuddy/binaries/node/versions/22.22.2/bin/node \
  ~/.workbuddy/skills/zw-wechat-draft/publish.js \
  --content <content.json> --output-dir <输出目录>
```
- 默认：渲染 HTML + 封面 **并** 推送草稿箱。
- 加 `--no-push`：只预览（生成本地 HTML + 封面，不推送），确认无误后再去掉该参数推送。

### 5. 同步文章到 Obsidian「公众号工作流」（必做，与推送并列）
无论是否推送，都把**文章内容（带排版）**同步到 Obsidian 一份——这是用户的长期约定，不要漏。
⚠️ **只放文章内容 + 排版（Markdown），绝不嵌入长图 / 封面 PNG。**

```bash
/Users/zhangwei/.workbuddy/binaries/python/versions/3.13.12/bin/python3 \
  ~/.workbuddy/skills/zw-wechat-draft/sync_obsidian.py \
  --input <content.json> [--date 2026-07-11] [--content-type 商业/管理]
```
- 脚本自动把 `content.json` 的 blocks 渲染成 Obsidian Markdown（标题 / `##` 章节 / 金句 `[!quote]` callout / 列表 / 来源），
  写入 `~/Obsidian/张伟的obsidian/公众号工作流/<标题>.md`。
- `date` 不传则默认今天；`content-type` 不传则取 content.json 的 `content_type`。
- 该脚本同时支持长图 HTML 输入（供 zw-card 复用），但本技能只传 content.json。

## 产物
| 文件 | 说明 |
|------|------|
| `<标题>_wechat.html` | 公众号版 HTML（纯 inline CSS，16px 正文，自适应） |
| `<标题>_cover.png` | 封面图（900×500） |
| 草稿 media_id | 推送成功后打印 |

## 文件结构（自包含）
```
~/.workbuddy/skills/zw-wechat-draft/
├── SKILL.md                  # 本文件
├── package.json             # {"type":"commonjs"}
├── palettes.js              # 共享调色板预设
├── render_wechat.js         # 公众号 HTML 渲染器
├── render_cover.js          # 封面生成器
├── push_draft.js            # 图文（news）草稿推送
├── push_pic_draft.js        # 图片消息（newspic）草稿推送（模式 B 贴图）
├── publish.js               # 统一编排入口（渲染+封面+推送，模式 A）
├── assets/capture.js        # Playwright 截图管线（自带）
└── references/
    ├── content-format.md    # content.json 格式 + 来源标注规范
    └── deploy.md            # 固定 IP 部署指引（根治每次加白名单）
```

## API 流程（push_draft.js 内部）
1. `GET /cgi-bin/token` → access_token（2 小时有效）
2. `POST /cgi-bin/material/add_material` → 上传封面图，得 thumb_media_id
3. `POST /cgi-bin/draft/add` → 新增草稿，得 media_id
4. （可选）`POST /cgi-bin/draft/update` → 按 media_id 覆盖已有草稿

## 更新已有草稿（--update <media_id>）
用于修正已推送的草稿，不产生重复草稿：
```bash
node publish.js --content <content.json> --output-dir <dir> --update "<旧media_id>"
```
⚠️ `draft/update` 与 `draft/add` 的关键差异（踩坑记录）：
- **`articles` 是单个对象，不是数组**。`add` 用 `articles:[article]`；`update` 必须用 `articles:article`，否则报 `47001 data format error`。
- `article` 必须含 `article_type: "news"`（更新接口比新增更严格，缺则同样 47001）。
- 若报 `40007 invalid media_id`：两种常见原因——
  1. **media_id 抄写遗漏**（2026-08-21 实测）：media_id 以 `_-_` 结尾（如 `...waC_-_`），手抄/重敲时极易漏最后那个 `_`（`waC-_` → 40007）。**务必从推送输出原样整段复制**，不要手抄。
  2. media_id 已失效 / 草稿已不在箱（被删或未真正留存）。此时**改用新增模式**（去掉 `--update`）重推一篇即可，旧 media_id 作废。
- 更新成功后 media_id **保持不变**（覆盖原草稿，不产生重复草稿；回复用户时可沿用原 media_id）。

## 常见错误
| 错误码 | 原因 | 解决 |
|--------|------|------|
| 40164 | IP 不在白名单 | 把报错 / `--check-ip` 返回的「实际 IP」加入开发者平台白名单；根治方案（固定推送出口 IP）见 `references/deploy.md` |
| 40113 | AppSecret 错误 | 检查 `~/.workbuddy/wechat_config.json` |
| 40007 | access_token 失效 / 更新的 media_id 已失效 / **media_id 末尾字符抄漏（结尾 `_-_` 易漏最后 `_`）** | 先核对 media_id 是否从输出原样复制；确已失效则改用新增模式重推 |
| 45009 | 接口调用频率限制 | 稍后重试 |
| 47001 | draft/update 的 articles 格式错 | 必须 `articles:article`（对象），且 article 含 `article_type:"news"` |

## 运行环境
- CommonJS（`require`）；`package.json` 声明 `"type":"commonjs"`。
- 截图依赖 Playwright（`assets/capture.js`），需已安装 chromium。
- 所有脚本路径相对本技能目录，自包含、不依赖其他技能。

## 固定 IP 部署（根治「每次加白名单」）
出口 IP 不固定（家庭宽带动态分配 / 开 VPN 节点漂移）导致每次都要手动加白名单；而白名单无法用 API 自动修改。根治方案是把推送请求改由一台**固定公网 IP**的服务器/云函数发出，白名单只加一次。三种形态（本地直连 / 仅推送上云 / 整链上云）的对比与操作步骤见 `references/deploy.md`。
