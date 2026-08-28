---
name: zw-card
description: "Content caster (铸). Transforms content into PNG visuals. Seven molds: -l (default) long reading card, -i infograph, -m multi-card reading cards (1080x1440), -v editorial sketchnote (problem→failure→pivot→insight→naming, magazine + archive layout), -c comic (manga-style B&W), -w whiteboard (marker-style board layout), -b big-fonts attachment card (1080x1440, weathered 碑刻 style for 小红书). Output to ~/Downloads/. Use when user says '铸', 'cast', '做成图', '做成卡片', '做成信息图', '做成海报', '视觉笔记', 'sketchnote', '杂志', 'editorial', '漫画', 'comic', 'manga', '白板', 'whiteboard', '大字', '附件图', 'big fonts', '小红书卡片'. Forked from ljg-card, customized with user avatar and signature."
user_invocable: true
version: "1.2.0"
---

# zw-card: 铸

将内容铸成可见的形态。内容进去，PNG 出来。模具决定形状。

## 参数

| 参数 | 模具 | 尺寸 | 说明 |
|------|------|------|------|
| `-l`（默认） | 长图 | 1080 x auto | 单张阅读卡，内容自动撑高 |
| `-i` | 信息图 | 1080 x auto | 内容驱动的自适应视觉布局 |
| `-m` | 多卡 | 1080 x 1440 | 自动切分为多张阅读卡片 |
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

**同时记录来源信息**（铸版前必须完成，用于 Footer 标注）：出处名称（媒体/公众号/作者名）、发布日期、原文链接。存疑时以原文标注为准，不臆造出处。

### 提炼原则（关键）

本 skill 产出的是「阅读卡 / 视觉摘要」，**不是原文的转录**。无论哪个模具，都遵循：**先理解、再抽取、后上版**。

- **-l 长图 / -v 视觉笔记**：面向长文、访谈、报告时，必须先通读、提炼骨架（标题 + 章节脉络）+ 金句 + 关键引述，压缩正文。长文铸成卡后正文篇幅应约为原文的 1/3 ~ 1/2；若几乎与原文等长，说明未提炼，需重做。
- **「不做切分」是版式指令**（单卡 vs 多卡），**绝不意味着逐字保留原文**——这是最常见的误用。
- 短帖、单句、金句类输入（如 -b 大字）可原样使用。

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
- 右侧：内容来源（**必注**，纯原创内容除外）——凡内容取自第三方（文章/报告/访谈/书籍等），必须在 Footer 标注出处，格式 `《出处》· 作者`（如 `《财经》· 吴俊宇 周源`）；无明确出处或纯原创时留空。使用 `{{SOURCE_LINE}}` 变量：有来源时填 `<span class="info-source">来源文字</span>`，否则空字符串。适用于 `-l`、`-i`、`-v`、`-c`、`-w` 模具（`-m` 多卡无 footer，不适用）。
- ⚠️ 出处信息不得遗漏或臆造：WebFetch 获取内容时同时记录出处与作者；模板变量必须与原文一致。

### 交付

1. 报告文件路径
2. 同步文章到 Obsidian「公众号工作流」（必做）：把长图里的**文章内容（带排版）**同步到 Obsidian 一份——这是用户的长期约定。
   ⚠️ **只放文章内容 + 排版（Markdown），绝不嵌入长图 PNG 本身。**
   ```bash
   /Users/zhangwei/.workbuddy/binaries/python/versions/3.13.12/bin/python3 \
     ~/.workbuddy/skills/zw-card/sync_obsidian.py \
     --input <长图.html> [--date 2026-07-11]
   ```
   - 脚本自动提取长图 HTML 的文字与结构（标题 / `##` 章节 / 金句 `[!quote]` callout / 列表 / 来源），
     渲染为 Obsidian Markdown，写入 `~/Obsidian/张伟的obsidian/公众号工作流/<标题>.md`。
   - 仅取文字与层级，**不复制、不嵌入长图 PNG**。适用于所有承载文章内容的模具（-l / -i / -v / -w 等）；
     纯单句装饰模具（-b 大字）也会生成极简笔记，无害。

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
