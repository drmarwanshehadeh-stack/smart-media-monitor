#!/usr/bin/env python3
"""Translate UTF-8 text or Markdown reports/studies with Argos Translate.

The source document is never modified. The translated document is written to a
new path. Paragraph boundaries are preserved to keep academic/report structure.

Usage:
    python scripts/translate_document.py report.md report.ar.md --from en --to ar
    python scripts/translate_document.py study.txt study.ar.txt --from fr --to ar
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import argostranslate.package
import argostranslate.translate


def ensure_model(from_code: str, to_code: str) -> None:
    installed = argostranslate.translate.get_installed_languages()
    src = next((x for x in installed if x.code == from_code), None)
    dst = next((x for x in installed if x.code == to_code), None)
    if src and dst:
        try:
            src.get_translation(dst)
            return
        except Exception:
            pass
    argostranslate.package.update_package_index()
    packages = argostranslate.package.get_available_packages()
    package = next((p for p in packages if p.from_code == from_code and p.to_code == to_code), None)
    if package is None:
        raise RuntimeError(f"No Argos model available for {from_code}->{to_code}")
    argostranslate.package.install_from_path(package.download())


def translate_block(block: str, from_code: str, to_code: str) -> str:
    if not block.strip():
        return block
    # Keep fenced code blocks and bare URLs unchanged.
    stripped = block.strip()
    if stripped.startswith("```") or re.fullmatch(r"https?://\S+", stripped):
        return block
    return argostranslate.translate.translate(block, from_code, to_code)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("input_file")
    p.add_argument("output_file")
    p.add_argument("--from", dest="from_code", required=True)
    p.add_argument("--to", dest="to_code", default="ar")
    args = p.parse_args()

    src = Path(args.input_file)
    dst = Path(args.output_file)
    if src.suffix.lower() not in {".txt", ".md", ".markdown"}:
        raise SystemExit("Supported formats in this pilot: .txt, .md, .markdown")

    ensure_model(args.from_code, args.to_code)
    text = src.read_text(encoding="utf-8")
    # Split on blank lines while retaining separators.
    parts = re.split(r"(\n\s*\n)", text)
    translated = []
    for part in parts:
        if re.fullmatch(r"\n\s*\n", part or ""):
            translated.append(part)
        else:
            translated.append(translate_block(part, args.from_code, args.to_code))

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("".join(translated), encoding="utf-8")
    print(f"Translated document {src} -> {dst} ({args.from_code}->{args.to_code})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
