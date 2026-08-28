#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
zw-summary 统一视频总结工具（B站 + YouTube）

支持：
  - B站 BV 号 / 链接
  - YouTube 链接 / video_id（自动走本机代理）

流程：字幕优先（B站字幕 / YouTube 字幕）→ 无字幕降级 Whisper 本地识别
      → AI 双 Pass 清洗纠错 → AI 生成中文总结

用法:
  python3 zw_summary.py BV1XHwWzVEmF
  python3 zw_summary.py https://www.youtube.com/watch?v=dQw4w9WgXcQ

配置文件（zw_config.json，与脚本同目录）:
  {
    "bilibili": {"cookie": {"SESSDATA": "", "bili_jct": "", "buvid3": ""}},
    "ai": {"api_key": "", "base_url": "https://api.deepseek.com/v1", "model": "deepseek-v4-flash"},
    "whisper": {"model": "base"},
    "error_correction": "dual",
    "proxy": ""
  }

依赖:
  托管 venv 需装 yt-dlp；whisper 走系统 Python venv（见 whisper_venv）；系统需 ffmpeg
"""

import glob
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# ──────────────────────────────────────────────
# 配置加载
# ──────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "zw_config.json"
AUDIO_DIR = SCRIPT_DIR / "audio"
AUDIO_DIR.mkdir(exist_ok=True)

DEFAULT_CONFIG = {
    "bilibili": {"cookie": {"SESSDATA": "", "bili_jct": "", "buvid3": ""}},
    "ai": {
        "api_key": "",
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-v4-flash",
    },
    "whisper": {"model": "base"},
    "error_correction": "dual",
    "proxy": "",
}


def load_config():
    cfg = dict(DEFAULT_CONFIG)
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        for k, v in loaded.items():
            if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                cfg[k].update(v)
            else:
                cfg[k] = v
    return cfg


CFG = load_config()


# ──────────────────────────────────────────────
# 平台识别
# ──────────────────────────────────────────────
def detect_platform(arg):
    """从输入判断平台，返回 (platform, id)"""
    arg = arg.strip()
    if "BV" in arg or "bilibili" in arg.lower():
        m = re.search(r"BV[A-Za-z0-9]+", arg)
        if m:
            return "bilibili", m.group(0)
    if re.search(r"youtu\.?be|youtube\.com", arg, re.I):
        m = re.search(
            r"(?:youtu\.be/|youtube\.com/(?:watch\?.*?v=|shorts/|embed/|live/|v/))"
            r"([A-Za-z0-9_-]{11})",
            arg,
        )
        if m:
            return "youtube", m.group(1)
        raise ValueError(f"无法从 YouTube 链接解析 video_id: {arg}")
    if re.search(r"\b(?:x|twitter)\.com", arg, re.I):
        m = re.search(r"/status/(\d+)", arg)
        if m:
            return "x", m.group(1)
        raise ValueError(f"无法从 X 链接解析 status ID: {arg}")
    # 纯 11 位 id 视作 YouTube
    if re.match(r"^[A-Za-z0-9_-]{11}$", arg):
        return "youtube", arg
    raise ValueError(f"无法识别视频链接/ID: {arg}")


# ──────────────────────────────────────────────
# 代理检测
# ──────────────────────────────────────────────
def detect_proxy():
    """返回代理字符串（http://host:port）或 None。
    优先级：macOS 系统代理(scutil，Shadowrocket/Clash 设置的权威源) → 环境变量 → 配置 proxy"""
    try:
        out = subprocess.run(
            ["scutil", "--proxy"], capture_output=True, text=True, timeout=5
        ).stdout
        if "HTTPSEnable : 1" in out:
            m = re.search(r"HTTPSPort\s*:\s*(\d+)", out)
            if m:
                return f"http://127.0.0.1:{m.group(1)}"
        if "HTTPEnable : 1" in out:
            m = re.search(r"HTTPPort\s*:\s*(\d+)", out)
            if m:
                return f"http://127.0.0.1:{m.group(1)}"
    except Exception:
        pass
    for var in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy", "ALL_PROXY", "all_proxy"):
        v = os.environ.get(var)
        if v:
            return v
    p = CFG.get("proxy", "")
    return p or None


def download_text_url(url, proxy=None):
    """带代理下载文本内容"""
    opener = None
    if proxy:
        opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({"http": proxy, "https": proxy})
        )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    if opener:
        with opener.open(req, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="ignore")


# ──────────────────────────────────────────────
# B站 API（含 wbi 签名，用于 AI 字幕真实地址）
# ──────────────────────────────────────────────
def make_bili_headers(sessdata=""):
    h = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.bilibili.com"}
    if sessdata:
        h["Cookie"] = f"SESSDATA={sessdata}"
    return h


def http_get_json(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


_WBI_PERM = [46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43,
             5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16,
             24, 55, 40, 61, 26, 17, 0, 1, 57, 22, 25, 34, 46, 52, 11, 44, 54, 36,
             4, 21, 56, 59, 6, 60, 20, 51, 30, 62, 63]


def _wbi_mixin_key(orig):
    return "".join(orig[i] for i in _WBI_PERM)[:32]


def _wbi_sign(params, sessdata=""):
    nav = http_get_json(
        "https://api.bilibili.com/x/web-interface/nav", make_bili_headers(sessdata)
    )
    img = re.search(r"([0-9a-f]+)\.png", nav["data"]["wbi_img"]["img_url"]).group(1)
    sub = re.search(r"([0-9a-f]+)\.png", nav["data"]["wbi_img"]["sub_url"]).group(1)
    mixin = _wbi_mixin_key(img + sub)
    params["wts"] = int(time.time())
    s = "".join(f"{k}={params[k]}" for k in sorted(params))
    params["w_rid"] = hashlib.md5((s + mixin).encode()).hexdigest()
    return params


def get_bilibili_meta(bvid, sessdata=""):
    data = http_get_json(
        f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}",
        make_bili_headers(sessdata),
    )
    if data.get("code") != 0:
        raise RuntimeError(f"获取B站视频信息失败: {data.get('message')}")
    info = data["data"]
    return {
        "platform": "bilibili",
        "id": bvid,
        "title": info.get("title", "未知"),
        "uploader": info.get("owner", {}).get("name", ""),
        "duration": info.get("duration", 0),
        "view": info.get("stat", {}).get("view", 0),
        "desc": info.get("desc", "").strip(),
        "cid": info.get("cid"),
        "url": f"https://www.bilibili.com/video/{bvid}/",
    }


def get_bilibili_subtitles(bvid, cid, sessdata=""):
    """优先 wbi 接口（可返回 ai-zh 真实地址），失败回退普通接口"""
    subs = []
    try:
        params = _wbi_sign({"bvid": bvid, "cid": cid}, sessdata)
        q = "&".join(f"{k}={urllib.parse.quote(str(params[k]))}" for k in params)
        data = http_get_json(
            f"https://api.bilibili.com/x/player/wbi/v2?{q}", make_bili_headers(sessdata)
        )
        if data.get("code") == 0:
            subs = data.get("data", {}).get("subtitle", {}).get("subtitles", [])
            if subs:
                return subs
    except Exception:
        pass
    data = http_get_json(
        f"https://api.bilibili.com/x/player/v2?bvid={bvid}&cid={cid}",
        make_bili_headers(sessdata),
    )
    if data.get("code") != 0:
        return []
    return data.get("data", {}).get("subtitle", {}).get("subtitles", [])


def bilibili_subtitle_to_text(url):
    if url.startswith("//"):
        url = "https:" + url
    body = http_get_json(url, {"User-Agent": "Mozilla/5.0"}).get("body", [])
    return "\n".join(
        item.get("content", "").strip() for item in body if item.get("content", "").strip()
    )


# ──────────────────────────────────────────────
# YouTube（yt-dlp 元数据 + 字幕）
# ──────────────────────────────────────────────
YT_SUB_LANG_PRIORITY = [
    "zh-Hans", "zh-CN", "zh", "zh-Hant", "zh-TW", "zh-HK",
    "en", "en-US", "en-GB", "en-orig",
]


def get_stream_meta(video_id, url, platform, proxy=None):
    """yt-dlp 提取元数据（YouTube / X 通用）"""
    import yt_dlp
    ydl_opts = {"quiet": True, "noplaylist": True, "skip_download": True}
    if proxy:
        ydl_opts["proxy"] = proxy
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return {
        "platform": platform,
        "id": video_id,
        "title": info.get("title", "未知"),
        "uploader": info.get("uploader") or info.get("channel", ""),
        "duration": int(info.get("duration") or 0),
        "view": int(info.get("view_count") or 0),
        "desc": (info.get("description") or "").strip(),
        "cid": None,
        "url": url,
        "_info": info,
    }


def vtt_to_text(vtt):
    """把 VTT 字幕解析为纯文本"""
    out = []
    for line in vtt.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.upper().startswith("WEBVTT") or line.upper().startswith("NOTE"):
            continue
        if "-->" in line or re.match(r"^\d{2}:\d{2}:\d{2}", line):
            continue
        if re.match(r"^[0-9a-f-]{8,}$", line):
            continue
        line = re.sub(r"<[^>]+>", "", line)  # 去 <c> 等标签
        line = html.unescape(line)
        line = line.strip()
        if line and not re.match(r"^\[.*\]$", line):  # 去 [音乐]/[掌声] 等
            out.append(line)
    return "\n".join(out)


def youtube_subtitle_to_text(raw):
    """解析 YouTube 字幕（自动识别 JSON3 / VTT 两种格式）。
    JSON3: events[].segs[].utf8 逐段拼接（空格/换行是独立 segment）"""
    raw = raw.strip()
    if raw.startswith("{"):
        try:
            data = json.loads(raw)
            lines = []
            for event in data.get("events", []):
                seg_text = "".join(
                    (seg.get("utf8") or "") for seg in event.get("segs", [])
                ).strip()
                if seg_text and re.search(r"[\u4e00-\u9fffA-Za-z0-9]", seg_text):
                    lines.append(seg_text)
            if lines:
                return "\n".join(lines)
        except (json.JSONDecodeError, AttributeError, TypeError):
            pass
    return vtt_to_text(raw)


def get_youtube_subtitle(meta, proxy=None):
    """优先手动字幕，其次自动字幕；语言中文优先、英文兜底。返回 (text, source)"""
    info = meta.get("_info") or {}
    for pool, src in (
        (info.get("subtitles") or {}, "youtube_subtitle"),
        (info.get("automatic_captions") or {}, "youtube_autosub"),
    ):
        for lang in YT_SUB_LANG_PRIORITY:
            entries = pool.get(lang) or []
            if not entries:
                continue
            url = entries[0].get("url")
            if not url:
                continue
            try:
                raw = download_text_url(url, proxy)
                text = youtube_subtitle_to_text(raw)
                if len(text) > 100:
                    print(f"✅ YouTube 字幕可用（{lang}，{len(text)} 字）")
                    return text, src
            except Exception as e:
                print(f"⚠️  YouTube 字幕 {lang} 下载失败（{e}）")
    return "", "none"


def get_x_subtitle(meta, proxy=None):
    """X/Twitter 字幕（HLS 字幕流）：用 yt-dlp 下载合并为 vtt 再解析。返回 (text, source)"""
    vid = meta["id"]
    tmpdir = tempfile.mkdtemp(prefix="xsub_")
    try:
        import yt_dlp
        ydl_opts = {
            "skip_download": True,
            "writesubtitles": True,
            "subtitleslangs": ["en", "zh", "zh-Hans", "zh-CN", "zh-Hant"],
            "subtitlesformat": "vtt",
            "outtmpl": tmpdir + "/%(id)s.%(ext)s",
            "proxy": proxy,
            "quiet": True,
            "noplaylist": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([meta["url"]])
        vtt_files = glob.glob(tmpdir + "/*.vtt")
        if vtt_files:
            text = vtt_to_text(Path(vtt_files[0]).read_text(encoding="utf-8"))
            if len(text) > 100:
                print(f"✅ X 字幕可用（{len(text)} 字）")
                return text, "x_subtitle"
            print(f"⚠️  X 字幕内容过短（{len(text)} 字），切换到 Whisper")
    except Exception as e:
        print(f"⚠️  X 字幕下载失败（{e}），切换到 Whisper")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    return "", "none"


# ──────────────────────────────────────────────
# 字幕校验
# ──────────────────────────────────────────────
def validate_subtitle(candidate, title):
    cn_title = set(re.sub(r"[^\u4e00-\u9fff]", " ", title).split())
    cn_sub = set(re.sub(r"[^\u4e00-\u9fff]", " ", candidate[:500]).split())
    cn_overlap = cn_title & cn_sub
    en_title = set(w.lower() for w in re.findall(r"[a-zA-Z0-9]{3,}", title))
    en_sub = set(w.lower() for w in re.findall(r"[a-zA-Z0-9]{3,}", candidate[:500]))
    en_overlap = en_title & en_sub
    return len(candidate) > 100 and (len(cn_overlap) >= 1 or len(en_overlap) >= 1)


# ──────────────────────────────────────────────
# 音频下载 + Whisper
# ──────────────────────────────────────────────
COOKIE_FILE = AUDIO_DIR / "bili_cookies.txt"

# 音频处理完成后即清理，仅保留文本缓存（subtitle/transcript/clean）以备复用
AUDIO_EXTS = (".m4a", ".wav", ".mp3", ".aac", ".opus", ".webm")


def cleanup_audio_files(vid):
    """删除指定视频的音频文件；文本缓存（字幕/转写/清洗）保留复用"""
    removed = []
    for f in glob.glob(str(AUDIO_DIR / f"{vid}.*")):
        if f.lower().endswith(AUDIO_EXTS):
            try:
                os.remove(f)
                removed.append(Path(f).name)
            except OSError:
                pass
    if removed:
        print(f"🧹 音频文件已清理: {', '.join(removed)}")


def generate_cookie_file(cfg):
    cookie = (cfg.get("bilibili") or {}).get("cookie", {})
    sessdata = cookie.get("SESSDATA", "")
    if not sessdata:
        return False
    expiry = int(time.time()) + 86400 * 365
    lines = [
        "# Netscape HTTP Cookie File",
        ".bilibili.com\tTRUE\t/\tTRUE\t" + str(expiry) + "\tSESSDATA\t" + sessdata,
        ".bilibili.com\tTRUE\t/\tTRUE\t" + str(expiry) + "\tbili_jct\t" + cookie.get("bili_jct", ""),
        ".bilibili.com\tTRUE\t/\tFALSE\t" + str(expiry) + "\tbuvid3\t" + cookie.get("buvid3", ""),
    ]
    with open(COOKIE_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return True


def get_cookie_file(cfg):
    if COOKIE_FILE.exists():
        return str(COOKIE_FILE)
    if generate_cookie_file(cfg):
        return str(COOKIE_FILE)
    return None


def find_audio_cache(vid):
    for f in glob.glob(str(AUDIO_DIR / f"{vid}.*")):
        if not f.endswith((".txt", ".vtt", ".srt", ".json")):
            return f
    return None


def download_audio(vid, url, cfg, proxy=None):
    """yt-dlp 下载音频；已有缓存直接复用。proxy 仅 YouTube 需要"""
    import yt_dlp

    cached = find_audio_cache(vid)
    if cached:
        print(f"📂 复用已有音频: {cached}")
        return cached

    print("⬇️  下载音频中...")
    if "x.com" in url or "twitter.com" in url:
        referer = "https://x.com/"
    elif "bilibili" in url:
        referer = "https://www.bilibili.com"
    else:
        referer = "https://www.youtube.com/"
    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "outtmpl": str(AUDIO_DIR / f"{vid}.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Referer": referer,
        },
    }
    if proxy:
        ydl_opts["proxy"] = proxy
        print("🛰  使用代理下载")
    cookie_path = get_cookie_file(cfg)
    if cookie_path:
        ydl_opts["cookiefile"] = cookie_path

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    cached = find_audio_cache(vid)
    if not cached:
        raise RuntimeError("音频下载失败，未找到输出文件")
    return cached


_WHISPER_VENV = SCRIPT_DIR.parent / "whisper_venv/bin/python3"


def transcribe_with_whisper(audio_path, model_name="base", language="auto"):
    """Whisper 本地识别（子进程调用系统 Python venv）。language="auto" 自动检测"""
    code = (
        "import sys, whisper\n"
        "audio_path = sys.argv[1]\n"
        "model_name = sys.argv[2]\n"
        "lang = sys.argv[3] if len(sys.argv) > 3 else 'auto'\n"
        "model = whisper.load_model(model_name)\n"
        "print('WHISPER_READY', flush=True)\n"
        "kwargs = {}\n"
        "if lang != 'auto':\n"
        "    kwargs['language'] = lang\n"
        "result = model.transcribe(audio_path, **kwargs)\n"
        "print(result['text'])\n"
    )
    script_file = tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    )
    try:
        script_file.write(code)
        script_file.close()
        print(f"🔊 加载 Whisper {model_name} 模型（language={language}）...")
        proc = subprocess.run(
            [str(_WHISPER_VENV), script_file.name, audio_path, model_name, language],
            capture_output=True, text=True, timeout=3600,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"Whisper 子进程失败: {proc.stderr.strip()}")
        lines = [l for l in proc.stdout.strip().split("\n") if l != "WHISPER_READY"]
        return "\n".join(lines)
    finally:
        try:
            os.unlink(script_file.name)
        except OSError:
            pass


# ──────────────────────────────────────────────
# 文字稿获取（字幕优先 → Whisper 兜底）
# ──────────────────────────────────────────────
_SUBTITLE_SOURCE = {"bilibili": "bilibili_subtitle", "x": "x_subtitle", "youtube": "youtube_subtitle"}
# 只有识别类来源才需要 AI 清洗纠错；手动/官方字幕质量高，跳过清洗（省时省 token，也避免 AI 改错原文）
_NEED_CLEAN_SOURCES = {"whisper", "youtube_autosub", "bilibili_subtitle"}


def get_transcript(meta, cfg, proxy=None):
    vid = meta["id"]
    platform = meta["platform"]

    # 缓存复用（跨平台按 id 区分）
    sub_cache = AUDIO_DIR / f"{vid}.subtitle.txt"
    if sub_cache.exists():
        cached = sub_cache.read_text(encoding="utf-8")
        if len(cached) > 100 and validate_subtitle(cached, meta["title"]):
            print(f"📂 复用已缓存字幕: {sub_cache}")
            return cached, _SUBTITLE_SOURCE.get(platform, "subtitle")

    # 1. 字幕优先
    text = ""
    source = "none"
    if platform == "bilibili":
        subs = get_bilibili_subtitles(vid, meta.get("cid"), (cfg.get("bilibili") or {}).get("cookie", {}).get("SESSDATA", ""))
        if subs:
            try:
                text = bilibili_subtitle_to_text(subs[0]["subtitle_url"])
                source = "bilibili_subtitle"
            except Exception as e:
                print(f"⚠️  字幕下载失败（{e}），切换到 Whisper")
        if text and not validate_subtitle(text, meta["title"]):
            print("⚠️  B站字幕与标题不匹配，切换到 Whisper")
            text = ""
    elif platform == "x":
        text, source = get_x_subtitle(meta, proxy)
    else:
        text, source = get_youtube_subtitle(meta, proxy)

    if text and source != "none":
        try:
            sub_cache.write_text(text, encoding="utf-8")
        except OSError:
            pass
        return text, source

    # 2. Whisper 兜底
    whisper_model = (cfg.get("whisper") or {}).get("model", "base")
    # B站默认中文；YouTube 自动检测（中英文都支持）
    lang = "zh" if platform == "bilibili" else "auto"
    return get_whisper_transcript(meta, cfg, whisper_model, lang, proxy)


def get_whisper_transcript(meta, cfg, whisper_model, language, proxy=None):
    vid = meta["id"]
    cache = AUDIO_DIR / f"{vid}.transcript.txt"
    if cache.exists():
        text = cache.read_text(encoding="utf-8")
        if len(text) > 50:
            print(f"📂 复用已识别文字稿: {cache}")
            return text, "whisper"

    print("🎙  使用 Whisper 本地语音识别...")
    try:
        audio_path = download_audio(vid, meta["url"], cfg, proxy)
        transcript = transcribe_with_whisper(audio_path, whisper_model, language)
        try:
            cache.write_text(transcript, encoding="utf-8")
        except OSError:
            pass
        print(f"✅ Whisper 识别完成（{len(transcript)} 字）")
        cleanup_audio_files(vid)
        return transcript, "whisper"
    except Exception as e:
        print(f"❌ 语音识别失败: {e}")
        return "", "none"


# ──────────────────────────────────────────────
# AI 调用与总结（输出统一中文）
# ──────────────────────────────────────────────
def _call_ai(messages, cfg, max_tokens):
    api_key = cfg["ai"]["api_key"]
    base_url = cfg["ai"]["base_url"].rstrip("/")
    model = cfg["ai"]["model"]
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": max_tokens,
    }
    url = f"{base_url}/chat/completions"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    last_err = None
    for attempt in range(4):
        wait = (2 ** attempt) * 5
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read())
            content = result["choices"][0]["message"]["content"].strip()
            if content:
                return content
            print(f"⚠️  AI 返回空内容，{wait}s 后重试 ({attempt+1}/4)...")
            time.sleep(wait)
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code == 429 or e.code >= 500:
                print(f"⚠️  AI 接口返回 {e.code}，{wait}s 后重试 ({attempt+1}/4)...")
                time.sleep(wait)
            else:
                raise
        except Exception as e:
            last_err = e
            print(f"⚠️  AI 调用异常({e})，{wait}s 后重试 ({attempt+1}/4)...")
            time.sleep(wait)
    raise last_err or RuntimeError("AI 多次返回空内容，已放弃")


def _split_into_chunks(text, max_chars=12000, overlap=300):
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + max_chars, n)
        if end < n:
            cut = -1
            for i in range(end, max(start + max_chars // 2, start + 1), -1):
                if text[i] in "。！？\n.!?":
                    cut = i + 1
                    break
            if cut > start:
                end = cut
        chunks.append(text[start:end])
        if end >= n:
            break
        start = max(end - overlap, start + 1)
    return chunks


_CLEAN_SYS = (
    "你是一名严谨的字幕/语音识别纠错助手。下面是一段视频转写文本（来自字幕或 Whisper 语音识别），"
    "可能含有同音/近音错别字、英文术语误听、人名/公司名/产品名混淆等识别错误。"
    "请仅做最小必要修正：结合上下文语义，纠正明显的人名、机构名、产品名、英文术语、数字单位等误听；"
    "保持原文的句子结构、分段、标点和所有直接引述不变；不要增删内容、不要改写风格、不要翻译、不要概括。"
    "仅在结合上下文高置信度时修改，不确定则保留原词，严禁臆造。"
    "直接输出纠错后的文本，不要任何解释或客套语。"
)

_SUMMARY_SYS = (
    "你是专业的视频内容分析师，擅长将视频原文整理成详细、有价值的中文总结报告。"
    "无论视频转写原文是什么语言（中文或英文），最终总结一律使用简体中文输出。"
    "【语言要求】全文用通顺的简体中文撰写：英文原话一律翻译成中文，严禁中英混杂、严禁照抄英文长句、"
    "严禁用引号标注大段英文原文。仅保留必要的专有名词与术语原文——如人名、机构名、公司名、产品名、"
    "品牌名、项目/论文名、专业术语（例如 Fei-Fei Li、ImageNet、Stanford HAI、Sora、AlphaGo、"
    "Transformer 等），以及精确数字和单位。"
    "总结时要忠于原文，内容翔实、全面、准确，不遗漏重要信息、不添油加醋。"
    "注意：待总结的原文来自视频语音识别或字幕，可能存在同音/近音错别字、英文术语误听、"
    "人名/公司名/产品名混淆等问题。请先结合上下文语义自动纠正明显的识别错误"
    "（尤其人名、机构名、产品名、英文术语、数字），再据此总结。"
    "纠正原则：仅在结合上下文高置信度时纠正，不确定则保留原词，严禁臆造或替换成无关内容。"
    "直接输出总结正文，不要复述指令、不要以“好的/收到/当然”等客套语开头。"
)

_SUMMARY_REQ = """请根据以上内容，生成一份详尽、完整的中文视频总结，要求如下：

