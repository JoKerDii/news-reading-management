#!/usr/bin/env node
/* ============================================================================
   build.js — regenerates index.html from the markdown in newsletter-sources/.
   Run after adding or updating markdown files:   node build.js

   How it works:
   - Scans every  newsletter-sources/<YYYY-MM>/  folder.
   - For each .md file it strips the leading date prefix (YYYY-MM-DD-) and the
     .md extension to get a "slug" (e.g. 2026-05-31-social-media.md -> social-media).
   - The slug is looked up in SECTION_META below to get the section's title,
     icon, colour, subtitle and display order. Unknown slugs still appear,
     using sensible defaults derived from the file's # H1 / filename.
   - Articles are parsed (## title + source/date/url/tag + summary), capped at 50.
   - Everything is embedded into index.html so it works on a plain double-click.

   To add / rename a section: add or edit an entry in SECTION_META (keyed by slug).
   ============================================================================ */
const fs = require("fs");
const path = require("path");

const ROOT = __dirname;
const SRC_DIR = path.join(ROOT, "newsletter-sources");
const TEMPLATE = path.join(ROOT, "template.html");
const OUT = path.join(ROOT, "index.html");
const MAX_ARTICLES = 50;

// slug -> presentation. `order` controls section order on the page.
const SECTION_META = {
  "email-newsletters-1":     { title:"AI & Tech Newsletters",        icon:"🤖", color:"#2b7de9", sub:"Anthropic · xAI · TechCrunch & more", order:1 },
  "email-newsletters-2":     { title:"Product, Fintech & Crypto",    icon:"🧩", color:"#8a4fff", sub:"Product, fintech & crypto newsletters", order:2 },
  "founder-newsletters":     { title:"Founder Newsletters",          icon:"🚀", color:"#f5a623", sub:"Founder & startup reads", order:3 },
  "substack-selections":     { title:"Substack Selections",          icon:"✍️", color:"#ff7a59", sub:"Curated Substack essays", order:4 },
  "harvard-business-review": { title:"Harvard Business Review",       icon:"🎓", color:"#e5484d", sub:"HBR articles + monthly picks", order:5 },
  "social-media":            { title:"Social Media",                 icon:"👥", color:"#2bb673", sub:"X · LinkedIn · Substack", order:6 },
  "consulting-reports":      { title:"Consulting Reports",           icon:"📊", color:"#0ea5e9", sub:"McKinsey · Bain · PwC & more", order:7 },
  "investment-analysis":     { title:"Investment Analysis",          icon:"💰", color:"#16a085", sub:"App Economy Insights & analysis", order:8 },
  "youtube-videos":          { title:"YouTube Videos",               icon:"▶️", color:"#ff6b6b", sub:"Watch Later playlist", order:9 }
};

const DEFAULT_PALETTE = ["#2b7de9","#8a4fff","#f5a623","#ff7a59","#e5484d","#2bb673","#0ea5e9","#16a085","#ff6b6b","#6366f1"];

function parseMarkdown(md){
  const articles = [];
  const blocks = md.split(/^##\s+/m).slice(1);
  for (const block of blocks){
    const lines = block.split("\n");
    const title = lines.shift().trim();
    const art = { title, source:"", date:"", url:"", tag:"", summary:"" };
    let i = 0;
    for (; i < lines.length; i++){
      const m = lines[i].match(/^(source|date|url|tag):\s*(.*)$/i);
      if (m){ art[m[1].toLowerCase()] = m[2].trim(); }
      else if (lines[i].trim() === "" && i === 0){ continue; }
      else { break; }
    }
    art.summary = lines.slice(i).join("\n").trim();
    if (art.title) articles.push(art);
  }
  return articles.slice(0, MAX_ARTICLES);
}

function slugFromFile(name){
  return name.replace(/\.md$/i, "").replace(/^\d{4}-\d{2}-\d{2}-/, "");
}
function titleFromMarkdown(md, slug){
  const h1 = md.match(/^#\s+(.+)$/m);
  if (h1) return h1[1].trim();
  return slug.replace(/-/g," ").replace(/\b\w/g, c => c.toUpperCase());
}
function monthLabel(value){ // "2026-05" -> "May 2026"
  const [y,m] = value.split("-").map(Number);
  return new Date(y, m-1, 1).toLocaleString("en-US",{month:"long",year:"numeric"});
}

// ---- scan months ----
const monthDirs = fs.readdirSync(SRC_DIR, {withFileTypes:true})
  .filter(d => d.isDirectory() && /^\d{4}-\d{2}$/.test(d.name))
  .map(d => d.name)
  .sort().reverse(); // newest first

const MONTHS = [];
const EMBEDDED = {};
const sourceMap = {}; // id -> {id,title,icon,color,sub,order}
let defaultColorIdx = 0;

for (const month of monthDirs){
  const dir = path.join(SRC_DIR, month);
  const files = fs.readdirSync(dir).filter(f => /\.md$/i.test(f) && f.toLowerCase() !== "format.md");
  const monthData = {};
  const present = [];
  for (const file of files){
    const slug = slugFromFile(file);
    const md = fs.readFileSync(path.join(dir, file), "utf8");
    const articles = parseMarkdown(md);
    if (!articles.length) continue;
    monthData[slug] = articles;
    present.push(slug);
    if (!sourceMap[slug]){
      const meta = SECTION_META[slug] || {};
      sourceMap[slug] = {
        id: slug,
        title: meta.title || titleFromMarkdown(md, slug),
        icon: meta.icon || "📄",
        color: meta.color || DEFAULT_PALETTE[defaultColorIdx++ % DEFAULT_PALETTE.length],
        sub: meta.sub || "",
        order: meta.order != null ? meta.order : 99
      };
    }
  }
  if (present.length){
    EMBEDDED[month] = monthData;
    MONTHS.push({ value: month, label: monthLabel(month), folder: month });
  }
}

const SOURCES = Object.values(sourceMap)
  .sort((a,b) => a.order - b.order || a.title.localeCompare(b.title))
  .map(({order, ...rest}) => rest);

// ---- inject into template ----
let html = fs.readFileSync(TEMPLATE, "utf8");
function inject(marker, value){
  const re = new RegExp("/\\*__"+marker+"__\\*/[\\s\\S]*?/\\*__END__\\*/");
  html = html.replace(re, JSON.stringify(value));
}
inject("MONTHS", MONTHS);
inject("SOURCES", SOURCES);
inject("EMBEDDED", EMBEDDED);

fs.writeFileSync(OUT, html);

// ---- report ----
let total = 0;
console.log("Built index.html");
for (const m of MONTHS){
  const n = Object.values(EMBEDDED[m.value]).reduce((s,a)=>s+a.length,0);
  total += n;
  console.log(`  ${m.label}: ${Object.keys(EMBEDDED[m.value]).length} sources, ${n} articles`);
}
console.log(`  TOTAL: ${total} articles, ${SOURCES.length} sections, ${(html.length/1024).toFixed(1)} KB`);
