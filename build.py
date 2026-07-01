#!/usr/bin/env python3
import json
import os
import re
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "newsletter-sources"
TEMPLATE = ROOT / "template.html"
OUT = ROOT / "index.html"
MAX_ARTICLES = 1000

SECTION_META = {
    "email-newsletters-1": {"title": "AI & Tech Newsletters", "icon": "🤖", "color": "#2b7de9", "sub": "Anthropic · xAI · TechCrunch & more", "order": 1},
    "email-newsletters-2": {"title": "Product, Fintech & Crypto", "icon": "🧩", "color": "#8a4fff", "sub": "Product, fintech & crypto newsletters", "order": 2},
    "founder-newsletters": {"title": "Founder Newsletters", "icon": "🚀", "color": "#f5a623", "sub": "Founder & startup reads", "order": 3},
    "substack-selections": {"title": "Substack Selections", "icon": "✍️", "color": "#ff7a59", "sub": "Curated Substack essays", "order": 4},
    "harvard-business-review": {"title": "Harvard Business Review", "icon": "🎓", "color": "#e5484d", "sub": "HBR articles + monthly picks", "order": 5},
    "social-media": {"title": "Social Media", "icon": "👥", "color": "#2bb673", "sub": "X · LinkedIn · Substack", "order": 6},
    "consulting-reports": {"title": "Consulting Reports", "icon": "📊", "color": "#0ea5e9", "sub": "McKinsey · Bain · PwC & more", "order": 7},
    "investment-analysis": {"title": "Investment Analysis", "icon": "💰", "color": "#16a085", "sub": "App Economy Insights & analysis", "order": 8},
    "youtube-videos": {"title": "YouTube Videos", "icon": "▶️", "color": "#ff6b6b", "sub": "Watch Later playlist", "order": 9},
}

DEFAULT_PALETTE = ["#2b7de9", "#8a4fff", "#f5a623", "#ff7a59", "#e5484d", "#2bb673", "#0ea5e9", "#16a085", "#ff6b6b", "#6366f1"]


def parse_markdown(md: str):
    raw = md.replace("\r\n", "\n")
    articles = []

    old_blocks = re.split(r"^##\s+", raw, flags=re.M)[1:]
    if old_blocks and re.search(r"(^|\n)(source|date|url|tag):\s*", raw, flags=re.I):
        for block in old_blocks:
            lines = block.split("\n")
            title = lines[0].strip() if lines else ""
            art = {"title": title, "source": "", "date": "", "url": "", "tag": "", "summary": ""}
            i = 0
            for i in range(len(lines)):
                m = re.match(r"^(source|date|url|tag):\s*(.*)$", lines[i], flags=re.I)
                if m:
                    art[m.group(1).lower()] = m.group(2).strip()
                elif lines[i].strip() == "" and i == 0:
                    continue
                else:
                    break
            art["summary"] = "\n".join(lines[i:]).strip()
            if art["title"]:
                articles.append(art)
        return articles[:MAX_ARTICLES]

    section_title = re.search(r"^#\s+(.+)$", raw, flags=re.M)
    section_title = section_title.group(1).strip() if section_title else ""
    blocks = re.split(r"^###\s+\d+\.\s+", raw, flags=re.M)[1:]
    for block in blocks:
        lines = [line.rstrip() for line in block.split("\n")]
        first = lines[0] if lines else ""
        title_match = re.match(r"^\[(.+?)\]\((https?:\/\/[^)\s]+)\)", first)
        title = title_match.group(1).strip() if title_match else re.sub(r"\s+", " ", first).strip()
        url = title_match.group(2).strip() if title_match else ""
        art = {"title": title, "source": "", "date": "", "url": url, "tag": "", "summary": ""}

        published_line = next((line for line in lines if re.match(r"^\*\*Published:\*\*", line, flags=re.I)), None)
        if published_line:
            m = re.match(r"^\*\*Published:\*\*\s*(.+?)(?:\s*\|\s*\*\*By:\*\*\s*(.+))?$", published_line, flags=re.I)
            if m:
                art["date"] = m.group(1).strip()
                if m.group(2):
                    art["source"] = m.group(2).strip()

        by_line = next((line for line in lines if re.match(r"^\*\*By:\*\*", line, flags=re.I)), None)
        if not art["source"] and by_line:
            art["source"] = by_line.replace("**By:**", "", 1).strip()
        if not art["source"]:
            art["source"] = section_title

        summary_index = next((i for i, line in enumerate(lines) if re.match(r"^\*\*Summary:\*\*", line, flags=re.I)), None)
        if summary_index is not None:
            summary_text = re.sub(r"^\*\*Summary:\*\*\s*", "", lines[summary_index], flags=re.I).strip()
            if summary_text:
                art["summary"] = summary_text
            else:
                art["summary"] = "\n".join(lines[summary_index + 1:]).strip()
        else:
            art["summary"] = "\n".join(lines[1:]).strip()

        if art["title"]:
            articles.append(art)
    return articles[:MAX_ARTICLES]


