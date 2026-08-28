---
name: zw-card
description: "Content caster (铸). Transforms content into PNG visuals. Eight molds: -l long reading card, -i infograph, -m multi-card reading cards, -s social sharing card set with a distinct cover and per-section cards, -v editorial sketchnote, -c comic, -w whiteboard, -b big-font attachment card. Use when user says '铸', '做成图', '做成卡片', '小红书组图', '社媒组图', '每节一张卡片', '小红书卡片', '信息图', '海报', '视觉笔记', '漫画', '白板', or '附件图'."
---

# zw-card: 铸

将内容铸成可见的形态。内容进去，PNG 出来。模具决定形状。

## 参数

| 参数 | 模具 | 尺寸 | 说明 |
|------|------|------|------|
| `-l`（默认） | 长图 | 1080 x auto | 单张阅读卡，内容自动撑高 |
| `-i` | 信息图 | 1080 x auto | 内容驱动的自适应视觉布局 |
| `-m` | 多卡 | 1080 x 1440 | 自动切分为多张阅读卡片 |
| `-s` | 社媒组图 | 1080 x 自适应 | 1 张总领封面 + 每节 1 张内容卡；全组同高 |
| `-v` | 视觉笔记 | 1080 x auto | 编辑式杂志专题：问题→失败→转折→顿悟→命名（6 layout 模具 / 4 字族对比 / 探案档案细节）|
| `-c` | 漫画 | 1080 x auto | 日式黑白漫画风格，动态选择漫画家视觉语言 |
| `-w` | 白板 | 1080 x auto | 白板马克笔风格，结构化框图+箭头+彩色标记 |
| `-b` | 大字 | 1080 x 1440 | 碑刻大字 + 和紙 + 外阴影，小红书附件风格（单句/短段） |

## 约束

本 skill 输出为视觉文件（PNG），不适用 L0 中的 Org-mode、Denote 和 ASCII-only 规范。

## 共享基础

### 获取内容

- URL --> WebFetch 获取
- 粘贴文本 --> 直接使用
- 文件路径 --> Read 获取

### 提炼原则（关键）

本 skill 产出的是「阅读卡 / 视觉摘要」，**不是原文的转录**。无论哪个模具，都遵循：**先理解、再抽取、后上版**。

- **-l 长图 / -v 视觉笔记**：面向长文、访谈、报告时，必须先通读、提炼骨架（标题 + 章节脉络）+ 金句 + 关键引述，压缩正文。长文铸成卡后正文篇幅应约为原文的 1/3 ~ 1/2；若几乎与原文等长，说明未提炼，需重做。
- **「不做切分」是版式指令**（单卡 vs 多卡），**绝不意味着逐字保留原文**——这是最常见的误用。
- 短帖、单句、金句类输入（如 -b 大字）可原样使用。
- **`-s 社媒组图`**：先做出“封面总判断”，再将每个章节重写为一个独立判断、一幅以卡片标题为主轴的简洁叙事图解和一段可分享的解释。配文负责规划画面证据，但只选择最能解释标题的 2–4 个要素，避免把整段文字塞进图里；全组统一视觉语言，每张图独立对应本卡主题。**配图必须通过 Image2 生图生成；不得以 SVG、CSS 图形、图标拼接、占位图或图库素材替代。**严禁机械切卡或重复使用同一插画。

### 文件命名

从内容提取标题或核心思想作为 `{name}`（中文直接用，去标点，≤ 20 字符）。

### 截图工具

```bash
node assets/capture.js <html> <png> <width> <height> [fullpage]
```

从 skill 根目录运行。依赖 skill 根目录下的 `node_modules/` 中的 playwright。如报错：

```bash
npm install playwright && npx playwright install chromium
```

### Footer

- 左侧：logo + 张伟。`{{LOGO}}` 变量**必须**使用 `file://` 绝对路径指向 `assets/avatar.png`：`src="file:///path/to/skills/zw-card/assets/avatar.png"`。禁止使用临时 SVG、占位图或内联 data URI。
- 右侧：内容来源（可选）——有明确来源时显示（如作者名、arxiv ID、网站名等），无来源时留空。使用 `{{SOURCE_LINE}}` 变量：有来源时填 `<span class="info-source">来源文字</span>`，否则空字符串。适用于 `-l`、`-i`、`-v`、`-c`、`-w`、`-s` 模具（`-m` 多卡无 footer，不适用）。

### 交付

1. 报告文件路径
2. `-s` 社媒组图的用户交付目录只放最终 PNG。HTML、原始/生成配图、构建脚本、检查文件和分享文案存入 `work/` 或其他内部源文件目录，不在最终回复中链接或列出；仅当用户明确索要源文件或分享文案时再提供。
3. 同步文章到 Obsidian「公众号工作流」（必做）：把长图里的**文章内容（带排版）**同步到 Obsidian 一份——这是用户的长期约定。
   ⚠️ **只放文章内容 + 排版（Markdown），绝不嵌入长图 PNG 本身。**
   ```bash
   /Users/zhangwei/.workbuddy/binaries/python/versions/3.13.12/bin/python3 \
     ~/.workbuddy/skills/zw-card/sync_obsidian.py \
     --input <长图.html> [--date 2026-07-11]
   ```
   - 脚本自动提取长图 HTML 的文字与结构（标题 / `##` 章节 / 金句 `[!quote]` callout / 列表 / 来源），
     渲染为 Obsidian Markdown，写入 `~/Obsidian/张伟的obsidian/公众号工作流/<标题>.md`。
   - 仅取文字与层级，**不复制、不嵌入长图 PNG**。适用于所有承载文章内容的模具（-l / -i / -v / -w 等）；
   纯单句装饰模具（-b 大字）也会生成极简笔记，无害。`-s` 社媒组图只交付图片与 HTML，不同步为公众号文章。

## 品味准则

**所有模具共享**。执行任何模具前，先 Read `references/taste.md`，作为视觉质量底线贯穿全流程。

核心：反 AI 生成痕迹——禁 Inter 字体、禁纯黑、禁三等分卡片、禁居中 Hero、禁 AI 文案腔、禁假数据。

## 执行

根据参数选择模具，Read `references/taste.md` + 对应的 mode 文件，按步骤执行：

### -l（默认）：长图

Read `references/mode-long.md`，按其步骤执行。

模板：`assets/long_template.html`

### -i：信息图

Read `references/mode-infograph.md`，按其步骤执行。

模板：`assets/infograph_template.html`

### -m：多卡

Read `references/mode-poster.md`，按其步骤执行。

模板：`assets/poster_template.html`

### -s：社媒组图

Read `references/mode-social.md` 和 `references/production-runbook.md`，按其步骤执行。前者定义模具，后者沉淀已验证的生产经验与每次任务的演进协议。

模板：`assets/social_cover_template.html`、`assets/social_card_template.html`

### -v：视觉笔记

Read `references/mode-sketchnote.md`，按其步骤执行。

模板：`assets/sketchnote_template.html`

### -c：漫画

Read `references/mode-comic.md`，按其步骤执行。

模板：`assets/comic_template.html`

### -w：白板

Read `references/mode-whiteboard.md`，按其步骤执行。

模板：`assets/whiteboard_template.html`

### -b：大字

Read `references/mode-big.md`，按其步骤执行。

模板：`assets/big_template.html`
