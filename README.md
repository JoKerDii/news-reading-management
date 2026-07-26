# Newsletter Site Architecture and Development Guide

This document explains how this project is structured, how the website is generated, how content is stored, and how to rebuild or extend it.

## 1. Project Purpose

This project builds a static newsletter archive website that displays curated content from monthly markdown files. The site is designed to:

- collect newsletter-style content from source markdown files
- organize content into monthly archives
- render a polished web page with sections, filters, and article cards
- work without a backend or database
- be rebuilt locally from source files into a single static HTML file

The final output is a single file named index.html that can be opened directly in a browser.

---

## 2. Repository Structure

At the top level, the project contains:

- index.html
  - The generated static website.
  - This is the file a browser opens.
  - It is produced by the build pipeline from the template and source markdown data.

- template.html
  - The HTML shell and JavaScript structure used as the base for the final page.
  - It contains the page layout, styles, and client-side rendering logic.
  - It includes placeholder markers that are replaced by build data.

- build.js
  - A Node.js build script.
  - Reads the markdown source data and generates index.html.
  - This is the canonical build script for the project.

- build.py
  - A Python fallback/build helper.
  - It performs the same job as build.js when Node is unavailable.
  - This was added to support environments where node is not installed.

- newsletter-sources/
  - Root directory for all source content.
  - Contains one subfolder per month, such as 2026-05 or 2026-06.
  - Each monthly folder contains one markdown file per content source category.

- newsletter-sources/FORMAT.md
  - Explains the expected markdown format for each article source file.
  - Useful for maintaining consistency when adding new content.

Example layout:

```text
news-management/
├── index.html
├── template.html
├── build.js
├── build.py
├── README.md
└── newsletter-sources/
    ├── FORMAT.md
    ├── 2026-05/
    │   ├── 2026-05-30-investment-analysis.md
    │   ├── 2026-05-30-youtube-videos.md
    │   └── ...
    └── 2026-06/
        ├── 2026-06-30-consulting-reports.md
        ├── 2026-06-30-email-newsletters-1.md
        └── ...
```

---

## 3. How Content Is Stored

### 3.1 Monthly folders

Every month is represented by a directory under newsletter-sources/ with a name matching the pattern YYYY-MM.

Examples:

- newsletter-sources/2026-05/
- newsletter-sources/2026-06/

Each folder contains one markdown file per source category.

### 3.2 File naming convention

Files follow this pattern:

```text
YYYY-MM-DD-slug.md
```

For example:

- 2026-06-30-harvard-business-review.md
- 2026-06-30-email-newsletters-1.md
- 2026-06-30-investment-analysis.md

The date prefix is used to identify the month and the slug represents the content section.

### 3.3 Markdown content format

Each source file is a markdown document containing:

- a top-level H1 heading that defines the section title
- optional introductory text or metadata
- one or more article entries introduced by a level-3 heading
- each article entry includes:
  - title
  - source
  - date
  - url
  - summary

The parser expects article entries in the following general structure:

```md
# Section Title

Some intro text.

### 1. [Article Title](https://example.com/article)

**Published:** 2026-06-30 | **By:** Author Name

**Summary:** A concise summary of the article.
```

The build script extracts the title, source, date, URL, and summary fields from the markdown content.

---

## 4. How the Website Is Designed

### 4.1 Design goals

The site is designed to feel like a polished editorial dashboard:

- clean, modern cards for individual articles
- a sectioned layout for different content categories
- top-level controls for month selection and keyword search
- visually distinct sections with icons and colors
- responsive behavior that works on a desktop browser

### 4.2 Visual structure

The page includes:

- a header with the site title and controls
- a top navigation bar for content sections
- a main content area with grouped article cards
- a footer with static branding labels

### 4.3 Styling conventions

The design uses CSS variables for a consistent theme.

Core style values include:

- background color
- panel color
- text color
- muted text color
- border color
- accent color
- border radius

The page uses a light editorial design with white cards, subtle shadows, rounded corners, and colored section accents.

---

## 5. How the Website Is Built

### 5.1 The build workflow

The website is generated from markdown files into a single static HTML file.

The general pipeline is:

1. Scan the monthly folders under newsletter-sources/
2. Read each markdown file
3. Parse each article entry into structured data
4. Group articles by section/slug
5. Build the month list from discovered folders
6. Inject the generated data into template.html
7. Write the final result to index.html

### 5.2 The template system

The file template.html is the page shell.

It contains:

- the full HTML document structure
- CSS styling
- the content container elements
- JavaScript that renders the cards and sections dynamically

It includes placeholders that are replaced by the build script with JSON-encoded content data.

The build script identifies markers like:

- MONTHS
- SOURCES
- EMBEDDED

and injects the generated content into the page script.

### 5.3 The generated data structure

The generated site uses three main constants in the browser script:

- MONTHS
  - list of available months
  - each entry includes value, label, and folder

- SOURCES
  - list of section definitions
  - each entry includes id, title, icon, color, sub

