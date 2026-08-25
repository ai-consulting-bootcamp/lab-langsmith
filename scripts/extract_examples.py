"""
Step 3: Extract and structure blog-title-generation examples from
fabiochiu/medium-articles into the JSON format used for the LangSmith dataset.

Each example:
  inputs:  {"article_text": <first ~400 words of the article body>}
  outputs: {"title": <the article's real, published title>}
  metadata: {tags, primary_tag, url, full_text_word_count, excerpt_word_count}

Usage:
    python3 scripts/extract_examples.py
Writes: data/blog_title_examples.json
"""

import ast
import json
import re
from collections import defaultdict

from datasets import load_dataset

EXCERPT_WORD_COUNT = 400
MIN_TITLE_LEN = 15
MAX_TITLE_LEN = 100
MIN_TEXT_WORDS = 250
MAX_PER_TAG = 2
TARGET_TOTAL = 18
SCAN_LIMIT = 8000  # how many rows of the (streamed) dataset to scan for candidates

OUTPUT_PATH = "data/blog_title_examples.json"


def clean_title(title: str) -> bool:
    if not title:
        return False
    if len(title) < MIN_TITLE_LEN or len(title) > MAX_TITLE_LEN:
        return False
    if "http" in title.lower():
        return False
    if title.strip().lower() in {"untitled", "untitled story"}:
        return False
    return True


def strip_leading_title(text: str, title: str) -> str:
    """Medium scrapes often repeat the headline (and sometimes a subtitle)
    as the first line(s) of `text`. Strip that so the excerpt doesn't hand
    the model the answer verbatim."""
    title_words = title.split()
    text_words = text.split()
    lookahead = min(len(title_words) + 8, len(text_words))
    window = " ".join(text_words[:lookahead]).lower()

    if title.lower() in window:
        idx = window.index(title.lower())
        char_cut = len(" ".join(text_words[:lookahead])[: idx + len(title)])
        remainder = text[char_cut:].lstrip(" \n\t—-:|")
        return remainder
    return text


def make_excerpt(text: str, title: str, word_count: int) -> str:
    text = strip_leading_title(text, title)
    words = text.split()
    excerpt = " ".join(words[:word_count])
    return excerpt.strip()


def has_title_leakage(excerpt: str, title: str) -> bool:
    title_words = title.lower().split()[:4]
    excerpt_start = " ".join(excerpt.lower().split()[:15])
    return len(title_words) >= 2 and all(w in excerpt_start for w in title_words)


def parse_tags(raw_tags) -> list:
    if isinstance(raw_tags, list):
        return raw_tags
    if isinstance(raw_tags, str):
        try:
            parsed = ast.literal_eval(raw_tags)
            if isinstance(parsed, list):
                return parsed
        except (ValueError, SyntaxError):
            pass
    return []


def main():
    ds = load_dataset("fabiochiu/medium-articles", split="train", streaming=True)

    buckets = defaultdict(list)
    seen_titles = set()
    scanned = 0

    for sample in ds:
        scanned += 1
        if scanned > SCAN_LIMIT:
            break

        title = (sample.get("title") or "").strip()
        text = (sample.get("text") or "").strip()
        tags = parse_tags(sample.get("tags"))

        if not clean_title(title):
            continue
        if title in seen_titles:
            continue
        word_count = len(text.split())
        if word_count < MIN_TEXT_WORDS:
            continue
        if not tags:
            continue

        primary_tag = tags[0]
        if len(buckets[primary_tag]) >= MAX_PER_TAG:
            continue

        excerpt = make_excerpt(text, title, EXCERPT_WORD_COUNT)

        # Guard against title leakage into the excerpt (Medium scrapes often
        # repeat the headline at the very start of the body text) and against
        # excerpts that got too short after stripping the leading title/subtitle.
        if has_title_leakage(excerpt, title):
            continue
        if len(excerpt.split()) < MIN_TEXT_WORDS:
            continue

        buckets[primary_tag].append({
            "inputs": {"article_text": excerpt},
            "outputs": {"title": title},
            "metadata": {
                "tags": tags,
                "primary_tag": primary_tag,
                "url": sample.get("url", ""),
                "full_text_word_count": word_count,
                "excerpt_word_count": len(excerpt.split()),
            },
        })
        seen_titles.add(title)

        total = sum(len(v) for v in buckets.values())
        if total >= TARGET_TOTAL and len(buckets) >= TARGET_TOTAL // MAX_PER_TAG:
            break

    examples = [ex for bucket in buckets.values() for ex in bucket][:TARGET_TOTAL]

    with open(OUTPUT_PATH, "w") as f:
        json.dump(examples, f, indent=2)

    print(f"Scanned {scanned} rows, found {len(examples)} examples across {len(buckets)} tags")
    tag_counts = {tag: len(v) for tag, v in buckets.items()}
    print("Tag distribution:", tag_counts)
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
