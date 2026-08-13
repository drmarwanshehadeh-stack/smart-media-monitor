#!/usr/bin/env python3
"""Translate monitoring CSV fields to Arabic with Argos Translate.

Preserves source text and adds translated_title / translated_summary fields.
Usage:
    python scripts/translate_argos.py input.csv output.csv --from en --to ar
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import argostranslate.package
import argostranslate.translate


def ensure_model(from_code: str, to_code: str) -> None:
    installed = argostranslate.translate.get_installed_languages()
    from_lang = next((x for x in installed if x.code == from_code), None)
    to_lang = next((x for x in installed if x.code == to_code), None)
    if from_lang and to_lang:
        try:
            from_lang.get_translation(to_lang)
            return
        except Exception:
            pass

    argostranslate.package.update_package_index()
    packages = argostranslate.package.get_available_packages()
    package = next((p for p in packages if p.from_code == from_code and p.to_code == to_code), None)
    if package is None:
        raise RuntimeError(f"No Argos model available for {from_code}->{to_code}")
    argostranslate.package.install_from_path(package.download())


def translate(text: str, from_code: str, to_code: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    return argostranslate.translate.translate(text, from_code, to_code)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv")
    parser.add_argument("output_csv")
    parser.add_argument("--from", dest="from_code", required=True)
    parser.add_argument("--to", dest="to_code", default="ar")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    ensure_model(args.from_code, args.to_code)

    src = Path(args.input_csv)
    dst = Path(args.output_csv)
    dst.parent.mkdir(parents=True, exist_ok=True)

    with src.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fields = list(reader.fieldnames or [])

    for extra in ("translated_title", "translated_summary", "translation_engine", "translation_target"):
        if extra not in fields:
            fields.append(extra)

    title_key = next((k for k in fields if k.lower() in {"title", "headline"}), None)
    summary_key = next((k for k in fields if k.lower() in {"summary", "description", "excerpt"}), None)

    translated_count = 0
    for row in rows:
        if translated_count >= args.limit:
            break
        if title_key:
            row["translated_title"] = translate(row.get(title_key, ""), args.from_code, args.to_code)
        if summary_key:
            row["translated_summary"] = translate(row.get(summary_key, ""), args.from_code, args.to_code)
        row["translation_engine"] = "Argos Translate"
        row["translation_target"] = args.to_code
        translated_count += 1

    with dst.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Translated {translated_count} rows to {args.to_code} -> {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
