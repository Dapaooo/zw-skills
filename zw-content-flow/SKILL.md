---
name: zw-content-flow
description: "选题内容流水线（zw- 家族）。给一个选题 → AI 联网调研并提炼观点（金句+来源）→ 经你确认/纠偏 → 按 zw-card 长图风格铸成 PNG（存档/朋友圈/知识星球分发）→ 同一份内容做成公众号图文并推送到草稿箱。两套产物内容同源。触发词：跑选题、做一篇、选题流水线、内容工作流、给个选题、出一篇公众号。"
user_invocable: true
agent_created: true
version: 1.1.0
---

# zw-content-flow — 选题到公众号的一键流水线

一次给选题，自动走完：**调研 → 你确认 → 铸长图 → 推公众号**。
最终**两套产物、内容同源**：

| 产物 | 形态 | 用途 |
|------|------|------|
| zw-card 长图 PNG | 1080px 视觉长图 | 存档 + 朋友圈/知识星球等分发 |
| 公众号图文 | HTML + 900×500 封面 | 已推送至微信公众号草稿箱 |

## 总览

```
阶段0 选题 ──→ 阶段1 AI联网调研+素材底稿 ──→ 阶段2【你确认/纠偏】
                                                      │
                                                      ▼
                                          阶段3 铸 zw-card 长图 PNG（存档）
                                                      │
                                                      ▼
                                          阶段4 做公众号图文 + 推送草稿箱
                                                      │
                                                      ▼
                                          阶段5 汇报（路径 + media_id + 来源）
```

## 内容风格准则（贯穿阶段 1–4）

本流水线产出的是「有态度的内容」，不是信息搬运。以下风格要求源自 `zhangwei-book-reading` 技能，经适配用于选题创作；创作前、创作中、自检时都须遵守。

### A. 立场先行：x / f / f(x) 选题框架

动笔前先想清这组问题，并在阶段 1 底稿的「立场框」中写明：

- **x（核心问题）**：这篇到底在回答什么具体问题？要具体到不能描述另一个同话题的内容。
- **attitude（态度）**：你希望读者读完感受到 / 接受什么立场？
- **old answer（旧认知）**：读者或这个领域在了解前，默认怎么想？
- **f（框架 / 透镜）**：你用什么模型、区分、比喻、程序来组织内容？
- **f(x)（结论）**：通过这个框架，你看到了什么、得出了什么？

这五个问答是内容的「骨架意图」，让文章有灵魂而非平铺信息。长图与公众号两版须贯穿同一组 x/f/f(x)。

### B. 语言风格（承载文字的通用底线）

- 用具体动词、短句，避免学术腔与 AI 总结腔。
- 不喊口号、不赞美；解释「它做了什么、在哪起作用」，而非吹捧。
- 过渡词变化：用「自此 / 到这里 / 更进一步 / 问题就在这里出现 / 这解释了 / 换个角度看 / 接下来 / 这让读者看到」等自然推进，不依赖重复的「但 / 然而 / 于是 / 所以」。
- 平铺直叙优先：能直说的句子就直说，别裹在对比或元解释里；不过度用「不是…而是…」，也不滥用「真正 / 核心 / 本质」标记。
- 标不确定性：来源存疑的数据或说法，标注置信度（如「据行业公开讨论」）；不假装全知。来源可考的标来源，推断的标「推断」。
- 不堆金句：金句只锚定决定性洞察，宁少勿滥。

### C. 结构承载 vs 文字风格（避免与 zw-card / 公众号结构化冲突）

- 长图（zw-card）的 item / section / ladder / list，以及公众号 content.json 的 blocks，是**视觉与层次承载**，结构清晰是优点，不受「避免项目符号」约束。
- 但承载其中的**文字内容**（intro、section body、item 正文、金句）必须遵守 B 的语言风格。
- 分析性正文优先用散文叙述；表格 / 列表仅用于「并列枚举型」信息（如分类清单、阶梯、公式对比），不用于承载论证推进。

### D. 提炼标准（强化）

