#!/usr/bin/env python3
"""Normalize a CSV export and remove obvious duplicate URLs/titles.

Usage:
    python scripts/normalize_export.py input.csv exports/normalized.csv
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

TRACKING_PREFIXES = ("utm_",)
TRACKING_KEYS = {"fbclid", "gclid", "mc_cid", "mc_eid"}


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def canonical_url(url: str) -> str:
    url = clean_text(url)
    if not url:
        return ""
    try:
        p = urlsplit(url)
        params = [
            (k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
            if k.lower() not in TRACKING_KEYS and not k.lower().startswith(TRACKING_PREFIXES)
        ]
        path = p.path.rstrip("/") or "/"
        return urlunsplit((p.scheme.lower(), p.netloc.lower(), path, urlencode(params), ""))
    except Exception:
        return url


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: normalize_export.py input.csv output.csv", file=sys.stderr)
        return 2

    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    dst.parent.mkdir(parents=True, exist_ok=True)

    with src.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    url_keys = [k for k in fieldnames if k.lower() in {"url", "link", "article_url"}]
    title_keys = [k for k in fieldnames if k.lower() in {"title", "headline"}]
    url_key = url_keys[0] if url_keys else None
    title_key = title_keys[0] if title_keys else None

    seen = set()
    out = []
    for row in rows:
        for k, v in list(row.items()):
            row[k] = clean_text(v or "")
        cu = canonical_url(row.get(url_key, "")) if url_key else ""
        title = clean_text(row.get(title_key, "")).casefold() if title_key else ""
        key = cu or title
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        if url_key and cu:
            row[url_key] = cu
        out.append(row)

    with dst.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out)

    print(f"Wrote {len(out)} unique rows to {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
