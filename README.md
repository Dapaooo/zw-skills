# zw-skills

张伟的 zw- 系列 WorkBuddy 技能集。覆盖内容创作全链路：视频总结 → 文章写作 → 文风审核 → 公众号推送 → 卡片生成。

## 技能清单

| 技能 | 用途 |
|------|------|
| [zw-summary](zw-summary/) | 视频内容总结（B站 / YouTube / X），自动获取字幕，无字幕降级 Whisper 语音识别 |
| [zw-writes](zw-writes/) | 文章写作：主题内容 → 确认 → 成文（1500-2000 字思辨随笔），写入本地 + 同步 Obsidian |
| [zw-wenfeng-review](zw-wenfeng-review/) | 文风与内容编排审核，输出逐项审核报告 |
| [zw-wechat-draft](zw-wechat-draft/) | 将文章提炼为公众号图文 / 贴图草稿，推送到公众号草稿箱 |
| [zw-card](zw-card/) | 内容铸卡：长图卡片、信息图、多卡阅读卡等 7 种形态的 PNG 视觉 |
| [zw-content-flow](zw-content-flow/) | 选题内容流水线：选题 → 联网调研提炼观点 → 铸卡 → 公众号图文推送 |
| [zw-read](zw-read/) | 低 Token 成本共读模式 |

## 安装（其他 Agent）

将技能目录放入 `~/.workbuddy/skills/` 即可，例如：

```bash
git clone https://github.com/Dapaooo/zw-skills.git
mkdir -p ~/.workbuddy/skills
cp -r zw-skills/zw-* ~/.workbuddy/skills/
```

## 首次使用需自行配置

技能运行所需的凭据**不在此仓库**（避免泄露），按需创建：

### zw-summary（B站 + LLM）

```bash
cp zw-summary/scripts/zw_config.example.json zw-summary/scripts/zw_config.json
```

填入你的 B站 cookie（SESSDATA / bili_jct / buvid3）和 LLM API Key。

### zw-wechat-draft（微信公众号）

创建 `~/.workbuddy/wechat_config.json`：

```json
{ "appId": "你的AppID", "appSecret": "你的AppSecret" }
```

> 注意：微信公众平台有 IP 白名单限制，推送失败时需将本机出口 IP 加入白名单，详见 [zw-wechat-draft/references/deploy.md](zw-wechat-draft/references/deploy.md)。

## 依赖

- zw-card：需要 `node_modules`（playwright-core），进入目录后 `npm install`（见其 `package.json`）
- zw-summary：Whisper 本地识别需要 Python 虚拟环境，见技能内 SKILL.md

## 维护

仓库结构：每个技能一个目录，内含 `SKILL.md` 与脚本/资源。更新技能后：

```bash
git add -A && git commit -m "update" && git push
```

## 同步约定

- 本地 `ljg-*` / `zw-*` 技能若带自定义字段（如 `disable-model-invocation: true`），同步时必须保留。
- 仅推送技能本体；`node_modules`、`whisper_venv`、字幕/音频缓存、含真实凭据的配置一律不入库（见 `.gitignore`）。
