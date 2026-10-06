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
import unicodedata
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
    if data.get("schema_version") != 2:
        raise BuildError("schema_version must be 2")
    if "paragraphs" in data:
        raise BuildError("root-level paragraphs is obsolete; nest paragraphs in chapters")

    page = data.get("page")
    if not isinstance(page, dict):
        raise BuildError("page must be an object")
    for obsolete_key in ("html_file", "section_title"):
        if obsolete_key in page:
            raise BuildError(f"page.{obsolete_key} is obsolete")
    for key in (
        "title",
        "author",
        "description",
        "footer",
    ):
        require_string(page, key, "page")
    for key in ("eyebrow", "study_hint"):
        if not isinstance(page.get(key), str):
            raise BuildError(f"page.{key} must be a string")

    levels = page.get("font_levels_percent")
    if (
        not isinstance(levels, list)
        or len(levels) < 2
        or any(not isinstance(value, int) or value <= 0 for value in levels)
        or levels != sorted(set(levels))
    ):
        raise BuildError(
            "page.font_levels_percent must contain unique ascending positive integers"
        )
    default_level = page.get("default_font_level_percent")
    if default_level not in levels:
        raise BuildError(
            "page.default_font_level_percent must occur in font_levels_percent"
        )

    audio = page.get("audio")
    if audio is not None:
        if not isinstance(audio, dict):
            raise BuildError("page.audio must be an object")
        require_string(audio, "base_url", "page.audio")
        require_string(audio, "voice", "page.audio")
        speed_levels = audio.get("speed_levels_percent")
        if (
            not isinstance(speed_levels, list)
            or not speed_levels
            or any(
                not isinstance(value, int) or value <= 0
                for value in speed_levels
            )
            or speed_levels != sorted(set(speed_levels))
        ):
            raise BuildError(
                "page.audio.speed_levels_percent must contain unique ascending "
                "positive integers"
            )
        if audio.get("default_speed_percent") not in speed_levels:
            raise BuildError(
                "page.audio.default_speed_percent must occur in "
                "speed_levels_percent"
            )

    chapters = data.get("chapters")
    if not isinstance(chapters, list) or not chapters:
        raise BuildError("chapters must be a non-empty array")
    for chapter_index, chapter in enumerate(chapters, start=1):
        if not isinstance(chapter, dict):
            raise BuildError(f"chapters[{chapter_index}] must be an object")
        require_string(chapter, "title", f"chapters[{chapter_index}]")
        paragraphs = chapter.get("paragraphs")
        if not isinstance(paragraphs, list) or not paragraphs:
            raise BuildError(f"chapters[{chapter_index}].paragraphs must be non-empty")

        for paragraph_index, paragraph in enumerate(paragraphs, start=1):
            if not isinstance(paragraph, list) or not paragraph:
                raise BuildError(
                    f"chapter {chapter_index}, paragraph {paragraph_index} must be non-empty"
                )
            for sentence_index, sentence in enumerate(paragraph, start=1):
                context = (
                    f"chapter {chapter_index}, paragraph {paragraph_index}, "
                    f"sentence {sentence_index}"
                )
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
                    if all(
                        unicodedata.category(character).startswith("P")
                        for character in surface
                    ):
                        raise BuildError(
                            f"{context}, chunk {chunk_index} must not contain "
                            "punctuation only"
                        )
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


def render(
    data: dict[str, Any], template: str, *, data_url: str | None = None
) -> str:
    page = data["page"]
    levels = page["font_levels_percent"]
    default_index = levels.index(page["default_font_level_percent"])

    replacements = {
        "{{META_DESCRIPTION}}": html.escape(page["description"], quote=True),
        "{{TITLE}}": html.escape(page["title"]),
        "{{EYEBROW}}": html.escape(page["eyebrow"]),
        "{{AUTHOR}}": html.escape(page["author"]),
        "{{STUDY_HINT}}": html.escape(page["study_hint"]),
        "{{FOOTER}}": html.escape(page["footer"]),
        "__FONT_LEVELS_JSON__": javascript_json(levels),
        "__DEFAULT_FONT_INDEX__": str(default_index),
    }

    output = template
    for marker, value in replacements.items():
        if marker not in output:
            raise BuildError(f"template marker is missing: {marker}")
        output = output.replace(marker, value)

    if data_url:
        data_block = (
            "    // BOOK_DATA_START\n"
            f"    const bookDataUrl = {javascript_json(data_url)};\n"
            "    const bookDataResponse = await fetch(bookDataUrl);\n"
            "    if (!bookDataResponse.ok) {\n"
            "      throw new Error(`Falha ao carregar o livro: ${bookDataResponse.status}`);\n"
            "    }\n"
            "    const bookData = await bookDataResponse.json();\n"
            "    const chapters = bookData.chapters;\n"
            "    // BOOK_DATA_END"
        )
    else:
        chapters = javascript_json(data["chapters"], indent=6)
        indented = "\n".join(f"    {line}" for line in chapters.splitlines())
        data_block = (
            "    // BOOK_DATA_START\n"
            f"    const chapters = {indented.lstrip()};\n"
            "    const bookData = null;\n"
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


def render_public_json(data: dict[str, Any]) -> str:
    """Render validated canonical data for browser-side loading."""
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def render_text(data: dict[str, Any]) -> str:
    """Render a clean, disposable Japanese reading copy from canonical JSON."""
    page = data["page"]
    blocks = [page["title"], page["author"]]
    for chapter in data["chapters"]:
        blocks.append(chapter["title"])
        blocks.extend(
            "".join(sentence["text"] for sentence in paragraph)
            for paragraph in chapter["paragraphs"]
        )
    return "\n\n".join(blocks).rstrip() + "\n"


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
        "--data-url",
        help="load book data at runtime from this URL instead of embedding it",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        help="publish a normalized copy of the validated JSON for the browser",
    )
    parser.add_argument(
        "--text-output",
        type=Path,
        help="optionally export a clean Japanese TXT from the canonical JSON",
    )
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
        output = render(data, template, data_url=args.data_url)
        json_output = render_public_json(data) if args.json_output else None
        text_output = render_text(data) if args.text_output else None
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
        if args.text_output:
            try:
                current_text = args.text_output.read_text(encoding="utf-8")
            except FileNotFoundError:
                current_text = None
            if current_text != text_output:
                print(f"stale: {args.text_output}", file=sys.stderr)
                return 1
        if args.json_output:
            try:
                current_json = args.json_output.read_text(encoding="utf-8")
            except FileNotFoundError:
                current_json = None
            if current_json != json_output:
                print(f"stale: {args.json_output}", file=sys.stderr)
                return 1
        print(f"up to date: {args.output}")
        if args.text_output:
            print(f"up to date: {args.text_output}")
        if args.json_output:
            print(f"up to date: {args.json_output}")
        return 0

    write_atomic(args.output, output)
    print(f"generated: {args.output}")
    if args.text_output and text_output is not None:
        write_atomic(args.text_output, text_output)
        print(f"generated: {args.text_output}")
    if args.json_output and json_output is not None:
        write_atomic(args.json_output, json_output)
        print(f"generated: {args.json_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
