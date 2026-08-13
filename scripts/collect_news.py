#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

import feedparser
import requests
import yaml
from bs4 import BeautifulSoup

UA = "SmartMediaMonitor/0.1 (+research pilot)"
TIMEOUT = 20
MAX_ITEMS_PER_SOURCE = 25


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def canonical_url(url: str) -> str:
    try:
        p = urlsplit(url)
        path = p.path.rstrip("/") or "/"
        return urlunsplit((p.scheme.lower(), p.netloc.lower(), path, "", ""))
    except Exception:
        return url


def item_id(source_id: str, url: str, title: str) -> str:
    raw = f"{source_id}|{canonical_url(url)}|{clean_text(title).casefold()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def fetch_rss(source: dict) -> list[dict]:
    resp = requests.get(source["url"], headers={"User-Agent": UA}, timeout=TIMEOUT)
    resp.raise_for_status()
    parsed = feedparser.parse(resp.content)
    items = []
    for e in parsed.entries[:MAX_ITEMS_PER_SOURCE]:
        title = clean_text(getattr(e, "title", ""))
        link = clean_text(getattr(e, "link", ""))
        if not title or not link:
            continue
        items.append({"title": title, "url": link, "published": clean_text(getattr(e, "published", ""))})
    return items


def fetch_html(source: dict) -> list[dict]:
    resp = requests.get(source["url"], headers={"User-Agent": UA}, timeout=TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    base_host = urlsplit(source["url"]).netloc.lower().removeprefix("www.")
    candidates = []
    seen = set()

    for a in soup.find_all("a", href=True):
        title = clean_text(a.get_text(" ", strip=True))
        if len(title) < 20 or len(title) > 220:
            continue
        href = urljoin(source["url"], a["href"])
        p = urlsplit(href)
        host = p.netloc.lower().removeprefix("www.")
        if p.scheme not in {"http", "https"} or not host:
            continue
        if host != base_host and not host.endswith("." + base_host):
            continue
        url = canonical_url(href)
        key = (title.casefold(), url)
        if key in seen:
            continue
        seen.add(key)
        score = 0
        path = p.path.lower()
        if any(k in path for k in ("news", "article", "story", "details", "post", "2026")):
            score += 2
        if len(title) >= 35:
            score += 1
        candidates.append((score, title, url))

    candidates.sort(key=lambda x: (-x[0], x[1]))
    return [{"title": t, "url": u, "published": ""} for _, t, u in candidates[:MAX_ITEMS_PER_SOURCE]]


def main() -> int:
    config_path = Path(sys.argv[1] if len(sys.argv) > 1 else "config/sources.yml")
    out_dir = Path(sys.argv[2] if len(sys.argv) > 2 else "exports")
    out_dir.mkdir(parents=True, exist_ok=True)

    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    sources = [s for s in config.get("sources", []) if s.get("enabled", False)]
    collected_at = datetime.now(timezone.utc).isoformat()

    rows = []
    status = []
    global_seen = set()

    for source in sources:
        try:
            mode = source.get("mode", "html")
            items = fetch_rss(source) if mode == "rss" else fetch_html(source)
            kept = 0
            for item in items:
                cu = canonical_url(item["url"])
                dedup_key = (clean_text(item["title"]).casefold(), cu)
                if dedup_key in global_seen:
                    continue
                global_seen.add(dedup_key)
                rows.append({
                    "item_id": item_id(source["id"], cu, item["title"]),
                    "source_id": source["id"],
                    "source_name": source["name"],
                    "country": source.get("country", ""),
                    "language": source.get("language", ""),
                    "mode": mode,
                    "title": clean_text(item["title"]),
                    "url": cu,
                    "published": item.get("published", ""),
                    "collected_at_utc": collected_at,
                })
                kept += 1
            status.append({"source_id": source["id"], "ok": True, "items": kept, "error": ""})
        except Exception as exc:
            status.append({"source_id": source.get("id", "unknown"), "ok": False, "items": 0, "error": str(exc)[:300]})

    csv_path = out_dir / "latest.csv"
    json_path = out_dir / "latest.json"
    status_path = out_dir / "status.json"

    fields = ["item_id", "source_id", "source_name", "country", "language", "mode", "title", "url", "published", "collected_at_utc"]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Collected {len(rows)} unique items from {len(sources)} enabled sources")
    for s in status:
        print(f"- {s['source_id']}: {'OK' if s['ok'] else 'FAIL'} ({s['items']}) {s['error']}")
    return 0 if rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
