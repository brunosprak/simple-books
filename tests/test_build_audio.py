from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_audio


class BuildAudioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = build_audio.load_data(
            ROOT / "texts" / "princess-of-mars-ja.json"
        )

    def test_sentence_paths_are_stable_and_one_based(self) -> None:
        self.assertEqual(
            build_audio.sentence_path(2, 4, 5).as_posix(),
            "chapter-02/paragraph-004/sentence-005.mp3",
        )

    def test_expected_entries_cover_every_sentence(self) -> None:
        entries = build_audio.expected_entries(self.data)
        sentence_count = sum(
            len(paragraph)
            for chapter in self.data["chapters"]
            for paragraph in chapter["paragraphs"]
        )
        self.assertEqual(len(entries), sentence_count)
        self.assertIn("chapter-02/paragraph-004/sentence-005.mp3", entries)

    def test_check_accepts_matching_manifest_and_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            entries = build_audio.expected_entries(self.data)
            manifest_items = {}
            for relative, entry in entries.items():
                audio_path = output / relative
                audio_path.parent.mkdir(parents=True, exist_ok=True)
                audio_path.write_bytes(b"fake-mp3")
                manifest_items[relative] = {**entry, "bytes": 8}
            manifest = {
                **build_audio.manifest_settings(self.data["source_file"]),
                "items": manifest_items,
            }
            (output / build_audio.MANIFEST_NAME).write_text(
                json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
            )
            self.assertEqual(build_audio.check_audio(self.data, output), [])

    def test_check_rejects_stale_sentence_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            entries = build_audio.expected_entries(self.data)
            manifest_items = {}
            for relative, entry in entries.items():
                audio_path = output / relative
                audio_path.parent.mkdir(parents=True, exist_ok=True)
                audio_path.write_bytes(b"fake-mp3")
                manifest_items[relative] = {**entry, "bytes": 8}
            first = next(iter(manifest_items.values()))
            first["text_sha256"] = "stale"
            manifest = {
                **build_audio.manifest_settings(self.data["source_file"]),
                "items": manifest_items,
            }
            (output / build_audio.MANIFEST_NAME).write_text(
                json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
            )
            errors = build_audio.check_audio(self.data, output)
            self.assertTrue(any("text_sha256 is stale" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
