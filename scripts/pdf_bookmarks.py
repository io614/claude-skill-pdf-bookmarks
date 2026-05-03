#!/usr/bin/env python3
# /// script
# dependencies = ["pymupdf"]
# ///
"""
PDF Bookmark Tool

Commands:
  extract <pdf_path>               Print each page's text with font-size hints
  insert  <pdf_path> <toc_json>    Insert bookmarks from JSON; saves <name>-bookmarked.pdf
  verify  <pdf_path>               Print each bookmark with the first lines of that page

TOC JSON format (array of objects):
  [{"page": 1, "title": "Introduction"}, {"page": 15, "title": "Chapter 1"}, ...]
"""

import sys
import json
import statistics
from pathlib import Path

import fitz  # pymupdf


def median_font_size(doc):
    sizes = []
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            if block["type"] == 0:
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span["text"].strip():
                            sizes.append(span["size"])
    return statistics.median(sizes) if sizes else 12.0


def cmd_extract(pdf_path):
    doc = fitz.open(pdf_path)
    median = median_font_size(doc)
    large_threshold = median * 1.2

    for page_num, page in enumerate(doc, start=1):
        print(f"\n{'='*60}")
        print(f"PAGE {page_num}")
        print(f"{'='*60}")

        blocks = page.get_text("dict")["blocks"]
        body_lines_shown = 0

        for block in blocks:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                spans = line["spans"]
                text = " ".join(s["text"] for s in spans).strip()
                if not text:
                    continue

                max_size = max(s["size"] for s in spans)
                is_bold = any(
                    "Bold" in s.get("font", "") or "bold" in s.get("font", "")
                    for s in spans
                )

                if max_size >= large_threshold:
                    tag = f"[{max_size:.0f}pt"
                    if is_bold:
                        tag += " bold"
                    tag += "]"
                    print(f"  {tag} {text}")
                else:
                    if body_lines_shown < 4:
                        print(f"  {text}")
                        body_lines_shown += 1
                    elif body_lines_shown == 4:
                        print("  ...")
                        body_lines_shown += 1

    doc.close()


def cmd_insert(pdf_path, toc_json_path):
    with open(toc_json_path) as f:
        entries = json.load(f)

    toc = [[e.get("level", 1), e["title"], e["page"]] for e in entries]

    doc = fitz.open(pdf_path)
    doc.set_toc(toc)

    p = Path(pdf_path)
    out_path = str(p.parent / (p.stem + "-bookmarked" + p.suffix))
    doc.save(out_path)
    doc.close()

    print(f"Saved: {out_path}")
    print(f"Inserted {len(toc)} bookmark(s).")
    return out_path


def cmd_verify(pdf_path):
    doc = fitz.open(pdf_path)
    toc = doc.get_toc()

    if not toc:
        print("No bookmarks found in this PDF.")
        doc.close()
        return

    print(f"{len(toc)} bookmark(s) found:\n")
    for level, title, page_num in toc:
        indent = "  " * (level - 1)
        page_obj = doc[page_num - 1]
        lines = [l.strip() for l in page_obj.get_text().split("\n") if l.strip()]
        preview = lines[:3] if lines else ["(no text)"]
        print(f"{indent}[p{page_num}] {title}")
        for line in preview:
            print(f"      | {line[:100]}")
        print()

    doc.close()


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    pdf_path = sys.argv[2]

    if cmd == "extract":
        cmd_extract(pdf_path)
    elif cmd == "insert":
        if len(sys.argv) < 4:
            print("insert requires: <pdf_path> <toc_json>")
            sys.exit(1)
        cmd_insert(pdf_path, sys.argv[3])
    elif cmd == "verify":
        cmd_verify(pdf_path)
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