1. **核心主题**
   用2-3句话概括视频主旨。

2. **内容详解**（按视频讲述顺序完整展开，覆盖视频涉及的所有主要话题，不设数量上限）
   每个话题：
   - 写清楚讲了什么、怎么说的、关键论据与例子
   - **用中文准确转述原文的关键信息、观点、数据**，仅保留必要的专有名词/术语原文
   - 补充必要的背景或说明

3. **重要细节 / 干货**
   完整列举原文中提到的具体方法、步骤、数字、案例、技巧、人名、机构、作品等，尽量不遗漏。

4. **关键结论**
   总结最终观点或行动建议。

注意：总结要详尽、完整、准确，**不要精简、不要过度概括、不要压缩信息**。篇幅尽量充分，宁可长一些、信息密度高一些，也要让读者读完后能完整还原视频的全部信息。
全文一律使用简体中文，英文原话翻译成中文，不要中英混杂、不要照抄英文长句、不要用引号标注英文原文。"""


def clean_transcript(text, meta, cfg):
    if cfg.get("error_correction", "dual") != "dual" or not text:
        return text
    vid = meta["id"]
    cc = AUDIO_DIR / f"{vid}.clean.txt"
    if cc.exists():
        cached = cc.read_text(encoding="utf-8")
        if len(cached) > 50:
            print("📂 复用已清洗文字稿")
            return cached

    clean_chunk = 9000
    if len(text) <= clean_chunk:
        cleaned = _call_ai(
            [{"role": "system", "content": _CLEAN_SYS},
             {"role": "user", "content": "待纠错文本：\n" + text}],
            cfg, 48000,
        )
    else:
        chunks = _split_into_chunks(text, max_chars=clean_chunk, overlap=0)
        print(f"🧹 双 Pass：清洗分 {len(chunks)} 块...")
        parts = []
        for i, ch in enumerate(chunks, 1):
            c = _call_ai(
                [{"role": "system", "content": _CLEAN_SYS},
                 {"role": "user", "content": f"这是第 {i}/{len(chunks)} 段，待纠错文本：\n{ch}"}],
                cfg, 48000,
            )
            parts.append(c)
            print(f"  ✅ 清洗 {i}/{len(chunks)} 完成")
        cleaned = "\n".join(parts)

    try:
        (AUDIO_DIR / f"{vid}.clean.txt").write_text(cleaned, encoding="utf-8")
    except OSError:
        pass
    return cleaned


def summarize_with_ai(transcript, meta, cfg, source="whisper"):
    title = meta.get("title", "")
    uploader = meta.get("uploader", "")
    desc = meta.get("desc", "")
    duration = meta.get("duration", 0)
    m, s = divmod(duration, 60)

    header = f"视频标题：{title}\n作者：{uploader}\n时长：{m}分{s}秒"
    if desc:
        header += f"\n简介：{desc[:200]}"

    # 仅识别类来源（whisper/自动字幕/B站AI字幕）需要清洗纠错；手动/官方字幕质量高，跳过清洗
    if (
        transcript
        and cfg.get("error_correction", "dual") == "dual"
        and source in _NEED_CLEAN_SOURCES
    ):
        transcript = clean_transcript(transcript, meta, cfg)

    if not transcript:
        user_msg = f"{header}\n\n（无字幕，请根据标题和简介总结）\n\n{_SUMMARY_REQ}"
        return _call_ai(
            [{"role": "system", "content": _SUMMARY_SYS},
             {"role": "user", "content": user_msg}],
            cfg, 10000,
        )

    if len(transcript) <= 14000:
        user_msg = f"{header}\n\n视频转写内容（原文）：\n{transcript}\n\n{_SUMMARY_REQ}"
        return _call_ai(
            [{"role": "system", "content": _SUMMARY_SYS},
             {"role": "user", "content": user_msg}],
            cfg, 10000,
        )

    chunks = _split_into_chunks(transcript, max_chars=12000, overlap=300)
    print(f"📚 长文本分 {len(chunks)} 块总结中...")
    parts = []
    for i, ch in enumerate(chunks, 1):
        prompt = (
            f"{header}\n\n这是视频转写的第 {i}/{len(chunks)} 段原文，请详细整理本段内容：\n"
            f"- 写清楚本段讲了什么、怎么说的、有哪些具体论点\n"
            f"- **完整保留本段的关键信息、观点、数据、案例、例子**，不要遗漏\n"
            f"- 用中文准确转述，仅保留必要的专有名词/术语原文\n"
            f"- 不要写总体结论\n\n"
            f"本段原文：\n{ch}"
        )
        part = _call_ai(
            [{"role": "system", "content": "你是视频内容分析师，擅长详细整理段落内容。"
              "本段原文来自语音识别或字幕，可能有识别错误；整理前请先结合上下文纠正本段明显的人名、"
              "产品名、机构名、英文术语等误听，再据此整理；不确定则保留原词，不要臆造。"
              "无论原文是中文还是英文，一律用简体中文输出：英文原话翻译成中文，"
              "仅保留必要的专有名词/术语原文，严禁照抄英文长句。"
              "要求详细、完整，不要精简、不要压缩信息。"
              "直接输出正文，不要复述指令或以客套语开头。"},
             {"role": "user", "content": prompt}],
            cfg, 12000,
        )
        parts.append(f"【第{i}段要点】\n{part}")
        print(f"  ✅ 第 {i}/{len(chunks)} 块完成")

    combined = "\n\n".join(parts)
    integrate = (
        f"{header}\n\n以下是该视频各段落的要点摘录，请整合为一份完整、连贯的中文总结，"
        f"必须包含「核心主题 / 内容详解 / 重要细节 / 关键结论」四个部分。"
        f"直接输出总结正文，不要任何客套语、前言或说明。\n\n"
        f"{combined}\n\n{_SUMMARY_REQ}"
    )
    print("🔗 整合各块要点为完整总结...")
    summary = _call_ai(
        [{"role": "system", "content": _SUMMARY_SYS},
         {"role": "user", "content": integrate}],
        cfg, 48000,
    )
    for _ in range(2):
        tail = summary.rstrip()
        if "关键结论" in tail and tail[-1] in "。！？”)”":
            break
        print("  ↳ 总结疑似被截断，自动续写补全...")
        cont = _call_ai(
            [{"role": "system", "content": _SUMMARY_SYS},
             {"role": "user", "content":
                f"以下是已写出的总结前半部分：\n\n{summary}\n\n请直接从中断处继续写下去，"
                f"补全剩余内容，重点是完成「关键结论」部分。不要重复已有内容，直接续写。"}],
            cfg, 24000,
        )
        summary = summary.rstrip() + "\n" + cont
    return summary


# ──────────────────────────────────────────────
# 输出保存
# ──────────────────────────────────────────────
PLATFORM_LABEL = {"bilibili": "B站", "youtube": "YouTube", "x": "X/Twitter"}


def save_summary_file(meta, source, summary):
    m, s = divmod(meta.get("duration", 0), 60)
    header = f"""## 视频总结报告

