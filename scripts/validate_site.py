#!/usr/bin/env python3
"""Validate local links and critical static-site metadata."""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_HTML = [ROOT / "index.html", ROOT / "resume.html", ROOT / "404.html", ROOT / "blog" / "index.html"]
PUBLIC_HTML += sorted((ROOT / "blog" / "posts").glob("*.html"))


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.refs: list[tuple[str, str]] = []
        self.meta: list[dict[str, str]] = []
        self.h1_count = 0
        self.images_without_alt = 0
        self.external_blank_without_rel = 0
        self.lang: str | None = None
        self._json_depth = 0
        self._json_buffer: list[str] = []
        self.json_ld: list[str] = []

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {key: value or "" for key, value in attrs_list}
        if tag == "html":
            self.lang = attrs.get("lang")
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "h1":
            self.h1_count += 1
        if tag == "meta":
            self.meta.append(attrs)
        if tag == "img" and "alt" not in attrs:
            self.images_without_alt += 1
        if tag == "a" and attrs.get("target") == "_blank":
            rel = set(attrs.get("rel", "").split())
            if not {"noopener", "noreferrer"}.issubset(rel):
                self.external_blank_without_rel += 1
        for attr in ("href", "src"):
            if attr in attrs:
                self.refs.append((attr, attrs[attr]))
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self._json_depth += 1
            self._json_buffer = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._json_depth:
            self._json_depth -= 1
            self.json_ld.append("".join(self._json_buffer).strip())
            self._json_buffer = []

    def handle_data(self, data: str) -> None:
        if self._json_depth:
            self._json_buffer.append(data)


def local_target(source: Path, value: str) -> tuple[Path, str] | None:
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or value.startswith(("mailto:", "tel:", "data:")):
        return None
    raw_path = unquote(parsed.path)
    if not raw_path:
        target = source
    elif raw_path.startswith("/"):
        target = ROOT / raw_path.lstrip("/")
    else:
        target = source.parent / raw_path
    if raw_path.endswith("/") or target.is_dir():
        target /= "index.html"
    return target.resolve(), unquote(parsed.fragment)


def parse_page(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def main() -> int:
    errors: list[str] = []
    parsed_pages = {path.resolve(): parse_page(path) for path in PUBLIC_HTML}

    for path, parser in parsed_pages.items():
        rel = path.relative_to(ROOT)
        if not parser.lang:
            errors.append(f"{rel}: missing html lang")
        if parser.h1_count != 1:
            errors.append(f"{rel}: expected one h1, found {parser.h1_count}")
        if parser.images_without_alt:
            errors.append(f"{rel}: {parser.images_without_alt} image(s) missing alt")
        if parser.external_blank_without_rel:
            errors.append(f"{rel}: target=_blank link missing noopener/noreferrer")
        if len(parser.ids) != len(set(parser.ids)):
            errors.append(f"{rel}: duplicate id")

        descriptions = [m for m in parser.meta if m.get("name") == "description"]
        if len(descriptions) != 1:
            errors.append(f"{rel}: expected one meta description")
        if rel.as_posix() != "404.html":
            # Canonical URLs are also seen as hrefs; require exactly one canonical element textually.
            if path.read_text(encoding="utf-8").count('rel="canonical"') != 1:
                errors.append(f"{rel}: expected one canonical link")

        for raw in parser.json_ld:
            try:
                json.loads(raw)
            except json.JSONDecodeError as exc:
                errors.append(f"{rel}: invalid JSON-LD ({exc})")

        text = path.read_text(encoding="utf-8")
        if "{{" in text or "}}" in text:
            errors.append(f"{rel}: unresolved template placeholder")

        for attr, value in parser.refs:
            if not value or value.startswith("#"):
                if value.startswith("#") and value[1:] not in parser.ids:
                    errors.append(f"{rel}: missing local fragment {value}")
                continue
            resolved = local_target(path, value)
            if resolved is None:
                continue
            target, fragment = resolved
            try:
                target.relative_to(ROOT)
            except ValueError:
                errors.append(f"{rel}: {attr} escapes project root: {value}")
                continue
            if not target.exists():
                errors.append(f"{rel}: missing {attr} target {value}")
                continue
            if fragment and target.suffix.lower() == ".html":
                target_parser = parsed_pages.get(target) or parse_page(target)
                if fragment not in target_parser.ids:
                    errors.append(f"{rel}: missing fragment {value}")

    for xml_name in ("feed.xml", "sitemap.xml"):
        try:
            ET.parse(ROOT / xml_name)
        except ET.ParseError as exc:
            errors.append(f"{xml_name}: invalid XML ({exc})")

    required = [
        ROOT / "assets" / "favicon.ico",
        ROOT / "assets" / "favicon-32x32.png",
        ROOT / "assets" / "og-card.png",
        ROOT / "output" / "pdf" / "hossein-moazami-resume.pdf",
        ROOT / "robots.txt",
    ]
    for path in required:
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing or empty required asset: {path.relative_to(ROOT)}")

    if errors:
        print("Site validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validated {len(PUBLIC_HTML)} public HTML pages, all local links, JSON-LD, XML, and required assets.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
