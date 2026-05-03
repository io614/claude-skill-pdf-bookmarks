# pdf-bookmarks — Claude Code Skill

A [Claude Code skill](https://docs.anthropic.com/en/docs/claude-code/skills) that inserts chapter bookmarks into a PDF that has none.

Claude reads the extracted text, identifies chapters using judgment (handles non-uniform formatting), proposes a table of contents, and inserts the bookmarks after your confirmation.

## Install

```bash
mkdir -p ~/.claude/skills/pdf-bookmarks
curl -fsSL https://raw.githubusercontent.com/io614/claude-skill-pdf-bookmarks/main/SKILL.md \
  -o ~/.claude/skills/pdf-bookmarks/SKILL.md
mkdir -p ~/.claude/skills/pdf-bookmarks/scripts
curl -fsSL https://raw.githubusercontent.com/io614/claude-skill-pdf-bookmarks/main/scripts/pdf_bookmarks.py \
  -o ~/.claude/skills/pdf-bookmarks/scripts/pdf_bookmarks.py
```

Requires [uv](https://github.com/astral-sh/uv) (`pymupdf` is fetched automatically on first run).

## Usage

```
/pdf-bookmarks path/to/your.pdf
```

Claude will:
1. Extract each page's text with font-size hints (large/bold lines flagged as likely headings)
2. Identify chapters using judgment — no rigid rules
3. Show you the proposed table of contents and ask for confirmation
4. Insert the bookmarks, saving `your-bookmarked.pdf` alongside the original
5. Verify each bookmark landed on the correct page

## Nested bookmarks

The proposed TOC supports levels. Claude will use these automatically when the document has parts, chapters, and sections:

```json
[
  {"page": 1,  "title": "Introduction",            "level": 1},
  {"page": 15, "title": "Part I: Foundations",     "level": 1},
  {"page": 17, "title": "Chapter 1: Getting Started", "level": 2},
  {"page": 30, "title": "Chapter 2: Core Concepts",   "level": 2}
]
```

## License

MIT
