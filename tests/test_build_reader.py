from __future__ import annotations

import copy
import json
import re
import struct
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
            (ROOT / "texts" / "princess-of-mars-ja.json").read_text(encoding="utf-8")
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
        self.assertIn('>−¶</button>', first)
        self.assertIn('>＋¶</button>', first)
        self.assertNotIn('>−1¶</button>', first)
        self.assertNotIn('>＋1¶</button>', first)
        self.assertIn('id="chapter-select"', first)
        self.assertIn('id="furigana-toggle"', first)
        self.assertIn('id="gloss-export"', first)
        self.assertIn('id="gloss-import"', first)
        self.assertIn('id="gloss-import-file"', first)
        self.assertIn('id="gloss-speak"', first)
        self.assertIn('function toggleMarkedGlossSpeech', first)
        self.assertIn('function currentSentenceListeningGlosses', first)
        self.assertIn('function speakNextMarkedGlossPart', first)
        self.assertIn('new SpeechSynthesisUtterance', first)
        self.assertIn('{ text: term, lang: "ja-JP" }', first)
        self.assertIn('{ text: portuguese, lang: "pt-BR" }', first)
        self.assertIn('window.speechSynthesis.speak(utterance)', first)
        self.assertIn('entry.reasons === undefined ? ["vocabulary"] : entry.reasons', first)
        self.assertIn('reasons: [...new Set(storedReasons)]', first)
        self.assertIn('id="gloss-count" aria-label="Nenhum gloss marcado">★ 0 · 🎧 0', first)
        self.assertIn('>▶ Escuta</button>', first)
        self.assertIn('function toggleAllGlossReasons', first)
        self.assertIn('reasons: [...glossReasons]', first)
        self.assertIn('toggleAllGlossReasons(surface, gloss)', first)
        self.assertIn('String(vocabularyMarked && listeningMarked)', first)
        self.assertIn('toggleReason("vocabulary")', first)
        self.assertIn('toggleReason("listening")', first)
        self.assertIn('id="offline-chapter-download"', first)
        self.assertIn('id="offline-book-download"', first)
        self.assertIn('id="offline-manage"', first)
        self.assertIn('id="offline-remove"', first)
        self.assertIn('function downloadOffline', first)
        self.assertIn('function offlineUrlsForChapters', first)
        self.assertIn('navigator.serviceWorker.register(offlineWorkerUrl)', first)
        self.assertIn('await cacheOfflineUrls(urls)', first)
        self.assertIn('const offlineVersion = "', first)
        self.assertIn('id="translation-speak"', first)
        self.assertIn('function toggleTranslationSpeech', first)
        self.assertIn('new SpeechSynthesisUtterance(sentences[activeIndex].pt)', first)
        self.assertIn('utterance.lang = "pt-BR"', first)
        self.assertIn('id="sentence-audio-controls"', first)
        self.assertIn('id="sentence-audio-toggle"', first)
        self.assertIn('id="sentence-audio-restart"', first)
        self.assertIn('id="sentence-audio-loop"', first)
        self.assertIn('id="sentence-audio-speed"', first)
        self.assertIn('playSentenceAudio({ restart: true })', first)
        self.assertIn('if (restart) sentenceAudio.currentTime = 0', first)
        self.assertIn('const sentenceAudioLoopDelayMs = 500', first)
        self.assertIn('<option value="sentence">Frase</option>', first)
        self.assertIn('<option value="listening">Glosses + frase</option>', first)
        self.assertIn('<option value="listening-ja">Glosses JP + frase</option>', first)
        self.assertIn('<option value="translation">Tradução + frase</option>', first)
        self.assertIn('<option value="paragraph">Parágrafo</option>', first)
        self.assertIn('<option value="listening-paragraph">Glosses + parágrafo</option>', first)
        self.assertIn('<option value="listening-ja-paragraph">Glosses JP + parágrafo</option>', first)
        self.assertIn('<option value="translation-paragraph">Tradução + parágrafo</option>', first)
        self.assertIn('sentenceAudioLoopMode = sentenceAudioLoop.value', first)
        self.assertIn('function continueSentenceAudioLoop', first)
        self.assertIn('function startGlossesThenSentence', first)
        self.assertIn('function loopModeUsesJapaneseOnlyGlosses', first)
        self.assertIn('japaneseOnly: loopModeUsesJapaneseOnlyGlosses(expectedMode)', first)
        self.assertIn('glosses.map(({ term }) => ({ text: term, lang: "ja-JP" }))', first)
        self.assertIn('Lendo glosses JP…', first)
        self.assertIn('function startTranslationThenSentence', first)
        self.assertIn('function scheduleTranslationThenSentence', first)
        self.assertIn('Tradução em 0,5 s…', first)
        self.assertIn('function startTranslationSpeech', first)
        self.assertIn('Lendo tradução…', first)
        self.assertIn('function reuseUnchangedOfflineAudio', first)
        self.assertIn('function sameOfflineManifestSettings', first)
        self.assertIn('currentManifest.items?.[relativePath]', first)
        self.assertIn('previousManifest.items?.[relativePath]', first)
        self.assertIn('pendingChapters', first)
        self.assertIn('áudios reutilizados', first)
        self.assertIn('function nextSentenceInCurrentParagraph', first)
        self.assertIn('function scheduleNextParagraphSentence', first)
        self.assertIn('renderCard(nextSentenceInCurrentParagraph())', first)
        self.assertIn('sentenceAudioLoopTimer = setTimeout', first)
        self.assertIn('function clearSentenceAudioLoopTimer', first)
        self.assertIn('function updateSentenceAudioLoop', first)
        self.assertIn('function startMarkedGlossSpeech', first)
        self.assertIn('loopSequence: true', first)
        self.assertIn('Frase em 0,5 s…', first)
        self.assertIn('Glosses em 0,5 s…', first)
        self.assertIn('Próxima frase em 0,5 s…', first)
        self.assertIn('audioConfig ? new Audio() : null', first)
        self.assertIn('<link rel="manifest" href="../manifest.webmanifest">', first)
        self.assertIn('<meta name="theme-color" content="#314f46">', first)
        self.assertIn('simple-ja-books:audio-speed:v1:', first)
        self.assertIn('function sentenceAudioPath', first)
        self.assertIn('prepareSentenceAudio(activeChapter, paragraphInChapter, sentenceInParagraph)', first)
        self.assertIn('stopSentenceAudio();', first)
        self.assertIn('simple-ja-books:marked-glosses:v1', first)
        self.assertIn('simple-ja-books:active-card:v1:', first)
        self.assertIn('saveActiveIndex()', first)
        self.assertIn('renderCard(activeIndex);', first)
        self.assertIn('function toggleGlossReason', first)
        self.assertIn('reasons: [...reasons]', first)
        self.assertIn("Exportar dados de leitura em JSON", first)
        self.assertIn("Importar dados de leitura em JSON", first)
        self.assertIn("schema_version: 3", first)
        self.assertIn("reader_state:", first)
        self.assertIn("active_sentence_index: activeIndex", first)
        self.assertIn("positions: readingPositions", first)
        self.assertIn("dados-de-leitura.json", first)
        self.assertIn("[1, 2, 3].includes(payload?.schema_version)", first)
        self.assertIn("[2, 3].includes(payload.schema_version)", first)
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
        self.assertIn("margin: -0.55rem 0 1.25rem", first)
        self.assertIn("min-height: 2.35rem", first)
        self.assertGreater(
            first.index('id="font-decrease"'),
            first.index("</article>"),
        )
        self.assertLess(
            first.index('id="font-increase"'),
            first.index('id="page-footer"'),
        )
        self.assertIn(".study-controls {", first)
        self.assertIn("margin: -0.4rem -0.4rem 0.65rem", first)
        self.assertIn("min-height: 2.4rem", first)
        self.assertIn("white-space: nowrap", first)
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
        self.assertLess(
            first.index('id="vertical-page-next"'),
            first.index('id="vertical-page-previous"'),
        )
        self.assertIn('chapterNextButton.textContent = "← 章"', first)
        self.assertIn('chapterPreviousButton.textContent = "章 →"', first)
        self.assertIn(
            "chapterNextButton,\n          chapterReaderTitle,\n          chapterFuriganaToggle,\n          chapterPreviousButton",
            first,
        )
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
        self.assertIn('if (readingMode === "continuous")', first)
        self.assertIn(
            'setReadingMode(horizontalDistance < 0 ? "vertical" : "sentence")',
            first,
        )
        self.assertIn("navigateChapter(horizontalDistance < 0 ? 1 : -1)", first)
        self.assertIn(
            "Deslize para a direita para Frases ou para a esquerda para Vertical.",
            first,
        )
        self.assertNotIn('id="paragraph-boundary"', first)
        self.assertNotIn("Novo parágrafo", first)
        self.assertNotIn('id="paragraph-end"', first)
        self.assertNotIn("Fim do parágrafo", first)
        self.assertNotIn(".paragraph-end-mark {", first)
        self.assertNotIn("paragraphEndMark", first)
        self.assertIn("paragraphSentenceStarts", first)
        self.assertIn("chapterParagraphStarts", first)
        self.assertIn("chapterParagraphCounts", first)
        self.assertIn("sentenceParagraphIndexes", first)
        self.assertIn("sentenceInParagraph + 1", first)
        self.assertIn("paragraphInChapter + 1", first)
        self.assertIn("chapterParagraphCounts[activeChapter]", first)
        self.assertIn(".selected-sentence.paragraph-start { text-indent: 1em; }", first)
        self.assertIn(
            'selectedSentence.classList.toggle("paragraph-start", sentenceInParagraph === 0)',
            first,
        )
        self.assertIn(".next-sentence-preview {", first)
        self.assertIn("function fittingPreviewPrefix", first)
        self.assertIn("function renderNextSentencePreview", first)
        self.assertIn("sentenceInParagraph >= sentencesInParagraph - 1", first)
        self.assertIn('preview.setAttribute("aria-hidden", "true")', first)
        self.assertIn("scheduleNextSentencePreview();", first)
        self.assertLess(
            first.index('id="selected-sentence"'),
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

    def test_optional_audio_metadata_is_validated(self) -> None:
        data = copy.deepcopy(self.data)
        data["page"]["audio"] = {
            "base_url": "audio",
            "voice": "Nise",
            "speed_levels_percent": [80, 90, 100, 120],
            "default_speed_percent": 100,
        }

        validated = build_reader.validate_data(data)

        self.assertEqual(validated["page"]["audio"]["voice"], "Nise")

    def test_princess_audio_speeds_cover_seventy_to_one_thirty(self) -> None:
        self.assertEqual(
            self.data["page"]["audio"]["speed_levels_percent"],
            list(range(70, 131, 5)),
        )
        self.assertEqual(self.data["page"]["audio"]["default_speed_percent"], 100)

    def test_audio_default_speed_must_be_an_allowed_speed(self) -> None:
        invalid = copy.deepcopy(self.data)
        invalid["page"]["audio"] = {
            "base_url": "audio",
            "voice": "Nise",
            "speed_levels_percent": [80, 100, 120],
            "default_speed_percent": 90,
        }

        with self.assertRaisesRegex(build_reader.BuildError, "default_speed_percent"):
            build_reader.validate_data(invalid)

    def test_audio_speeds_must_be_unique_ascending_positive_integers(self) -> None:
        invalid = copy.deepcopy(self.data)
        invalid["page"]["audio"] = {
            "base_url": "audio",
            "voice": "Nise",
            "speed_levels_percent": [100, 80, 100],
            "default_speed_percent": 100,
        }

        with self.assertRaisesRegex(build_reader.BuildError, "speed_levels_percent"):
            build_reader.validate_data(invalid)

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

        self.assertTrue(output.startswith("火星のプリンセス\n\nエドガー・ライス・バローズ\n\n"))
        self.assertIn(self.data["chapters"][0]["title"], output)
        self.assertIn(
            "".join(
                sentence["text"]
                for sentence in self.data["chapters"][0]["paragraphs"][0]
            ),
            output,
        )
        self.assertTrue(output.endswith("\n"))

    def test_offline_version_changes_with_public_book_data(self) -> None:
        first_data = build_reader.validate_data(copy.deepcopy(self.data))
        second_data = copy.deepcopy(first_data)
        self.first_sentence(second_data)["pt"] += " Atualizada."

        first = build_reader.render(first_data, self.template)
        second = build_reader.render(second_data, self.template)
        pattern = re.compile(r'const offlineVersion = "([0-9a-f]{16})";')

        self.assertNotEqual(pattern.search(first).group(1), pattern.search(second).group(1))

        changed_template = self.template.replace("Leitura offline", "Leitura sem rede", 1)
        third = build_reader.render(first_data, changed_template)
        self.assertNotEqual(pattern.search(first).group(1), pattern.search(third).group(1))

    def test_offline_worker_uses_network_fallback_and_cached_assets(self) -> None:
        worker = (ROOT / "site" / "offline-sw.js").read_text(encoding="utf-8")

        self.assertIn('self.addEventListener("install"', worker)
        self.assertIn('self.addEventListener("activate"', worker)
        self.assertIn('self.addEventListener("fetch"', worker)
        self.assertIn('findCachedResponse(request)', worker)
        self.assertIn('const response = await fetch(request)', worker)
        self.assertIn('event.respondWith(networkFirst(request))', worker)
        self.assertIn('const PWA_CACHE_PREFIX', worker)
        self.assertIn('const PWA_SHELL_URLS', worker)
        self.assertIn('cache.addAll(PWA_SHELL_URLS)', worker)
        self.assertIn('name.startsWith(PWA_CACHE_PREFIX)', worker)

    def test_pwa_manifest_icons_and_library_registration(self) -> None:
        manifest = json.loads(
            (ROOT / "site" / "manifest.webmanifest").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["start_url"], "./princess-of-mars/")
        self.assertEqual(manifest["scope"], "./")
        self.assertEqual(manifest["display"], "standalone")
        self.assertEqual(
            [(icon["src"], icon["sizes"]) for icon in manifest["icons"]],
            [("icons/icon-192.png", "192x192"), ("icons/icon-512.png", "512x512")],
        )

        library = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<link rel="manifest" href="manifest.webmanifest">', library)
        self.assertIn('navigator.serviceWorker.register("offline-sw.js")', library)

        for filename, expected_size in (("icon-192.png", 192), ("icon-512.png", 512)):
            payload = (ROOT / "site" / "icons" / filename).read_bytes()
            self.assertEqual(payload[:8], b"\x89PNG\r\n\x1a\n")
            self.assertEqual(struct.unpack(">II", payload[16:24]), (expected_size, expected_size))

    def test_runtime_reader_fetches_json_without_embedding_book_text(self) -> None:
        validated = build_reader.validate_data(copy.deepcopy(self.data))

        output = build_reader.render(
            validated,
            self.template,
            data_url="../books/princess-of-mars-ja.json",
        )

        self.assertIn('await fetch(bookDataUrl)', output)
        self.assertIn('../books/princess-of-mars-ja.json', output)
        self.assertIn('const bookDataUrl = "../books/princess-of-mars-ja.json"', output)
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
