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

    @staticmethod
    def first_sentence(data: dict) -> dict:
        return data["chapters"][0]["paragraphs"][0][0]

    def test_render_is_deterministic_and_resolves_markers(self) -> None:
        validated = build_reader.validate_data(copy.deepcopy(self.data))
        first = build_reader.render(validated, self.template)
        second = build_reader.render(validated, self.template)

        self.assertEqual(first, second)
        self.assertIsNone(build_reader.UNRESOLVED_MARKER.search(first))
        self.assertIn(self.data["page"]["title"], first)
        self.assertIn(self.first_sentence(self.data)["text"], first)
        self.assertIn('id="study-previous"', first)
        self.assertIn('id="study-next"', first)
        self.assertIn('id="study-previous-ten"', first)
        self.assertIn('id="study-next-ten"', first)
        self.assertIn('id="chapter-select"', first)
        self.assertIn('id="furigana-toggle"', first)
        self.assertIn('id="gloss-export"', first)
        self.assertIn('id="gloss-import"', first)
        self.assertIn('id="gloss-import-file"', first)
        self.assertIn('simple-ja-books:marked-glosses:v1', first)
        self.assertIn('simple-ja-books:active-card:v1:', first)
        self.assertIn('saveActiveIndex()', first)
        self.assertIn('renderCard(activeIndex);', first)
        self.assertIn('portuguese: gloss', first)
        self.assertIn("renderCard(activeIndex - 1)", first)
        self.assertIn("renderCard(activeIndex + 1)", first)
        self.assertIn("activeIndex - 10", first)
        self.assertIn("activeIndex + 10", first)
        self.assertNotIn('id="gloss-status"', first)
        self.assertNotIn('content: "✓"', first)
        self.assertNotIn('id="reading-text"', first)
        self.assertIn("visibility: hidden", first)
        self.assertIn("position: sticky", first)
        self.assertLess(
            first.index('id="study-previous"'),
            first.index('id="furigana-toggle"'),
        )
        self.assertLess(
            first.index('id="furigana-toggle"'),
            first.index('id="study-next"'),
        )

    def test_validation_rejects_out_of_order_chunks(self) -> None:
        invalid = copy.deepcopy(self.data)
        chunks = self.first_sentence(invalid)["chunks"]
        chunks[0], chunks[1] = chunks[1], chunks[0]

        with self.assertRaisesRegex(
            build_reader.BuildError, "uncovered text|absent or out of order"
        ):
            build_reader.validate_data(invalid)

    def test_validation_rejects_uncovered_sentence_text(self) -> None:
        invalid = copy.deepcopy(self.data)
        sentence = self.first_sentence(invalid)
        sentence["text"] = "追加" + sentence["text"]

        with self.assertRaisesRegex(build_reader.BuildError, "uncovered text"):
            build_reader.validate_data(invalid)

    def test_backslashes_in_json_are_not_interpreted_by_regex(self) -> None:
        data = copy.deepcopy(self.data)
        self.first_sentence(data)["pt"] = r"C:\temp\1"
        validated = build_reader.validate_data(data)

        output = build_reader.render(validated, self.template)

        self.assertIn(r"C:\\temp\\1", output)

    def test_plain_text_is_derived_from_canonical_json(self) -> None:
        validated = build_reader.validate_data(copy.deepcopy(self.data))

        output = build_reader.render_text(validated)

        self.assertTrue(output.startswith("クトゥルフの呼び声\n\nH・P・ラヴクラフト\n\n"))
        self.assertIn(self.data["chapters"][0]["title"], output)
        self.assertIn(
            "".join(
                sentence["text"]
                for sentence in self.data["chapters"][0]["paragraphs"][0]
            ),
            output,
        )
        self.assertTrue(output.endswith("\n"))

    def test_runtime_reader_fetches_json_without_embedding_book_text(self) -> None:
        validated = build_reader.validate_data(copy.deepcopy(self.data))

        output = build_reader.render(
            validated,
            self.template,
            data_url="../books/call-of-cthulhu-ja.json",
        )

        self.assertIn('await fetch(bookDataUrl)', output)
        self.assertIn('../books/call-of-cthulhu-ja.json', output)
        self.assertNotIn(self.first_sentence(self.data)["text"], output)
        self.assertIn('document.querySelector("#page-title")', output)

    def test_public_json_is_deterministic(self) -> None:
        validated = build_reader.validate_data(copy.deepcopy(self.data))
        first = build_reader.render_public_json(validated)
        second = build_reader.render_public_json(validated)

        self.assertEqual(first, second)
        self.assertEqual(json.loads(first), self.data)

    def test_validation_rejects_obsolete_flat_structure(self) -> None:
        invalid = copy.deepcopy(self.data)
        invalid["paragraphs"] = invalid["chapters"][0]["paragraphs"]

        with self.assertRaisesRegex(build_reader.BuildError, "root-level paragraphs"):
            build_reader.validate_data(invalid)


if __name__ == "__main__":
    unittest.main()