def slug_from_file(name: str):
    return re.sub(r"\.md$", "", name).replace(r"^\d{4}-\d{2}-\d{2}-", "", 1) if False else name.replace(".md", "").replace("^", "")


def slug_from_file(name: str):
    name = name.replace(".md", "")
    return re.sub(r"^\d{4}-\d{2}-\d{2}-", "", name)


def month_label(value: str):
    year, month = map(int, value.split("-"))
    return datetime(year, month, 1).strftime("%b %Y")


month_dirs = sorted(
    [d.name for d in SRC_DIR.iterdir() if d.is_dir() and re.match(r"^\d{4}-\d{2}$", d.name)],
    reverse=True,
)

MONTHS = []
EMBEDDED = {}
source_map = {}
default_color_idx = 0

for month in month_dirs:
    month_dir = SRC_DIR / month
    files = sorted([f.name for f in month_dir.iterdir() if f.is_file() and f.suffix.lower() == ".md" and f.name.lower() != "format.md"])
    month_data = {}
    present = []
    for file_name in files:
        slug = slug_from_file(file_name)
        md = (month_dir / file_name).read_text(encoding="utf-8")
        articles = parse_markdown(md)
        if not articles:
            continue
        month_data[slug] = articles
        present.append(slug)
        if slug not in source_map:
            meta = SECTION_META.get(slug, {})
            source_map[slug] = {
                "id": slug,
                "title": meta.get("title") or re.sub(r"-", " ", slug).title(),
                "icon": meta.get("icon") or "📄",
                "color": meta.get("color") or DEFAULT_PALETTE[default_color_idx % len(DEFAULT_PALETTE)],
                "sub": meta.get("sub") or "",
                "order": meta.get("order", 99),
            }
            default_color_idx += 1
    if present:
        EMBEDDED[month] = month_data
        MONTHS.append({"value": month, "label": month_label(month), "folder": month})

SOURCES = [
    {k: v for k, v in item.items() if k != "order"}
    for item in sorted(source_map.values(), key=lambda x: (x["order"], x["title"].lower()))
]

html = TEMPLATE.read_text(encoding="utf-8")

def inject(marker, value):
    pattern = re.compile(rf"/\*__{marker}__\*/[\s\S]*?/\*__END__\*/")
    replacement = json.dumps(value, ensure_ascii=False)
    return pattern.sub(lambda match: replacement, html, count=1)

html = inject("MONTHS", MONTHS)
html = inject("SOURCES", SOURCES)
html = inject("EMBEDDED", EMBEDDED)

OUT.write_text(html, encoding="utf-8")

print("Built index.html")
for m in MONTHS:
    n = sum(len(v) for v in EMBEDDED[m["value"]].values())
    print(f"  {m['label']}: {len(EMBEDDED[m['value']])} sources, {n} articles")
print(f"  TOTAL: {sum(sum(len(v) for v in EMBEDDED[m['value']].values()) for m in MONTHS)} articles, {len(SOURCES)} sections")
