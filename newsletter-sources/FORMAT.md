# Newsletter Source Format

This file defines the markdown format the website expects. Upload it once; it
guides all 7 monthly markdown files. The website parses these files
automatically — you never edit HTML to publish a new month.

## Folder & file layout

```
newsletter-sources/
├── FORMAT.md
└── 2026-05/
    ├── 2026-05-01-email-letters.md
    ├── 2026-05-01-harvard-business-review.md
    ├── 2026-05-01-social-media.md
    ├── 2026-05-01-consulting-reports.md
    ├── 2026-05-01-tech-newsletters.md
    ├── 2026-05-01-investment-analysis.md
    └── 2026-05-01-youtube-videos.md
```

Each month is its own folder named `YYYY-MM`. The 7 filenames stay the same
every month, only the date prefix changes.

## Article format

Each file holds **up to 50 articles**. One article = one `##` heading,
followed by optional metadata lines (`key: value`), then the summary text.

```markdown
# Email Letters        <!-- optional H1, ignored by the site -->

## Article title goes here
source: TLDR AI
date: 2026-05-28
url: https://example.com/article
tag: AI

One or two sentences summarising the article. Plain text or simple markdown.

## Next article title
source: AlphaSignal
date: 2026-05-25
tag: Tools

Summary for the next article.
```

### Rules
- `##` starts a new article. Its text becomes the card title.
- Metadata lines come immediately after the `##` line, one `key: value` per line.
  Recognised keys: `source`, `date`, `url`, `tag`. All optional.
- Everything after the metadata block (until the next `##`) is the summary.
- If `url` is set, the card title links to it.
- Order in the file = order on the page. Put the most important first.
- Max 50 articles per file; extras beyond 50 are ignored.

## Publishing a new month
1. Create a new `YYYY-MM/` folder with the 7 files (same names, new date prefix).
2. Add the month to the `MONTHS` list at the top of `index.html` (one line).
3. Commit. The site picks it up — no other code changes.
