#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_obsidian.py — 把文章内容（带排版）同步到 Obsidian「公众号工作流」文件夹。

- 输入可为 content.json（zw-wechat-draft 产物）或 长图 HTML（zw-card 产物）。
- 输出：Obsidian Markdown 笔记（标题 / 章节 / 金句 callout / 列表 / 来源 等排版）。
- 关键约定：只放「文章内容 + 排版」，绝不嵌入长图 PNG / 封面 PNG。

用法：
  python3 sync_obsidian.py --input <content.json | long.html> \
      [--title ...] [--date ...] [--content-type ...] [--source ...] [--type ...]
"""
import json
import os
import re
import sys
import argparse
import datetime
from html.parser import HTMLParser

OBS_BASE = "/Users/zhangwei/Obsidian/张伟的obsidian/公众号工作流"


def sanitize_filename(name):
    name = (name or "未命名").strip()
    for ch in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
        name = name.replace(ch, " ")
    return name.strip()[:80]


# ---------------- content.json -> md ----------------
def blocks_to_md(blocks):
    out = []
    for b in blocks:
        t = b.get("type")
        if t == "intro":
            txt = (b.get("text") or "").strip()
            if txt:
                out.append(txt)
        elif t == "highlight":
            txt = (b.get("text") or "").strip()
            if txt:
                out.append("> [!quote] " + txt.replace("\n", "\n> "))
        elif t == "quote":
            txt = (b.get("text") or "").strip()
            if txt:
                out.append("> " + txt.replace("\n", "\n> "))
        elif t == "section":
            title = (b.get("title") or "").strip()
            body = (b.get("body") or "").strip()
            out.append(f"## {title}")
            if body:
                out.append(body)
        elif t == "subtitle":
            txt = (b.get("text") or "").strip()
            if txt:
                out.append(f"> [!info] {txt}")
        elif t == "divider":
            out.append("---")
        elif t == "item":
            label = (b.get("label") or "").strip()
            body = (b.get("body") or "").strip()
            out.append(f"- **{label}**：{body}")
        elif t == "list":
            items = b.get("items") or []
            if items:
                out.append("\n".join(f"- {it}" for it in items))
        elif t == "footer":
            txt = (b.get("text") or "").strip()
            if txt:
                out.append(f"> {txt}")
        elif t == "endmark":
            pass
    return "\n\n".join(out)


# ---------------- 长图 HTML -> md ----------------
class CardParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.blocks = []
        self.buf = []
        self.kind = None
        self.in_title_area = False
        self.in_footer = False
        self.in_info_source = False
        self.source_text = ""
        self.in_item = False
        self.in_item_label = False
        self.item_label_buf = []
        self.item_body_buf = []
        self.in_ladder = False
        self.in_step = False
        self.step_buf = []
        self.ladder_steps = []
        self.in_formula = False
        self.in_list = False
        self.list_items = []
        self.list_ordered = False
        self.cur_li = None
        self.skip_idx = False
        self.in_style = False
        self.in_script = False

    def _flush(self):
        if self.kind and self.buf:
            text = "".join(self.buf).strip()
            if text:
                self.blocks.append((self.kind, text))
        self.buf = []
        self.kind = None

    def handle_starttag(self, tag, attrs):
        classes = set()
        for k, v in attrs:
            if k == "class" and v:
                classes = set(v.split())
        if tag == "h1":
            if not self.title:
                self.title = ""
                self.kind = "title"
            return
        if tag in ("h2", "h3", "h4"):
            self._flush()
            self.kind = "h" + tag[1]
            return
        if tag == "p":
            if self.in_item and "label" in classes:
                self.in_item_label = True
                return
            self._flush()
            if "highlight" in classes:
                self.kind = "quote"
            elif "prompt" in classes:
                self.kind = "note"
            elif "subtitle" in classes:
                self.kind = "lead"
            else:
                self.kind = "p"
            return
        if tag == "blockquote":
            self._flush()
            self.kind = "quote"
            return
        if tag == "ul":
            self._flush()
            self.in_list = True
            self.list_ordered = False
            self.list_items = []
            return
        if tag == "ol":
            self._flush()
            self.in_list = True
            self.list_ordered = True
            self.list_items = []
            return
        if tag == "li":
            self._flush()
            self.list_items.append("")
            self.cur_li = len(self.list_items) - 1
            return
        if tag == "div":
            if "title-area" in classes:
                self.in_title_area = True
            elif "footer" in classes:
                self.in_footer = True
            elif "item" in classes:
                self._flush()
                self.in_item = True
                self.in_item_label = False
                self.item_label_buf = []
                self.item_body_buf = []
            elif "ladder" in classes:
                self._flush()
                self.in_ladder = True
                self.ladder_steps = []
            elif "formula" in classes:
                self._flush()
                self.in_formula = True
            elif "conclusion" in classes:
                self._flush()
                self.kind = "summary"
            elif "divider" in classes:
                self._flush()
                self.blocks.append(("divider", ""))
            return
        if tag in ("style", "script"):
            self.in_style = True if tag == "style" else self.in_style
            self.in_script = True if tag == "script" else self.in_script
            self.buf = []
            return
        if tag == "span":
            if "info-source" in classes:
                self.in_info_source = True
            elif "step" in classes and self.in_ladder:
                self.in_step = True
                self.step_buf = []
            elif "idx" in classes and self.in_item_label:
                self.skip_idx = True
            return
        if tag == "br":
            self.buf.append("\n")
            return
        if tag in ("strong", "b"):
            self.buf.append("**")
            return
        if tag in ("em", "i"):
            self.buf.append("*")
            return
        # img 等装饰性标签：忽略

    def handle_endtag(self, tag):
        if tag in ("strong", "b"):
            self.buf.append("**")
            return
        if tag in ("em", "i"):
            self.buf.append("*")
            return
        if tag == "h1":
            if not self.title:
                self.title = "".join(self.buf).strip()
            self.buf = []
            self.kind = None
            return
        if tag in ("h2", "h3", "h4"):
            self._flush()
            return
        if tag == "p":
            if self.in_item and self.in_item_label:
                self.item_label_buf.append("".join(self.buf).strip())
                self.buf = []
                self.in_item_label = False
                return
            if self.in_item and not self.in_item_label:
                txt = "".join(self.buf).strip()
                if txt:
                    self.item_body_buf.append(txt)
                self.buf = []
                return
            self._flush()
            return
        if tag == "blockquote":
            self._flush()
            return
        if tag in ("ul", "ol"):
            self._flush()
            if self.list_items:
                prefix = "1." if self.list_ordered else "-"
                self.blocks.append(
                    ("list", "\n".join(f"{prefix} {it}" for it in self.list_items))
                )
            self.in_list = False
            self.list_items = []
            return
        if tag == "li":
            if self.cur_li is not None and self.cur_li < len(self.list_items):
                self.list_items[self.cur_li] = "".join(self.buf).strip()
            self.buf = []
            self.cur_li = None
            return
        if tag == "div":
            if self.in_item:
                label = "".join(self.item_label_buf).strip()
                body = " ".join(b for b in self.item_body_buf if b).strip()
                if label or body:
                    self.blocks.append(
                        ("item", f"**{label}**：{body}" if label else body)
                    )
                self.in_item = False
                self.in_item_label = False
                self.item_label_buf = []
                self.item_body_buf = []
            elif self.in_ladder:
                if self.ladder_steps:
                    self.blocks.append(("ladder", " → ".join(self.ladder_steps)))
                self.in_ladder = False
                self.ladder_steps = []
                self.buf = []
            elif self.in_formula:
                lines = [l.strip() for l in "".join(self.buf).split("\n") if l.strip()]
                if lines:
                    self.blocks.append(("formula", "\n".join(lines)))
                self.in_formula = False
                self.buf = []
            elif self.in_title_area:
                self.in_title_area = False
            elif self.in_footer:
                self.in_footer = False
            else:
                self._flush()
            return
        if tag in ("style", "script"):
            self.in_style = False
            self.in_script = False
            self.buf = []
            return
        if tag == "span":
            if self.in_info_source:
                self.source_text = "".join(self.buf).strip()
                self.in_info_source = False
                self.buf = []
            elif self.in_step:
                self.ladder_steps.append("".join(self.step_buf).strip())
                self.in_step = False
                self.step_buf = []
            elif self.skip_idx:
                self.skip_idx = False
            return

    def handle_data(self, data):
        if self.skip_idx:
            return
        if self.in_title_area and self.kind == "title":
            self.buf.append(data)
            return
        if self.in_info_source:
            self.buf.append(data)
            return
        if self.in_step:
            self.step_buf.append(data)
            return
        if self.in_style or self.in_script:
            return
        if self.in_item:
            if self.in_item_label:
                self.item_label_buf.append(data)
            else:
                self.item_body_buf.append(data)
            return
        if self.in_title_area or self.in_footer:
            return
        self.buf.append(data)


def html_blocks_to_md(blocks):
    out = []
    for kind, text in blocks:
        if kind == "h2":
            out.append(f"## {text}")
        elif kind == "h3":
            out.append(f"### {text}")
        elif kind == "h4":
            out.append(f"#### {text}")
        elif kind == "quote":
            out.append("> [!quote] " + text.replace("\n", "\n> "))
        elif kind == "note":
            out.append("> [!note] " + text.replace("\n", "\n> "))
        elif kind == "summary":
            out.append("> [!summary] " + text.replace("\n", "\n> "))
        elif kind == "lead":
            out.append(f"*{text}*")
        elif kind == "formula":
            out.append("> [!info]\n" + "\n".join(f"> {l}" for l in text.split("\n")))
        elif kind == "ladder":
            out.append(f"**变现阶梯**：{text}")
        elif kind == "item":
            out.append(f"- {text}")
        elif kind == "list":
            out.append(text)
        elif kind == "divider":
            out.append("---")
        else:
            if text:
                out.append(text)
    return "\n\n".join(out)


def build_note(title, date, atype, ctype, source, body_md, extra_source_line=""):
    src = (source or "").replace('"', "'")
    ctype_tag = f', "{ctype}"' if ctype else ""
    fm = (
        f"---\n"
        f'title: "{title}"\n'
        f"date: {date}\n"
        f"type: {atype}\n"
        f'content_type: "{ctype}"\n'
        f'source: "{src}"\n'
        f"tags: [公众号工作流{ctype_tag}]\n"
        f"---\n\n"
    )
    md = fm + f"# {title}\n\n" + body_md
    if extra_source_line:
        md += f"\n\n> 来源：{extra_source_line}\n"
    return md


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--title")
    ap.add_argument("--date")
    ap.add_argument("--content-type")
    ap.add_argument("--source")
    ap.add_argument("--type")
    args = ap.parse_args()

    path = os.path.abspath(args.input)
    if not os.path.exists(path):
        print(f"ERROR: 输入文件不存在：{path}")
        sys.exit(1)

    os.makedirs(OBS_BASE, exist_ok=True)

    if path.lower().endswith(".json"):
        d = json.load(open(path, encoding="utf-8"))
        title = args.title or d.get("title", "")
        ctype = args.content_type or d.get("content_type", "")
        source = args.source or d.get("source", "")
        date = args.date or datetime.date.today().isoformat()
        atype = args.type or "公众号图文"
        body = blocks_to_md(d.get("blocks", []))
        extra = ""
    else:
        html = open(path, encoding="utf-8").read()
        p = CardParser()
        p.feed(html)
        p._flush()
        title = args.title or p.title or ""
        source = args.source or p.source_text or ""
        date = args.date or datetime.date.today().isoformat()
        ctype = args.content_type or ""
        atype = args.type or "长图（zw-card）"
        body = html_blocks_to_md(p.blocks)
        extra = p.source_text or ""

    if not title:
        title = "未命名文章"

    md = build_note(title, date, atype, ctype, source, body, extra)
    out_name = sanitize_filename(title) + ".md"
    out_path = os.path.join(OBS_BASE, out_name)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"OK -> {out_path}")
    print(f"    title={title!r} type={atype} blocks={len(body.splitlines())} lines")


if __name__ == "__main__":
    main()
