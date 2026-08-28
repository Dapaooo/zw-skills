---
name: zw-summary
description: 统一视频内容总结技能（B站 + YouTube + X/Twitter）。当用户提供B站BV号/链接、YouTube链接/video_id、X/Twitter推文视频链接，要求总结/分析视频内容时使用。自动获取字幕（B站字幕 / YouTube 字幕 / X 字幕，中英文均支持），无字幕降级 Whisper 本地语音识别，AI 双 Pass 纠错后生成详细中文总结（无论原文中英文，输出统一简体中文）。YouTube/X 自动走本机代理下载。
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - WebFetch
---

# zw-summary 统一视频总结技能（B站 + YouTube + X/Twitter）

## 使用方法

用户提供 B站（BV号/链接）、YouTube（链接/11位 video_id）或 X/Twitter（推文视频链接，`x.com/用户/status/数字ID`）后，执行：

1. 运行脚本（务必设置长超时 + 放行网络，见下方"注意事项"）。必须用 **venv python**（已装 yt_dlp）运行：
   `/Users/zhangwei/.workbuddy/binaries/python/envs/default/bin/python /Users/zhangwei/.workbuddy/skills/zw-summary/scripts/zw_summary.py <BV号 或 YouTube链接 或 X链接>`
2. 脚本自动：识别平台 → 取元数据 → 字幕优先/Whisper 兜底 → AI 中文总结 → 保存 Markdown
3. 用 `present_files` 交付总结文件，并在回复中给出总结要点概览

## 脚本输出说明

终端输出：
- 平台/ID/代理检测结果
- 视频元数据（标题、作者、播放量、时长）
- 转录来源（`bilibili_subtitle` / `youtube_subtitle` / `youtube_autosub` / `whisper`）
- 完整 AI 总结正文
- 最后一行 `📄 总结已保存: /path/to/xxx.md`

## 配置文件

- 位置：`scripts/zw_config.json`
- `bilibili.cookie`：B站登录态（SESSDATA 等，复用原 bili-summary）
- `ai`：AI 后端（DeepSeek，api_key/base_url/model 可替换）
- `whisper.model`：Whisper 模型（`base` 默认，`small` 更准但更慢）
- `error_correction`：`dual`（默认，双 Pass 纠错）/ `single`（关闭清洗，省一次调用）。注意：即便 `dual`，也**只对识别类来源清洗**（Whisper 转写、自动字幕、B站AI字幕）；手动/官方字幕（X 官方字幕、YouTube 创作者字幕）质量高，自动跳过清洗直接总结。
- `proxy`：代理地址。**留空则自动检测**（环境变量 → macOS 系统代理 scutil → 此字段）

## 架构说明

### 双平台统一数据流

```
输入链接 → detect_platform 识别平台
   ├─ B站:      wbi 签名拿字幕 → 匹配失败 → yt-dlp 下音频(直连) → Whisper(zh)
   ├─ YouTube:  yt-dlp 元数据 + 字幕(中/英) → 无字幕 → yt-dlp 下音频(代理) → Whisper(auto)
   └─ X/Twitter: yt-dlp 元数据 + 字幕(HLS 流，en/zh) → 无字幕 → yt-dlp 下音频(代理) → Whisper(auto)
          ↓
   AI 第一遍清洗纠错（dual 模式）→ 缓存 .clean.txt
          ↓
   AI 第二遍生成中文总结 → 保存 Markdown（Obsidian 目录优先）
```

### 关键设计

- **字幕语言策略**：YouTube/X 手动字幕优先，其次自动字幕；语言按 `zh-Hans/zh-CN/zh/zh-Hant/...` 中文优先、`en` 英文兜底。英文视频用英文字幕，AI 总结时统一译成中文。
- **X 字幕特殊性**：X 的字幕是 HLS m3u8 流（不是直接 vtt 文件），用 yt-dlp `writesubtitles` 下载合并成 vtt 后，`vtt_to_text` 去掉 `<X-word-ms>` 逐字标签与时间戳。X 平台无自动字幕，无手动字幕时直接降级 Whisper。
- **Whisper 语言自适应**：B站强制 `zh`（B站视频基本中文）；YouTube/X 用 `auto` 自动检测（英文视频识别英文、中文视频识别中文）。
- **代理**：`detect_proxy()` 自动读取本机 Shadowrocket/Clash 等系统代理（HTTP/HTTPS 端口）。**YouTube/X 下载走代理，B站直连不走代理**。
- **Whisper 运行**：通过系统 Python 3.9 venv（`zw-summary/whisper_venv`）子进程执行，规避托管运行时沙箱代码签名对 PyTorch 的限制。

## 注意事项

- **必须长超时 + 放行网络**：Whisper + AI 总结整体可能超过 Bash 默认超时（约 120s）。建议 `timeout=600000`（10 分钟）+ `dangerouslyDisableSandbox=true`（放行 AI 接口与 YouTube 代理网络）。
- **缓存复用（音频用完即清）**：字幕 `.subtitle.txt`、Whisper `.transcript.txt`、双 Pass `.clean.txt` 缓存在 `scripts/audio/`，重跑秒级复用——AI 总结失败时重跑即可复用文本缓存重新总结，无需重新下载音频。**音频文件（.m4a/.wav 等）转录完成后自动删除，不保留**（`cleanup_audio_files`，主流程结束还有兜底清理）。Whisper 失败时音频暂留以便重试复用，重试成功后即清理；确认不再需要可手动删 `scripts/audio/` 下的音频。转写更新后删对应 `.clean.txt` 强制重新清洗。
- **转录来源为 `none`**：说明字幕与音频都获取失败，需提示用户（YouTube 可能是代理未开/视频受限/需登录）。
- **YouTube 限制**：年龄限制/会员视频需 cookie（当前未配置，可用 yt-dlp `--cookies-from-browser` 提取后放 `audio/cookies.txt` 并改脚本）。公开视频无需 cookie。
- **X/Twitter 限制**：X 无自动字幕，无手动字幕的视频只能靠 Whisper 转写（更慢）。X 被墙，必须走代理。X 视频音频是 HLS 流，Whisper 兜底时需 ffmpeg 合并（已具备）。极长视频（如 2 小时播客）字幕可达数万字，AI 分块清洗+总结耗时较长。
- **代理检测**：若 YouTube 下载失败且检测不到代理，检查代理软件是否开启、或手动在 `zw_config.json` 的 `proxy` 填 `http://127.0.0.1:<端口>`。
- **Whisper 默认 `base` 模型**：英文专有名词识别明显优于 `tiny`，个别术语仍可能听岔（如 MuonClip→"Meal Clip"），交付前需人工校正；需更准可把 `whisper.model` 调 `small`。
- **视频简介里的推广链接**会被当作"原文"混入转写，注意区分演讲者原话与简介内容。
- **推理模型兼容性**：使用 DeepSeek V4 等推理模型时，脚本已放大各阶段 `max_tokens`（清洗 48k、块提取 8k、整合 32k、续写 16k）。切回非推理模型（如 `deepseek-chat`）可调回。若 AI 持续返回空内容，检查 `zw_config.json` 的 `model` 与 `max_tokens`。
- **总结文件路径**：以脚本最后一行 `📄 总结已保存: ...` 为准（优先 Obsidian `~/Obsidian/张伟的obsidian/视频总结/`，无权限回退当前目录）。
