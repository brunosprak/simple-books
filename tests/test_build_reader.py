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
        self.assertIn('id="study-previous-paragraph"', first)
        self.assertIn('id="study-next-paragraph"', first)
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
        self.assertIn("Exportar dados de leitura em JSON", first)
        self.assertIn("Importar dados de leitura em JSON", first)
        self.assertIn("schema_version: 2", first)
        self.assertIn("reader_state:", first)
        self.assertIn("active_sentence_index: activeIndex", first)
        self.assertIn("positions: readingPositions", first)
        self.assertIn("dados-de-leitura.json", first)
        self.assertIn("[1, 2].includes(payload?.schema_version)", first)
        self.assertIn("payload.schema_version === 2", first)
        self.assertIn("simple-ja-books:furigana-visible:v1:", first)
        self.assertIn("renderCard(activeIndex - 1)", first)
        self.assertIn("renderCard(activeIndex + 1)", first)
        self.assertIn("paragraphSentenceStarts[activeParagraph - 1]", first)
        self.assertIn("paragraphSentenceStarts[activeParagraph + 1]", first)
        self.assertIn("touch-action: pan-y", first)
        self.assertIn('panel.addEventListener("pointerdown"', first)
        self.assertIn('panel.addEventListener("pointerup"', first)
        self.assertIn("suppressClickAfterSwipe", first)
        self.assertIn("showPreviousSentence()", first)
        self.assertIn("showNextSentence()", first)
        self.assertIn('aria-label="Alternar furigana"', first)
        self.assertIn('selectedSentence.addEventListener("click", toggleFurigana)', first)
        self.assertIn('selectedSentence.addEventListener("keydown"', first)
        self.assertIn('data-reading-mode="sentence"', first)
        self.assertIn('data-reading-mode="continuous"', first)
        self.assertIn('data-reading-mode="vertical"', first)
        self.assertIn('>Frases</button>', first)
        self.assertIn('>Corrido</button>', first)
        self.assertIn('>Vertical</button>', first)
        self.assertIn(".reading-mode-switch {", first)
        self.assertIn(".study-controls {", first)
        self.assertIn('class="study-controls"', first)
        self.assertNotIn(".study-controls {\n      position: sticky;", first)
        self.assertLess(
            first.index('class="study-topline"'),
            first.index('class="gloss-tools"'),
        )
        self.assertIn("simple-ja-books:reading-positions:v1:", first)
        self.assertIn("function captureReadingPosition", first)
        self.assertIn("function restoreSentencePosition", first)
        self.assertIn('window.addEventListener("pagehide"', first)
        self.assertIn('chapterReadingViewport.addEventListener("scroll"', first)
        self.assertIn("const previousMode = readingMode;", first)
        self.assertIn("const currentChapter = chapterReaderIndex;", first)
        self.assertIn("renderFullChapter(readingPositions[mode].chapterIndex);", first)
        self.assertNotIn("activeIndex = chapterSentenceStarts[chapterIndex];", first)
        self.assertIn('id="chapter-reader"', first)
        self.assertIn('id="chapter-reading-text"', first)
        self.assertIn("writing-mode: vertical-rl", first)
        self.assertIn('id="vertical-page-controls"', first)
        self.assertIn('id="vertical-page-previous"', first)
        self.assertIn('id="vertical-page-next"', first)
        self.assertIn("function navigateVerticalPage", first)
        self.assertIn("function hideClippedVerticalFurigana", first)
        self.assertIn('annotation.style.visibility = "hidden"', first)
        self.assertIn("verticalPageIndex", first)
        self.assertIn("readableColumns * columnWidth", first)
        self.assertIn("contentWidth / verticalPageWidth", first)
        self.assertIn("paddedPagesWidth - contentWidth - gutterWidth", first)
        self.assertIn("verticalStartScrollLeft - (verticalPageIndex * verticalPageWidth)", first)
        self.assertIn("horizontalDistance > 0 ? 1 : -1", first)
        self.assertIn("margin: 0 0 0 2.25em", first)
        self.assertNotIn("position: absolute", first)
        self.assertIn('style.setProperty("--vertical-page-gutter"', first)
        self.assertIn('chapterReadingViewport.addEventListener("pointerup"', first)
        self.assertIn("overflow-x: hidden", first)
        self.assertIn(".chapter-reading-text p {", first)
        self.assertIn("font-size: inherit;", first)
        self.assertIn("renderFullChapter", first)
        self.assertIn("appendSentenceWithRuby(paragraphElement, sentence)", first)
        self.assertIn('chapterReadingText.addEventListener("click", toggleFurigana)', first)
        self.assertIn("navigateChapter(horizontalDistance < 0 ? 1 : -1)", first)
        self.assertIn('id="paragraph-boundary"', first)
        self.assertIn('id="paragraph-end"', first)
        self.assertIn("paragraphSentenceStarts", first)
        self.assertIn("sentenceParagraphIndexes", first)
        self.assertIn("sentenceInParagraph + 1", first)
        self.assertLess(
            first.index('id="selected-sentence"'),
            first.index('id="paragraph-end"'),
        )
        self.assertLess(
            first.index('id="paragraph-end"'),
            first.index('id="interlinear"'),
        )
        self.assertNotIn('id="gloss-status"', first)
        self.assertNotIn('content: "✓"', first)
        self.assertNotIn('id="reading-text"', first)
        self.assertIn("visibility: hidden", first)
        self.assertNotIn("position: sticky", first)
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

    def test_optional_page_labels_may_be_empty(self) -> None:
        data = copy.deepcopy(self.data)
        data["page"]["eyebrow"] = ""
        data["page"]["study_hint"] = ""

        validated = build_reader.validate_data(data)
        output = build_reader.render(validated, self.template)

        self.assertIn('<p class="eyebrow" id="page-eyebrow"></p>', output)
        self.assertIn('<p class="study-hint" id="study-hint"></p>', output)
        self.assertIn(".eyebrow:empty", output)

    def test_validation_rejects_uncovered_sentence_text(self) -> None:
        invalid = copy.deepcopy(self.data)
        sentence = self.first_sentence(invalid)
        sentence["text"] = "追加" + sentence["text"]

        with self.assertRaisesRegex(build_reader.BuildError, "uncovered text"):
            build_reader.validate_data(invalid)

    def test_validation_rejects_punctuation_only_chunk(self) -> None:
        invalid = copy.deepcopy(self.data)
        self.first_sentence(invalid)["chunks"].append(["。", "。", "."])

        with self.assertRaisesRegex(build_reader.BuildError, "punctuation only"):
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
