#!/usr/bin/env python3
"""Translate non-Arabic monitoring CSV fields to Arabic with Argos Translate.

Preserves source text and adds translated fields. The source language is read from
`language` by default, so mixed-language monitoring exports are supported.

Usage:
    python scripts/translate_argos.py exports/latest.csv exports/latest_translated.csv
    python scripts/translate_argos.py input.csv output.csv --to ar --limit 100
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import argostranslate.package
import argostranslate.translate

LANG_ALIASES = {
    "arabic": "ar", "ar": "ar",
    "english": "en", "en": "en",
    "french": "fr", "fr": "fr",
    "german": "de", "de": "de",
    "spanish": "es", "es": "es",
    "russian": "ru", "ru": "ru",
    "turkish": "tr", "tr": "tr",
}


def norm_lang(value: str) -> str:
    value = (value or "").strip().lower()
    return LANG_ALIASES.get(value, value[:2] if len(value) >= 2 else value)


def ensure_model(from_code: str, to_code: str) -> None:
    if not from_code or from_code == to_code:
        return
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
    if not text or not from_code or from_code == to_code:
        return text
    return argostranslate.translate.translate(text, from_code, to_code)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv")
    parser.add_argument("output_csv")
    parser.add_argument("--to", dest="to_code", default="ar")
    parser.add_argument("--language-column", default="language")
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()

    src = Path(args.input_csv)
    dst = Path(args.output_csv)
    dst.parent.mkdir(parents=True, exist_ok=True)

    with src.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fields = list(reader.fieldnames or [])

    extras = (
        "translated_title", "translated_summary", "translation_engine",
        "translation_source", "translation_target", "translation_status",
    )
    for extra in extras:
        if extra not in fields:
            fields.append(extra)

    title_key = next((k for k in fields if k.lower() in {"title", "headline"}), None)
    summary_key = next((k for k in fields if k.lower() in {"summary", "description", "excerpt"}), None)

    models_ready: set[tuple[str, str]] = set()
    translated_count = 0
    skipped_count = 0
    failed_count = 0

    for row in rows:
        source_lang = norm_lang(row.get(args.language_column, ""))
        row["translation_source"] = source_lang
        row["translation_target"] = args.to_code

        if source_lang in {"", args.to_code}:
            row["translated_title"] = row.get(title_key, "") if title_key else ""
            row["translated_summary"] = row.get(summary_key, "") if summary_key else ""
            row["translation_engine"] = "none"
            row["translation_status"] = "source_already_target"
            skipped_count += 1
            continue

        if translated_count >= args.limit:
            row["translation_status"] = "limit_skipped"
            skipped_count += 1
            continue

        try:
            pair = (source_lang, args.to_code)
            if pair not in models_ready:
                ensure_model(*pair)
                models_ready.add(pair)
            if title_key:
                row["translated_title"] = translate(row.get(title_key, ""), source_lang, args.to_code)
            if summary_key:
                row["translated_summary"] = translate(row.get(summary_key, ""), source_lang, args.to_code)
            row["translation_engine"] = "Argos Translate"
            row["translation_status"] = "translated"
            translated_count += 1
        except Exception as exc:
            row["translation_engine"] = "Argos Translate"
            row["translation_status"] = f"failed:{type(exc).__name__}"
            failed_count += 1

    with dst.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Translated={translated_count} skipped={skipped_count} failed={failed_count} -> {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