| 项目 | 内容 |
|------|------|
| **平台** | {PLATFORM_LABEL.get(meta.get('platform'), meta.get('platform'))} |
| **视频ID** | {meta.get('id')} |
| **标题** | {meta.get('title')} |
| **作者** | {meta.get('uploader')} |
| **时长** | {m:02d}:{s:02d} |
| **播放量** | {meta.get('view', 0):,} |
| **来源** | {source} |

"""
    desc = meta.get("desc", "")
    if desc:
        header += f"> {desc}\n\n---\n\n"
    else:
        header += "---\n\n"

    content = header + summary

    obsidian_dir = Path.home() / "Obsidian/张伟的obsidian/视频总结"
    safe_title = re.sub(r'[<>:"/\\|?*]', "_", meta.get("title", "视频"))
    try:
        obsidian_dir.mkdir(parents=True, exist_ok=True)
        out_file = obsidian_dir / f"{safe_title}.md"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(content)
    except (PermissionError, OSError):
        out_file = Path.cwd() / f"{meta['id']}_视频总结.md"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(content)
    return str(out_file)


# ──────────────────────────────────────────────
# 主程序
# ──────────────────────────────────────────────
def main():
    args = sys.argv[1:]
    raw = next((a for a in args if a.strip()), None)
    if not raw:
        print("\n🎬 zw-summary 视频总结工具（B站 + YouTube）")
        print("用法: python3 zw_summary.py <BV号/B站链接/YouTube链接/video_id>")
        raw = input("请输入链接或ID: ").strip()
        if not raw:
            return

    platform, vid = detect_platform(raw)
    proxy = detect_proxy()
    print(f"\n📡 识别平台: {platform} | ID: {vid}")
    if proxy:
        print(f"🛰  检测到代理: {proxy}")

    # 元数据
    if platform == "bilibili":
        sessdata = (CFG.get("bilibili") or {}).get("cookie", {}).get("SESSDATA", "")
        meta = get_bilibili_meta(vid, sessdata)
    else:
        url = (
            f"https://www.youtube.com/watch?v={vid}"
            if platform == "youtube"
            else f"https://x.com/i/status/{vid}"
        )
        meta = get_stream_meta(vid, url, platform, proxy)

    print(f"🎬 {meta['title']}")

    # 文字稿
    transcript, source = get_transcript(meta, CFG, proxy)

    # AI 总结
    print("\n🤖 生成总结中...")
    ai_failed = False
    try:
        summary = summarize_with_ai(transcript, meta, CFG, source)
    except Exception as e:
        print(f"❌ AI总结失败: {e}")
        ai_failed = True

    if ai_failed:
        print("⚠️  已保存原始文字稿，待 AI 接口恢复后重跑本脚本即可复用缓存重新总结")
        fallback = (
            "⚠️ **AI 自动总结失败**（接口可能限流/不可用），"
            "以下为原始文字稿，待接口恢复后重跑本脚本（已缓存可秒复用）或人工整理。\n\n---\n\n"
        )
        if transcript:
            fallback += f"## 原始文字稿（{len(transcript)} 字，来源：{source}）\n\n{transcript}"
        else:
            fallback += "（无可用文字稿）"
        summary = fallback

    output_path = save_summary_file(meta, source, summary)

    # 兜底清理：无论走字幕还是 Whisper 路径，确保本视频音频不残留（文本缓存保留）
    cleanup_audio_files(vid)

    sep = "=" * 60
    print(f"\n{sep}")
    print(f"📹 {meta['title']}")
    print(f"👤 {meta['uploader']}  |  👁 {meta['view']:,}  |  📝 来源: {source}")
    print(sep)
    print(summary)
    print(sep)
    print(f"\n📄 总结已保存: {output_path}")


if __name__ == "__main__":
    main()