- 抓重心，不平均权重：重建内容的「架构」，而非逐条罗列章节。
- 篇幅为素材的 1/3~1/2，读起来像「有人帮你读完并划了重点」。
- 凡引用外部来源必须标注；纯原创观点注明「原创」，推断标注「推断」。

---

## 阶段 0：接收选题

- 用户给出选题（主题 / 角度 / 关键词）。若用户已附带素材、链接或私有观点，阶段 1 可跳过或缩短。
- 与用户敲定一个 `{name}`：中文去标点、≤20 字，作为文件命名与目录名（如 `AI泡沫2029`）。
- 建议在本技能适用的内容项目目录下运行（如 `/Users/zhangwei/WorkBuddy/自动化内容创作/`）。在该目录建工作子目录 `{name}/`，所有中间与最终产物都放这里。

## 阶段 1：AI 联网调研 + 素材底稿（给你纠偏）

用 `WebSearch` / `WebFetch` 检索选题相关的：核心观点、关键数据、争议点、代表人物/来源、近期进展。

提炼为「素材底稿」写入 `{name}/research.md`：

- **标题候选**（1–3 个）
- **章节骨架**（每节：标题 + 2–4 句核心论点）
- **金句候选**（独立成段、<25 字、承载关键洞察的短句）
- **立场框（x / f / f(x)）**：见「内容风格准则 A」——先定核心问题 x、态度 attitude、旧认知 old answer、框架 f、结论 f(x)，贯穿两版创作并交阶段 2 你确认。
- **来源清单**（出处 / 作者 / 日期 / 链接——用于后续著作权标注）
- **内容气质判定**：从 `思辨/哲学` `技术/工程` `文学/叙事` `科学/研究` `商业/管理` 中选一，决定阶段 3 的色调与阶段 4 的 `content_type`

遵循「先理解、再抽取、后上版」：底稿是骨架+金句，不是原文转录。读起来应像「有人帮你读完并划了重点」。

> ⚠️ **阶段 1 结束后必须暂停**：把 `research.md` 的摘要（含**立场框** x/f/f(x)）呈现给用户，请用户确认「核心问题是否具体、态度是否到位、框架是否清晰」，再**确认 / 补充 / 纠偏**。得到用户明确的「继续」后再进入阶段 3。此「你纠偏」节点是本工作流的核心，不可跳过。

## 阶段 3：按 zw-card 长图风格铸 PNG（存档 / 分发）

本阶段 = 执行 **zw-card 的 `-l 长图` 模具**。先 Read 以下权威文件（风格细节以它们为准，本技能不重复定义）：

- `~/.workbuddy/skills/zw-card/references/taste.md`（设计品味底线，最高优先级）
- `~/.workbuddy/skills/zw-card/references/mode-long.md`（步骤 2 / 2.5 / 3 / 4 / 5）
- `~/.workbuddy/skills/zw-card/assets/long_template.html`（模板变量）

步骤：

1. 按 `mode-long.md` 步骤 2/2.5/3，把**已确认**的素材格式化为 `BODY_HTML`（`<p>`、`<h2>`、`<blockquote>`、`.highlight`、`.prompt`、`.item`、`.divider`、首段 `.dropcap`）。
2. 色调：按阶段 1 判定的内容气质，套用 `mode-long.md` 步骤 2.5 的 `BG_COLOR` / `ACCENT_COLOR` 表。
3. 渲染模板 → 写 `{name}/long_{name}.html`，替换全部 `{{变量}}`：
   - `{{LOGO}}` 用 `file://` 绝对路径填写：`file:///Users/zhangwei/.workbuddy/skills/zw-card/assets/avatar.png`（勿用相对路径或保留占位符，capture.js 不会自动注入）；
   - `{{TITLE_BLOCK}}` / `{{BODY_HTML}}` / `{{SOURCE_LINE}}`（有来源才填）按 mode-long 规则填入；
   - `{{BG_COLOR}}` / `{{ACCENT_COLOR}}` 用步骤 2.5 的值。
4. 截图（capture.js 已随 zw-card 装好 playwright；若报 chromium 缺失，先在该目录执行 `npx playwright install chromium`）：

