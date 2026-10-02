from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_reader


class BuildReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(
            (ROOT / "texts" / "call-of-cthulhu-ja.json").read_text(encoding="utf-8")
        )
        cls.template = (ROOT / "site" / "reader.template.html").read_text(
            encoding="utf-8"
        )

    def test_render_is_deterministic_and_resolves_markers(self) -> None:
        validated = build_reader.validate_data(copy.deepcopy(self.data))
        first = build_reader.render(validated, self.template)
        second = build_reader.render(validated, self.template)

        self.assertEqual(first, second)
        self.assertIsNone(build_reader.UNRESOLVED_MARKER.search(first))
        self.assertIn(self.data["page"]["title"], first)
        self.assertIn(self.data["paragraphs"][0][0]["text"], first)
        self.assertIn('id="study-previous"', first)
        self.assertIn('id="study-next"', first)
        self.assertIn('id="furigana-toggle"', first)
        self.assertIn("renderCard(activeIndex - 1)", first)
        self.assertIn("renderCard(activeIndex + 1)", first)
        self.assertNotIn('id="reading-text"', first)

    def test_validation_rejects_out_of_order_chunks(self) -> None:
        invalid = copy.deepcopy(self.data)
        chunks = invalid["paragraphs"][0][0]["chunks"]
        chunks[0], chunks[1] = chunks[1], chunks[0]

        with self.assertRaisesRegex(
            build_reader.BuildError, "uncovered text|absent or out of order"
        ):
            build_reader.validate_data(invalid)

    def test_validation_rejects_uncovered_sentence_text(self) -> None:
        invalid = copy.deepcopy(self.data)
        invalid["paragraphs"][0][0]["text"] = (
            "追加" + invalid["paragraphs"][0][0]["text"]
        )

        with self.assertRaisesRegex(build_reader.BuildError, "uncovered text"):
            build_reader.validate_data(invalid)

    def test_backslashes_in_json_are_not_interpreted_by_regex(self) -> None:
        data = copy.deepcopy(self.data)
        data["paragraphs"][0][0]["pt"] = r"C:\temp\1"
        validated = build_reader.validate_data(data)

        output = build_reader.render(validated, self.template)

        self.assertIn(r"C:\\temp\\1", output)


if __name__ == "__main__":
    unittest.main()
