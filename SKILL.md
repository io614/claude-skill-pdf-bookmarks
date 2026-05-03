---
name: pdf-bookmarks
description: Insert chapter bookmarks into a PDF that has none. Detects chapters by reading the extracted text and using judgment — handles non-uniform formatting.
argument-hint: "<pdf-file-path>"
allowed-tools: Bash Write Read
---

Insert chapter bookmarks into: **$ARGUMENTS**

## Steps

### 1. Extract page content

```bash
uv run --with pymupdf ${CLAUDE_SKILL_DIR}/scripts/pdf_bookmarks.py extract "$ARGUMENTS"
```

Read the output carefully. Each page shows its text; lines prefixed with `[Npt]` or `[Npt bold]` have a font size at least 20% larger than the document's body text — these are visually prominent and likely headings.

### 2. Identify chapters using judgment

Do NOT rely on rigid rules. Instead:
- Read the text and consider what a reader would call a "chapter" or top-level section
- Look for structural cues: numbering, prominent titles, large/bold font tags, page breaks before new topics
- Ignore running headers, footers, page numbers, and captions
- If the PDF appears to be scanned or has no large-font cues, look for textual patterns (e.g. "Chapter 1", "Part II", numbered headings)
- If uncertain between two candidates on the same page, pick the one that best names the section

### 3. Write the TOC JSON

Write a file `/tmp/toc_bookmarks.json` with the identified chapters. Use the optional `"level"` field (default: 1) for nested bookmarks — level 1 is a top-level entry, level 2 is a sub-entry, and so on:

```json
[
  {"page": 1, "title": "Introduction", "level": 1},
  {"page": 15, "title": "Part I: Foundations", "level": 1},
  {"page": 17, "title": "Chapter 1: Getting Started", "level": 2},
  {"page": 30, "title": "Chapter 2: Core Concepts", "level": 2}
]
```

If the document has only top-level chapters with no sub-sections, omit `"level"` (or set it to 1 for all entries).

Show the proposed TOC to the user and ask for confirmation before inserting.

### 4. Insert bookmarks

Once confirmed:

```bash
uv run --with pymupdf ${CLAUDE_SKILL_DIR}/scripts/pdf_bookmarks.py insert "$ARGUMENTS" /tmp/toc_bookmarks.json
```

### 5. Verify

```bash
uv run --with pymupdf ${CLAUDE_SKILL_DIR}/scripts/pdf_bookmarks.py verify "<output-pdf-path>"
```

The output shows the first few lines of each bookmarked page. Review with the user to confirm every bookmark landed on the correct page.

Report the output file path when done.
