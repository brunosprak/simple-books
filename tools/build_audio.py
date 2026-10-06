#!/usr/bin/env python3
"""Generate and verify deterministic per-sentence audio for a book reader."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterator

from build_reader import validate_data


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "texts" / "princess-of-mars-ja.json"
DEFAULT_OUTPUT_DIR = ROOT / "site" / "princess-of-mars" / "audio"
DEFAULT_ENGINE_URL = "http://127.0.0.1:10101"
MANIFEST_NAME = "manifest.json"

VOICE = {
    "engine": "AivisSpeech Engine",
    "model_uuid": "6d11c6c2-f4a4-4435-887e-23dd60f8b8dd",
    "model_sha256": "6ff7eaa61c24d37434e2c6ab672fc3ba189ecc9118c08918a486ed5316e5c9d3",
    "speaker_name": "にせ",
    "speaker_uuid": "bf56410a-d8e6-430d-a477-f789e16206d3",
    "style_name": "ノーマル",
}

ENCODING = {
    "speed_scale": 1.0,
    "sample_rate_hz": 44100,
    "channels": 1,
    "codec": "libmp3lame",
    "quality": 2,
}


class AudioBuildError(RuntimeError):
    """Raised when audio generation or verification cannot complete."""


def sentence_path(chapter: int, paragraph: int, sentence: int) -> Path:
    return Path(
        f"chapter-{chapter:02d}",
        f"paragraph-{paragraph:03d}",
        f"sentence-{sentence:03d}.mp3",
    )


def iter_sentences(
    data: dict[str, Any],
) -> Iterator[tuple[int, int, int, str, Path]]:
    for chapter_index, chapter in enumerate(data["chapters"], start=1):
        for paragraph_index, paragraph in enumerate(chapter["paragraphs"], start=1):
            for sentence_index, sentence in enumerate(paragraph, start=1):
                yield (
                    chapter_index,
                    paragraph_index,
                    sentence_index,
                    sentence["text"],
                    sentence_path(chapter_index, paragraph_index, sentence_index),
                )


def text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_data(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as source:
        return validate_data(json.load(source))


def load_manifest(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        with path.open(encoding="utf-8") as source:
            manifest = json.load(source)
    except (OSError, json.JSONDecodeError) as error:
        raise AudioBuildError(f"cannot read {path}: {error}") from error
    if not isinstance(manifest, dict):
        raise AudioBuildError(f"{path} must contain a JSON object")
    return manifest


def manifest_settings(source_file: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "source_file": source_file,
        "voice": VOICE,
        "encoding": ENCODING,
    }


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as temporary:
        json.dump(manifest, temporary, ensure_ascii=False, indent=2)
        temporary.write("\n")
        temporary_path = Path(temporary.name)
    os.replace(temporary_path, path)


def request_json(url: str, *, body: bytes | None = None) -> Any:
    headers = {"Content-Type": "application/json"} if body is not None else {}
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as error:
        raise AudioBuildError(f"AivisSpeech request failed: {url}: {error}") from error


def find_speaker_id(engine_url: str) -> int:
    try:
        with urllib.request.urlopen(f"{engine_url}/speakers", timeout=30) as response:
            speakers = json.loads(response.read().decode("utf-8"))
    except Exception as error:
        raise AudioBuildError(
            f"cannot connect to AivisSpeech at {engine_url}: {error}"
        ) from error

    for speaker in speakers:
        if (
            speaker.get("name") == VOICE["speaker_name"]
            and speaker.get("speaker_uuid") == VOICE["speaker_uuid"]
        ):
            for style in speaker.get("styles", []):
                if style.get("name") == VOICE["style_name"]:
                    return int(style["id"])
    raise AudioBuildError(
        "the pinned Nise voice/style is not installed in AivisSpeech"
    )


def synthesize_wav(engine_url: str, speaker_id: int, text: str) -> bytes:
    parameters = urllib.parse.urlencode({"text": text, "speaker": speaker_id})
    query = request_json(f"{engine_url}/audio_query?{parameters}", body=b"")
    query["speedScale"] = ENCODING["speed_scale"]
    query["outputSamplingRate"] = ENCODING["sample_rate_hz"]
    query["outputStereo"] = False
    body = json.dumps(query, ensure_ascii=False).encode("utf-8")
    url = f"{engine_url}/synthesis?{urllib.parse.urlencode({'speaker': speaker_id})}"
    request = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            return response.read()
    except Exception as error:
        raise AudioBuildError(f"AivisSpeech synthesis failed: {error}") from error


def encode_mp3(wav: bytes, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    wav_path: Path | None = None
    mp3_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
            wav_file.write(wav)
            wav_path = Path(wav_file.name)
        with tempfile.NamedTemporaryFile(
            suffix=".mp3", dir=output.parent, delete=False
        ) as mp3_file:
            mp3_path = Path(mp3_file.name)
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(wav_path),
                "-map_metadata",
                "-1",
                "-codec:a",
                ENCODING["codec"],
                "-q:a",
                str(ENCODING["quality"]),
                str(mp3_path),
            ],
            check=True,
        )
        os.replace(mp3_path, output)
        mp3_path = None
    except (OSError, subprocess.CalledProcessError) as error:
        raise AudioBuildError(f"ffmpeg failed for {output}: {error}") from error
    finally:
        if wav_path is not None:
            wav_path.unlink(missing_ok=True)
        if mp3_path is not None:
            mp3_path.unlink(missing_ok=True)


def expected_entries(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    for chapter, paragraph, sentence, text, relative_path in iter_sentences(data):
        entries[relative_path.as_posix()] = {
            "chapter": chapter,
            "paragraph": paragraph,
            "sentence": sentence,
            "text_sha256": text_sha256(text),
        }
    return entries


def check_audio(data: dict[str, Any], output_dir: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = output_dir / MANIFEST_NAME
    manifest = load_manifest(manifest_path)
    if manifest is None:
        return [f"missing {manifest_path}"]

    settings = manifest_settings(data["source_file"])
    for key, expected in settings.items():
        if manifest.get(key) != expected:
            errors.append(f"manifest {key} does not match the pinned configuration")

    expected = expected_entries(data)
    actual = manifest.get("items")
    if not isinstance(actual, dict):
        return errors + ["manifest items must be an object"]
    if set(actual) != set(expected):
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        if missing:
            errors.append(f"manifest is missing {len(missing)} sentence entries")
        if extra:
            errors.append(f"manifest has {len(extra)} obsolete sentence entries")

    for relative, expected_entry in expected.items():
        entry = actual.get(relative)
        if not isinstance(entry, dict):
            continue
        for key, value in expected_entry.items():
            if entry.get(key) != value:
                errors.append(f"{relative}: manifest {key} is stale")
        audio_path = output_dir / relative
        if not audio_path.is_file():
            errors.append(f"{relative}: MP3 is missing")
        elif audio_path.stat().st_size != entry.get("bytes"):
            errors.append(f"{relative}: file size does not match the manifest")

    actual_mp3s = {
        path.relative_to(output_dir).as_posix() for path in output_dir.rglob("*.mp3")
    }
    extra_mp3s = sorted(actual_mp3s - set(expected))
    if extra_mp3s:
        errors.append(f"audio directory has {len(extra_mp3s)} obsolete MP3 files")
    return errors


def generate_audio(data: dict[str, Any], output_dir: Path, engine_url: str) -> None:
    manifest_path = output_dir / MANIFEST_NAME
    previous = load_manifest(manifest_path) or {}
    settings = manifest_settings(data["source_file"])
    settings_match = all(previous.get(key) == value for key, value in settings.items())
    previous_items = previous.get("items", {}) if settings_match else {}
    if not isinstance(previous_items, dict):
        previous_items = {}

    planned = list(iter_sentences(data))
    speaker_id = find_speaker_id(engine_url)
    items: dict[str, dict[str, Any]] = {}
    generated = 0
    skipped = 0

    for position, (chapter, paragraph, sentence, text, relative_path) in enumerate(
        planned, start=1
    ):
        relative = relative_path.as_posix()
        audio_path = output_dir / relative_path
        entry = {
            "chapter": chapter,
            "paragraph": paragraph,
            "sentence": sentence,
            "text_sha256": text_sha256(text),
        }
        previous_entry = previous_items.get(relative)
        if (
            isinstance(previous_entry, dict)
            and previous_entry == {**entry, "bytes": previous_entry.get("bytes")}
            and audio_path.is_file()
            and audio_path.stat().st_size == previous_entry.get("bytes")
        ):
            items[relative] = previous_entry
            skipped += 1
            print(f"[{position}/{len(planned)}] skip {relative}", flush=True)
            continue

        wav = synthesize_wav(engine_url, speaker_id, text)
        encode_mp3(wav, audio_path)
        entry["bytes"] = audio_path.stat().st_size
        items[relative] = entry
        generated += 1
        print(f"[{position}/{len(planned)}] generated {relative}", flush=True)

        checkpoint = {**settings, "items": items}
        write_manifest(manifest_path, checkpoint)

    write_manifest(manifest_path, {**settings, "items": items})
    print(f"generated {generated}; reused {skipped}; total {len(planned)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--engine-url", default=DEFAULT_ENGINE_URL)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        data = load_data(args.data)
        if args.check:
            errors = check_audio(data, args.output_dir)
            if errors:
                for error in errors:
                    print(error)
                return 1
            print(f"audio is current: {args.output_dir}")
        else:
            generate_audio(data, args.output_dir, args.engine_url.rstrip("/"))
    except (AudioBuildError, OSError, json.JSONDecodeError) as error:
        print(f"error: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
