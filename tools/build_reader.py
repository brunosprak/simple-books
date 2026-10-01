#!/usr/bin/env python3
"""Build the static Japanese reader deterministically from its JSON data."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "texts" / "call-of-cthulhu-ja.json"
DEFAULT_TEMPLATE = ROOT / "site" / "reader.template.html"
DEFAULT_OUTPUT = ROOT / "site" / "index.html"
ALLOWED_GAPS = re.compile(r"^[\s、。！？…—―「」『』（）・]*$")
DATA_BLOCK = re.compile(
    r"(?ms)^    // BOOK_DATA_START\n.*?^    // BOOK_DATA_END$"
)
UNRESOLVED_MARKER = re.compile(r"\{\{[A-Z0-9_]+\}\}|__[A-Z0-9_]+__")


class BuildError(ValueError):
    """Raised when reader data or its template is invalid."""


def require_string(container: dict[str, Any], key: str, context: str) -> str:
    value = container.get(key)
    if not isinstance(value, str) or not value:
        raise BuildError(f"{context}.{key} must be a non-empty string")
    return value


def validate_data(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise BuildError("the JSON root must be an object")
    if data.get("schema_version") != 1:
        raise BuildError("schema_version must be 1")

    page = data.get("page")
    if not isinstance(page, dict):
        raise BuildError("page must be an object")
    for key in (
        "title",
        "author",
        "eyebrow",
        "description",
        "section_title",
        "study_hint",
        "footer",
    ):
        require_string(page, key, "page")

    levels = page.get("font_levels_percent")
    if (
        not isinstance(levels, list)
        or len(levels) != 5
        or any(not isinstance(value, int) or value <= 0 for value in levels)
        or levels != sorted(set(levels))
    ):
        raise BuildError(
            "page.font_levels_percent must contain five unique ascending positive integers"
        )
    default_level = page.get("default_font_level_percent")
    if default_level not in levels:
        raise BuildError(
            "page.default_font_level_percent must occur in font_levels_percent"
        )

    paragraphs = data.get("paragraphs")
    if not isinstance(paragraphs, list) or not paragraphs:
        raise BuildError("paragraphs must be a non-empty array")

    for paragraph_index, paragraph in enumerate(paragraphs, start=1):
        if not isinstance(paragraph, list) or not paragraph:
            raise BuildError(f"paragraphs[{paragraph_index}] must be non-empty")
        for sentence_index, sentence in enumerate(paragraph, start=1):
            context = f"paragraph {paragraph_index}, sentence {sentence_index}"
            if not isinstance(sentence, dict):
                raise BuildError(f"{context} must be an object")
            text = require_string(sentence, "text", context)
            require_string(sentence, "pt", context)
            chunks = sentence.get("chunks")
            if not isinstance(chunks, list) or not chunks:
                raise BuildError(f"{context}.chunks must be non-empty")

            cursor = 0
            for chunk_index, chunk in enumerate(chunks, start=1):
                if (
                    not isinstance(chunk, list)
                    or len(chunk) != 3
                    or any(not isinstance(item, str) or not item for item in chunk)
                ):
                    raise BuildError(
                        f"{context}, chunk {chunk_index} must contain "
                        "[surface, reading, gloss]"
                    )
                surface = chunk[0]
                start = text.find(surface, cursor)
                if start < 0:
                    raise BuildError(
                        f"{context}, chunk {chunk_index} is absent or out of order: "
                        f"{surface!r}"
                    )
                gap = text[cursor:start]
                if not ALLOWED_GAPS.fullmatch(gap):
                    raise BuildError(
                        f"{context} has uncovered text before chunk {chunk_index}: {gap!r}"
                    )
                cursor = start + len(surface)

            remainder = text[cursor:]
            if not ALLOWED_GAPS.fullmatch(remainder):
                raise BuildError(
                    f"{context} has uncovered text after its final chunk: {remainder!r}"
                )

    return data


def javascript_json(value: Any, *, indent: int | None = None) -> str:
    rendered = json.dumps(value, ensure_ascii=False, indent=indent)
    return (
        rendered.replace("</script", "<\\/script")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def render(data: dict[str, Any], template: str) -> str:
    page = data["page"]
    levels = page["font_levels_percent"]
    default_index = levels.index(page["default_font_level_percent"]) - 2

    replacements = {
        "{{META_DESCRIPTION}}": html.escape(page["description"], quote=True),
        "{{TITLE}}": html.escape(page["title"]),
        "{{EYEBROW}}": html.escape(page["eyebrow"]),
        "{{AUTHOR}}": html.escape(page["author"]),
        "{{SECTION_TITLE}}": html.escape(page["section_title"]),
        "{{STUDY_HINT}}": html.escape(page["study_hint"]),
        "{{FOOTER}}": html.escape(page["footer"]),
        "__FONT_LEVELS_JSON__": javascript_json(levels),
        "__DEFAULT_FONT_LEVEL__": str(default_index),
    }

    output = template
    for marker, value in replacements.items():
        if marker not in output:
            raise BuildError(f"template marker is missing: {marker}")
        output = output.replace(marker, value)

    paragraphs = javascript_json(data["paragraphs"], indent=6)
    indented = "\n".join(f"    {line}" for line in paragraphs.splitlines())
    data_block = (
        "    // BOOK_DATA_START\n"
        f"    const paragraphs = {indented.lstrip()};\n"
        "    // BOOK_DATA_END"
    )
    output, replacements_count = DATA_BLOCK.subn(
        lambda _match: data_block, output, count=1
    )
    if replacements_count != 1:
        raise BuildError("template must contain exactly one BOOK_DATA block")

    unresolved = UNRESOLVED_MARKER.search(output)
    if unresolved:
        raise BuildError(f"unresolved template marker: {unresolved.group(0)}")
    return output.rstrip() + "\n"


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = content.encode("utf-8")
    with tempfile.NamedTemporaryFile(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False
    ) as temporary:
        temporary.write(encoded)
        temporary.flush()
        os.fsync(temporary.fileno())
        temporary_path = Path(temporary.name)
    os.replace(temporary_path, path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the static Japanese reader from structured JSON."
    )
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit with an error instead of writing when the output is stale",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        with args.data.open(encoding="utf-8") as source:
            data = validate_data(json.load(source))
        template = args.template.read_text(encoding="utf-8")
        output = render(data, template)
    except (BuildError, json.JSONDecodeError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if args.check:
        try:
            current = args.output.read_text(encoding="utf-8")
        except FileNotFoundError:
            current = None
        if current != output:
            print(f"stale: {args.output}", file=sys.stderr)
            return 1
        print(f"up to date: {args.output}")
        return 0

    write_atomic(args.output, output)
    print(f"generated: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