```bash
/Users/zhangwei/.workbuddy/binaries/node/versions/22.22.2/bin/node \
  /Users/zhangwei/.workbuddy/skills/zw-card/assets/capture.js \
  {name}/long_{name}.html {name}/{name}.png 1080 800 fullpage
```

成品 `{name}/{name}.png` 即 zw-card 长图，进入存档 / 分发。

5. **同步 Obsidian（必做）**：铸完长图后，按 zw-card「交付」第 2 步，把长图里的**文章内容（带排版）**同步到 `~/Obsidian/张伟的obsidian/公众号工作流/`（只放文字+排版，**绝不嵌入长图 PNG**；脚本 `zw-card/sync_obsidian.py` 自动提取 HTML 文字与结构）。

## 阶段 4：做公众号图文并推送草稿箱

本阶段 = 执行 **zw-wechat-draft**。先 Read `~/.workbuddy/skills/zw-wechat-draft/references/content-format.md`。

把**同一份素材**组织成 `content.json` 写入 `{name}/content.json`：

- 字段：`title` / `subtitle`（来源+日期）/ `author`(张伟) / `digest` / `content_type`（与阶段 3 气质一致）/ `source` / `blocks`
- `blocks` 类型：`intro` `section` `highlight` `quote` `divider` `list` `item` `subtitle` `footer` `endmark`
- **金句位置对齐（关键）**：`blocks` 里 `highlight` / `quote` 的出现顺序，必须与阶段 3 长图 `BODY_HTML` 中 `.highlight` / `blockquote` 的出现顺序**逐处一致**（见 content-format.md「金句/引用位置规则」）。用「只写 title 的 section + 拆段穿插」表达。
- **来源标注（必做）**：`subtitle` 标来源+日期；末尾 `footer` 块写完整来源声明 + 免责措辞（模板见 content-format.md）。

前置检查（仅首次或推送失败时需要）：

- `~/.workbuddy/wechat_config.json` 含 `appId` + `appSecret`，缺失则提示用户创建（不要替用户写密钥）。
- 当前机器出口 IP 已加入微信开发者平台 → 公众号 → 接口管理 → **API IP 白名单**（`developers.weixin.qq.com/platform`）。若用 VPN，以推送报错 `40164` 返回的实际 IP 为准。

渲染 + 推送：

```bash
/Users/zhangwei/.workbuddy/binaries/node/versions/22.22.2/bin/node \
  ~/.workbuddy/skills/zw-wechat-draft/publish.js \
  --content {name}/content.json --output-dir {name}/
```

- 默认即渲染 HTML + 封面**并**推送草稿箱。
- 加 `--no-push`：仅预览（生成本地 HTML + 封面，不推送），确认无误后再去掉该参数推送。
- 修正已推草稿：`--update "<旧media_id>"`。
- **同步 Obsidian（必做）**：渲染/推送后，按 zw-wechat-draft 第 5 步，把**文章内容（带排版）**同步到 `~/Obsidian/张伟的obsidian/公众号工作流/`（只放文字+排版，**绝不嵌入长图/封面 PNG**；脚本 `zw-wechat-draft/sync_obsidian.py` 读 content.json 生成 Markdown）。

## 阶段 5：汇报

向用户汇总：

- 选题与最终标题
- **zw-card 长图 PNG** 路径（存档 / 分发用）
- **公众号图文** HTML 路径 + 封面 PNG 路径
- **公众号草稿 media_id**（推送成功时打印）
- **来源标注情况**（已标 / 缺来源提醒）

## 关键约束

- **提炼而非转录**：长图文稿与公众号均为原文 1/3~1/2 篇幅。
- **去 AI 腔**（详见 taste.md）：禁「赋能 / 无缝 / 释放 / 下一代」；禁假数据（用有机「脏」数据如 `47.2%`）；禁通用人名（John Doe 等）；禁纯黑 `#000`；禁三等分等宽卡片、禁居中 Hero。
- **著作权**：凡引用外部来源必须标注；纯原创观点可不标来源但注明「原创」。
- **阶段 2（你纠偏）不可跳过**：这是保证内容质量与你对齐的关键闸门。