- EMBEDDED
  - nested object of month -> section -> article list
  - this is the core content dataset used by the page at runtime

### 5.4 Client-side rendering

Once index.html is loaded in the browser, JavaScript:

- reads the embedded dataset
- populates the month dropdown
- renders section tabs
- renders article cards for the currently selected month
- supports search filtering

No server-side rendering is required.

---

## 6. The Build Scripts

### 6.1 build.js

build.js is the primary build script.

It:

- scans newsletter-sources/
- discovers monthly folders
- reads markdown files
- parses the content
- builds the embedded data object
- writes index.html

To run it:

```bash
node build.js
```

### 6.2 build.py

build.py is a Python fallback implementation.

It performs the same core logic as build.js and is useful when Node is not installed.

To run it:

```bash
python3 build.py
```

### 6.3 Important note

If content files change, index.html should be regenerated using one of the build scripts. The generated HTML is not meant to be edited by hand.

---

## 7. Parsing Logic

The build scripts parse markdown content into structured article objects.

### 7.1 Supported article format

The parser expects articles to have:

- a title
- a published date
- a source/author line
- a URL
- a summary

The parser uses regular expressions and markdown structure to identify these values.

### 7.2 Summary handling

The parser captures the summary from the markdown text following the summary marker. This is important because the website displays the summary under each card.

If the summary text is missing or formatted oddly, the card may show little or no summary text, so content authors should follow the format carefully.

### 7.3 Section mapping

Each markdown file maps to a section identifier based on the filename slug.

For example:

- 2026-06-30-investment-analysis.md -> investment-analysis
- 2026-06-30-harvard-business-review.md -> harvard-business-review

These IDs are used in the generated website to group content into visual sections.

---

## 8. How to Add or Update Content

### 8.1 Add a new month

To add a new month:

1. create a new folder under newsletter-sources/ named YYYY-MM
2. add one or more markdown files using the expected format
3. run the build script
4. refresh the generated site

### 8.2 Add a new section file

To add a new section file:

1. create a new markdown file in the appropriate month folder
2. use a slug that matches the intended section id
3. ensure the article entries follow the expected format
4. rebuild the site

### 8.3 Update existing content

To update existing content:

1. edit the relevant markdown file
2. rebuild the site
3. check the generated page in the browser

### 8.4 Content format tips

When authoring new markdown files:

- keep the H1 title concise and clear
- use level-3 headings for each article
- include a source/date/url/tag/summary structure where possible
- ensure summaries are written as real prose rather than just separators or placeholders
- keep URLs valid

---

## 9. How the UI Works

### 9.1 Month selection

The dropdown at the top of the page lets users switch between available months. The list comes from the folders discovered in newsletter-sources/.

### 9.2 Search filter

The search box filters article cards across the current month.

It searches the title, summary, source, and tag fields.

### 9.3 Section tabs

Each section tab links to a section on the page. It shows the number of visible articles for that section.

### 9.4 Article cards

Each card displays:

- title
- source
- date
- summary
- optional tag

The title is clickable and opens the article URL in a new tab if a URL exists.

---

## 10. Known Implementation Notes

### 10.1 Static-only architecture

This project intentionally uses no backend or database. It is a static site generated from local markdown files.

### 10.2 Browser-side rendering

Rendering is done in JavaScript inside the final HTML file. The build step embeds data into the browser script so the whole thing works as a standalone static page.

### 10.3 Output is generated

The generated page index.html should be treated as build output, not as source of truth. The markdown files and templates are the source of truth.

### 10.4 The site is local-first

The project is designed to be simple to run locally. No package installation is required if the build scripts already run in the environment.

---

## 11. Troubleshooting

### 11.1 Page shows nothing

If the page appears blank or empty:

- ensure index.html was rebuilt
- confirm the build script completed without errors
- make sure the injected constants are present in the generated script
- check the browser console for JavaScript errors

### 11.2 Missing summaries

If summaries are missing:

- review the markdown formatting for the article
- ensure the summary marker uses the expected format
- re-run the build script

### 11.3 A month is missing from the dropdown

If a month does not appear:

- verify the folder name matches YYYY-MM
- ensure the folder contains at least one markdown file with parseable content
- rebuild the site

### 11.4 A section is missing from the page

If a section is not displayed:

- verify the source file slug maps to a known section
- ensure the file contains at least one article entry with a title
- rebuild the site

---

## 12. Recommended Development Workflow

When making changes, use the following workflow:

1. Edit or add markdown content in newsletter-sources/
2. If needed, update template.html or the build logic in build.js/build.py
3. Rebuild the site with the appropriate script
4. Open index.html in a browser
5. Verify the month dropdown, sections, cards, and summaries

---

## 13. Summary

This project is a static newsletter archive site built from monthly markdown files.

The essential flow is:

- markdown source files live in newsletter-sources/
- build scripts parse those files into structured article data
- template.html provides the page shell and JavaScript rendering logic
- the build outputs index.html as a standalone static website

Any future developer or AI agent should be able to recreate or extend the site by following the file structure, markdown conventions, and build steps described in this document.
