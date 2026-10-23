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
        self.assertIn('id="editable-book-panel"', first)
        self.assertIn('id="editable-chapter-form"', first)
        self.assertIn('id="editable-paragraph-generate"', first)
        self.assertIn('id="editable-paragraph-status"', first)
        self.assertIn('function setEditableParagraphStatus', first)
        self.assertIn('function fetchEditableParagraphResponse', first)
        self.assertIn('abortController.abort()', first)
        self.assertIn('Motivo informado pela API', first)
        self.assertIn('editableParagraphGenerate.textContent = "Gerando…"', first)
        self.assertIn('<summary>Adicionar capítulo</summary>', first)
        self.assertIn('<summary>Gerenciar parágrafos</summary>', first)
        self.assertIn('id="editable-paragraph-delete-target"', first)
        self.assertIn('id="editable-paragraph-delete"', first)
        self.assertIn('function deleteEditableParagraph', first)
        self.assertIn('Excluir permanentemente este parágrafo?', first)
        self.assertIn('chapters[chapterIndex].paragraphs.splice(paragraphIndex, 1)', first)
        self.assertIn('editableParagraphDelete.addEventListener("click", deleteEditableParagraph)', first)
        self.assertIn('simple-ja-books:editable-book:v1:', first)
        self.assertIn('function generateEditableParagraph', first)
        self.assertIn('const indexedCharacters = Array.from(paragraphText)', first)
        self.assertIn('sentence_end: { type: "integer" }', first)
        self.assertIn('chunk_end: { type: "integer" }', first)
        self.assertIn('const surface = characters.slice(chunkStart, chunkEnd).join("")', first)
        self.assertIn('text: characters.slice(sentenceStart, sentenceEnd).join("")', first)
        self.assertIn('if (sentenceStart !== characters.length)', first)
        self.assertIn('const paragraphText = editableParagraphText.value;', first)
        self.assertIn('if (!paragraphText.trim())', first)
        self.assertNotIn('const paragraphText = editableParagraphText.value.trim();', first)
        self.assertIn('function renderEditableBookManager', first)
        self.assertIn('A API dividirá o parágrafo em frases e chunks', first)
        self.assertIn('const standaloneEditableParticles = new Set', first)
        self.assertIn('function editableChunkIsStandaloneParticle', first)
        self.assertIn('editableChunkIsStandaloneParticle(surface)', first)
        self.assertIn('A resposta separou partículas em chunks', first)
        self.assertIn('Nunca deixe partículas isoladas em um chunk', first)
        self.assertIn('彼女が, 私は, 本を, 学校に', first)
        self.assertIn('Evite a segmentação de quase uma palavra por chunk', first)
        self.assertIn('id="furigana-toggle"', first)
        self.assertIn('id="gloss-export"', first)
        self.assertIn('id="gloss-import"', first)
        self.assertIn('id="gloss-import-file"', first)
        self.assertIn('id="gloss-speak"', first)
        self.assertIn('id="gloss-speak-ja"', first)
        self.assertIn('>▶ JP</button>', first)
        self.assertIn('const glossSpeakJapanese = document.querySelector("#gloss-speak-ja")', first)
        self.assertIn('let markedGlossSpeechMode = null', first)
        self.assertIn('function toggleMarkedGlossSpeech', first)
        self.assertIn('toggleMarkedGlossSpeech(true)', first)
        self.assertIn('markedGlossSpeechMode = japaneseOnly ? "ja" : "full"', first)
        self.assertIn('function currentSentenceListeningGlosses', first)
        self.assertIn('function speakNextMarkedGlossPart', first)
        self.assertIn('new SpeechSynthesisUtterance', first)
        self.assertIn('{ text: term, lang: "ja-JP" }', first)
        self.assertIn('{ text: portuguese, lang: "pt-BR" }', first)
        self.assertIn('window.speechSynthesis.speak(utterance)', first)
        self.assertIn('entry.reasons === undefined ? ["vocabulary"] : entry.reasons', first)
        self.assertIn('reasons: [...new Set(storedReasons)]', first)
        self.assertIn('id="study-count" aria-label="Nenhuma marcação de estudo">★ 0 · 🎧 0 · 📖︎ 0 · 🧩︎ 0', first)
        self.assertIn('function updateStudyCount()', first)
        self.assertIn('total + analysis.checked_entries.length', first)
        self.assertIn('total + analysis.checked_topics.length', first)
        self.assertIn('${vocabularySymbol} ${vocabularyCount} · ${grammarSymbol} ${grammarCount}', first)
        self.assertIn('>▶ Escuta</button>', first)
        self.assertIn('toggleReason("vocabulary")', first)
        self.assertIn('toggleReason("listening")', first)
        self.assertNotIn('function toggleAllGlossReasons', first)
        self.assertIn('id="api-key-button"', first)
        self.assertIn('id="api-key-dialog"', first)
        self.assertIn('id="api-key-remove"', first)
        self.assertIn('simple-ja-books:openai-api-key:v1', first)
        self.assertIn('simple-ja-books:grammar-analyses:v1:', first)
        self.assertIn('const grammarModel = "gpt-6-luna"', first)
        self.assertIn('function grammarAnalysisPrompt', first)
        self.assertIn('Frase completa:', first)
        self.assertIn('Trecho-alvo:', first)
        self.assertIn('https://api.openai.com/v1/responses', first)
        self.assertIn('store: false', first)
        self.assertIn('renderGrammarAnalysis(grammarPanel, stored.analysis, stored, chunkButton)', first)
        self.assertIn('renderGrammarAnalysis(grammarPanel, analysis, entry, chunkButton)', first)
        self.assertIn('function appendGrammarInline', first)
        self.assertIn('function renderGrammarAnalysis', first)
        self.assertIn('document.createElement(strong ? "strong" : "em")', first)
        self.assertIn('const heading = document.createElement("h3")', first)
        self.assertIn('activeList = document.createElement(tagName)', first)
        self.assertIn('function setGrammarTopicChecked', first)
        self.assertIn('checked_topics: [...new Set(checkedTopics)]', first)
        self.assertIn('checked_topics: []', first)
        self.assertIn('topicCheckbox.type = "checkbox"', first)
        self.assertIn('topicCheckbox.checked = checkedTopics.has(currentTopicIndex)', first)
        self.assertIn('setGrammarTopicChecked(entry, currentTopicIndex, topicCheckbox.checked)', first)
        self.assertIn('markChunkGrammarAvailable(chunkButton, entry)', first)
        self.assertIn('chunkButton.dataset.checkedGrammarTopics = String(checkedTopics)', first)
        self.assertIn('hasGrammar ? `${grammarSymbol}✓ ${checkedTopics}` : `${grammarSymbol}＋`', first)
        self.assertIn('? `, ${checkedTopics} ${checkedTopics === 1 ? "tópico marcado" : "tópicos marcados"}`', first)
        self.assertIn('className = "chunk-grammar-topic-content"', first)
        self.assertIn('grammar_analyses: [...grammarAnalyses.values()]', first)
        self.assertIn('id="chunks-tab"', first)
        self.assertIn('id="incremental-tab"', first)
        self.assertIn('id="translation-tab"', first)
        self.assertIn('id="chunks-panel"', first)
        self.assertIn('id="incremental-panel"', first)
        self.assertIn('id="translation-panel"', first)
        self.assertNotIn('id="vocabulary-tab"', first)
        self.assertNotIn('id="sentence-vocabulary"', first)
        self.assertIn('id="vocabulary-confirm-dialog"', first)
        self.assertIn('simple-ja-books:vocabulary-analyses:v3:', first)
        self.assertIn('function vocabularyPrompt', first)
        self.assertIn('function generateVocabularyAnalysis', first)
        self.assertIn('somente do chunk-alvo', first)
        self.assertIn('restaure esse kanji', first)
        self.assertIn('Não restrinja meaning ao sentido especializado', first)
        self.assertIn('significado central e geral do vocábulo', first)
        self.assertIn('type: "json_schema"', first)
        self.assertIn('strict: true', first)
        self.assertIn('dictionary_form: { type: "string" }', first)
        self.assertIn('reading: { type: "string" }', first)
        self.assertIn('jlpt_level: { type: "string", enum: vocabularyJlptLevels }', first)
        self.assertIn('JLPT: ${item.jlpt_level}', first)
        self.assertNotIn('pitch_accent', first)
        self.assertIn('part_of_speech: { type: "string", enum: vocabularyPartsOfSpeech }', first)
        self.assertIn('meaning: { type: "string" }', first)
        self.assertIn('checked_entries: []', first)
        self.assertIn('checkbox.className = "vocabulary-check"', first)
        self.assertIn('appendAlignedRuby(dictionaryForm, item.dictionary_form, item.reading)', first)
        self.assertIn('saveVocabularyAnalyses()', first)
        self.assertIn('function showStoredVocabularyAnalysis', first)
        self.assertIn('async function revealVocabularyAnalysis', first)
        self.assertIn('vocabularyPanel.hidden = !expanded', first)
        self.assertIn('confirmVocabularyGeneration(chunkSurface)', first)
        self.assertIn('vocabulary_analyses: [...vocabularyAnalyses.values()]', first)
        self.assertIn('vocabulario-selecionado.json', first)
        vocabulary_export_block = first[
            first.index('vocabularyExport.addEventListener("click"'):
            first.index('function glossKey')
        ]
        self.assertIn('schema_version: 2', vocabulary_export_block)
        self.assertIn('id="incremental-confirm-dialog"', first)
        self.assertIn('simple-ja-books:incremental-analyses:v2:', first)
        self.assertIn('simple-ja-books:sentence-study-tab:v1:', first)
        self.assertIn('function incrementalPrompt(sentenceIndex)', first)
        self.assertIn('function generateIncrementalAnalysis(sentenceIndex)', first)
        self.assertIn('tradução parcial autêntica do novo chunk', first)
        self.assertIn('Não use metalinguagem', first)
        self.assertIn('algo enorme e aterrorizante...', first)
        self.assertIn('...encarnação do ódio, da vingança e da morte...', first)
        self.assertIn('name: "incremental_reading"', first)
        self.assertIn('required: ["interpretation", "grammar_points"]', first)
        self.assertIn('minItems: stepCount', first)
        self.assertIn('maxItems: stepCount', first)
        self.assertIn('segment: sentence.chunks[index]?.[0]', first)
        self.assertIn('reading: sentence.chunks[index]?.[1]', first)
        self.assertIn('step.segment !== expectedChunks[index][0]', first)
        self.assertIn('steps.map((step) => step.segment).join("") !== entry.sentence_text', first)
        self.assertIn('function renderIncrementalAnalysis(entry, notice = "")', first)
        self.assertIn('className = "incremental-progress-step"', first)
        self.assertIn('"Continuar →"', first)
        self.assertIn('"↺ Recomeçar"', first)
        self.assertIn('appendAlignedRuby(segment, item.segment, item.reading)', first)
        self.assertIn('classList.toggle("is-current-segment", index === stepIndex)', first)
        self.assertIn('grammarHeading.textContent = "Principais pontos gramaticais"', first)
        self.assertIn('function syncIncrementalGrammarAnalyses(entry)', first)
        self.assertIn('renderGrammarAnalysis(grammar, sharedGrammar.analysis, sharedGrammar, null)', first)
        self.assertIn('false,\n        true', first)
        self.assertIn('function setSentenceStudyTab(tab, persist = true)', first)
        self.assertIn('renderIncrementalForActiveSentence()', first)
        self.assertIn('incrementalTab.addEventListener("click", () => setSentenceStudyTab("incremental"))', first)
        self.assertNotIn('if (generate) void revealIncrementalAnalysis(activeIndex)', first)
        self.assertIn('incremental_analyses: [...incrementalAnalyses.values()]', first)
        self.assertIn('saveIncrementalAnalyses()', first)
        self.assertIn('incrementalAnalyses = importedIncrementalAnalyses', first)
        self.assertIn('font-size: 0.9rem;', first)
        self.assertNotIn('grammarPanel.innerHTML', first)
        self.assertIn('function showStoredGrammarAnalysis', first)
        self.assertIn('if (!stored) return false;', first)
        self.assertIn('expanded = true', first)
        self.assertIn('grammarPanel.hidden = !expanded', first)
        self.assertIn('chunkButton.setAttribute("aria-expanded", String(expanded))', first)
        self.assertIn('showStoredGrammarAnalysis(sentence.text, chunkIndex, surface, grammarPanel, chunkButton, false);', first)
        self.assertIn('function confirmGrammarGeneration', first)
        self.assertIn('id="grammar-confirm-dialog"', first)
        self.assertIn('id="grammar-confirm-submit"', first)
        self.assertIn('return new Promise((resolve) => {', first)
        self.assertIn('grammarConfirmDialog.returnValue === "confirm"', first)
        self.assertIn('A frase e o chunk serão enviados à API da OpenAI.', first)
        self.assertIn('generationConfirmed = false', first)
        self.assertIn('if (!generationConfirmed && !await confirmGrammarGeneration(chunkSurface)) return;', first)
        reveal_start = first.index('async function revealGrammarAnalysis')
        confirmation_check = first.index(
            'if (!generationConfirmed && !await confirmGrammarGeneration(chunkSurface)) return;',
            reveal_start,
        )
        self.assertLess(confirmation_check, first.index('if (!openAiApiKey)', reveal_start))
        self.assertLess(
            confirmation_check,
            first.index('const analysis = await generateGrammarAnalysis', reveal_start),
        )
        self.assertIn('chunkButton.dataset.grammarAvailable = "true"', first)
        self.assertNotIn('chunk-grammar-indicator', first)
        self.assertNotIn('grammarIndicator', first)
        self.assertIn('markChunkGrammarAvailable(chunkButton, stored);', first)
        self.assertIn('chunkMain.className = "chunk-main"', first)
        self.assertIn('chunkButton.className = "chunk-action chunk-grammar-toggle"', first)
        self.assertIn('translationButton.className = "chunk-action chunk-translation-toggle"', first)
        self.assertIn('chunkReason.className = "chunk-action chunk-reason"', first)
        self.assertIn('vocabularyButton.className = "chunk-action chunk-vocabulary-toggle"', first)
        self.assertIn('listeningReason.className = "chunk-action chunk-reason"', first)
        self.assertIn('.chunk-reason[aria-pressed="true"] {', first)
        self.assertIn('color: var(--paper);\n      background: var(--accent);', first)
        self.assertNotIn('.chunk[data-vocabulary="true"]', first)
        self.assertNotIn('.chunk[data-listening="true"]', first)
        self.assertNotIn('.chunk:focus-within', first)
        self.assertNotIn('chunk.dataset.vocabulary', first)
        self.assertNotIn('chunk.dataset.listening', first)
        self.assertIn('setChunkActionContent(chunkReason, "★", "Chunk")', first)
        self.assertIn('hasVocabulary ? `${vocabularySymbol}✓ ${checkedEntries}` : `${vocabularySymbol}＋`', first)
        self.assertIn('chunkButton.dataset.checkedVocabularyEntries = String(entry.checked_entries.length)', first)
        self.assertIn('setChunkActionContent(listeningReason, "🎧", "Escuta")', first)
        self.assertIn('chunkButton.dataset.checkedGrammarTopics = String(checkedTopics)', first)
        self.assertIn('setChunkActionContent(translationButton, translationSymbol, "Tradução")', first)
        self.assertIn('const vocabularySymbol = "📖︎"', first)
        self.assertIn('const grammarSymbol = "🧩︎"', first)
        self.assertIn('const translationSymbol = "🌐︎"', first)
        self.assertIn('filter: grayscale(1);', first)
        self.assertIn('grid-template-columns: repeat(5, minmax(0, 1fr));', first)
        self.assertIn('studyActions.append(\n          chunkReason,', first)
        self.assertNotIn('className = "chunk-reasons"', first)
        self.assertIn('setChunkGlossVisibility(chunk, visible)', first)
        self.assertNotIn('chunkButton.className = "chunk-main"', first)
        self.assertIn('grammarAnalysisKey(sentenceText, chunkIndex, chunkSurface),\n          entry', first)
        self.assertNotIn('grammarAnalyses.set(key, entry)', first)
        self.assertIn('void revealGrammarAnalysis(sentence.text, chunkIndex, surface', first)
        self.assertIn('chunkButton.setAttribute("aria-expanded", "false")', first)
        self.assertIn('chunkReason.addEventListener("click", () => toggleReason("vocabulary"))', first)
        self.assertIn('void revealVocabularyAnalysis(', first)
        self.assertIn('listeningReason.addEventListener("click", () => toggleReason("listening"))', first)
        self.assertIn('id="offline-chapter-download"', first)
        self.assertIn('id="offline-book-download"', first)
        self.assertIn('id="offline-manage"', first)
        self.assertIn('id="offline-remove"', first)
        self.assertIn('function downloadOffline', first)
        self.assertIn('function offlineUrlsForChapters', first)
        self.assertIn('navigator.serviceWorker.register(offlineWorkerUrl, {', first)
        self.assertIn('updateViaCache: "none"', first)
        self.assertIn('await cacheOfflineUrls(urls)', first)
        self.assertIn('const offlineVersion = "', first)
        self.assertIn('id="translation-speak"', first)
        self.assertIn('function toggleTranslationSpeech', first)
        self.assertIn('new SpeechSynthesisUtterance(sentences[activeIndex].pt)', first)
        self.assertIn('utterance.lang = "pt-BR"', first)
        self.assertIn('id="sentence-audio-controls"', first)
        self.assertIn('id="sentence-audio-toggle"', first)
        self.assertIn('id="sentence-audio-japanese"', first)
        self.assertIn('>▶ JP + Ouvir</button>', first)
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
        self.assertIn('function startJapaneseGlossesThenSentenceOnce', first)
        self.assertIn('sentenceAudioLoopMode !== "off" || !listeningAvailable', first)
        self.assertIn('japaneseOnly: true', first)
        self.assertIn('loopSequence: true', first)
        self.assertIn('Frase em 0,5 s…', first)
        self.assertIn('Glosses em 0,5 s…', first)
        self.assertIn('Próxima frase em 0,5 s…', first)
        self.assertIn('audioConfig ? new Audio() : null', first)
        self.assertIn('<link rel="manifest" href="../manifest.webmanifest?v=2">', first)
        self.assertIn('<meta name="theme-color" content="#314f46">', first)
        self.assertIn('simple-ja-books:audio-speed:v1:', first)
        self.assertIn('function sentenceAudioPath', first)
        self.assertIn('prepareSentenceAudio(activeChapter, paragraphInChapter, sentenceInParagraph)', first)
        self.assertIn('stopSentenceAudio();', first)
        self.assertIn('simple-ja-books:marked-glosses:v1', first)
        self.assertIn('simple-ja-books:active-card:v1:', first)
        self.assertIn('simple-ja-books:sentence-chapter-positions:v1:', first)
        self.assertIn('function normalizeSentenceChapterPositions', first)
        self.assertIn('function validSentenceChapterPositions', first)
        self.assertIn('sentenceChapterPositions[activeChapterForIndex(activeIndex)] = activeIndex', first)
        self.assertIn('renderCard(sentenceChapterPositions[chapterIndex])', first)
        self.assertIn('saveActiveIndex()', first)
        self.assertIn('renderCard(activeIndex);', first)
        self.assertIn('id="chapter-progress"', first)
        self.assertIn('id="chapter-progress-paragraphs"', first)
        self.assertIn('id="chapter-progress-sentences"', first)
        self.assertIn('>Parágrafos</span>', first)
        self.assertIn('>Frases</span>', first)
        self.assertIn('function renderChapterProgress', first)
        self.assertIn('paragraph.classList.toggle("is-current", paragraphIndex === activeParagraph)', first)
        self.assertIn('sentence.classList.toggle("is-current", offset === sentenceInParagraph)', first)
        self.assertIn('function toggleGlossReason', first)
        self.assertIn('reasons: [...reasons]', first)
        self.assertIn("Exportar dados de leitura em JSON", first)
        self.assertIn("Importar dados de leitura em JSON", first)
        self.assertIn("schema_version: 9", first)
        self.assertIn("reader_state:", first)
        self.assertIn("grammar_analyses: [...grammarAnalyses.values()]", first)
        self.assertIn("active_sentence_index: activeIndex", first)
        self.assertIn("sentence_chapter_positions: sentenceChapterPositions", first)
        self.assertIn("sentence_study_tab: sentenceStudyTab", first)
        self.assertIn("storedSentenceChapterPositions !== undefined", first)
        self.assertIn("positions: readingPositions", first)
        self.assertIn("dados-de-leitura.json", first)
        self.assertIn("[1, 2, 3, 4, 5, 6, 7, 8, 9].includes(payload?.schema_version)", first)
        self.assertIn("[2, 3, 4, 5, 6, 7, 8, 9].includes(payload.schema_version)", first)
        self.assertIn("[4, 5, 6, 7, 8, 9].includes(payload.schema_version)", first)
        self.assertIn("[6, 7, 8, 9].includes(payload.schema_version)", first)
        self.assertIn("payload.schema_version === 9", first)
        self.assertIn("saveGrammarAnalyses()", first)
        export_block = first[
            first.index('glossExport.addEventListener("click"'):
            first.index('glossImport.addEventListener("click"')
        ]
        self.assertNotIn("openAiApiKey", export_block)
        self.assertIn("simple-ja-books:furigana-visible:v1:", first)
        self.assertIn("renderCard(activeIndex - 1)", first)
        self.assertIn("renderCard(activeIndex + 1)", first)
        self.assertIn("paragraphSentenceStarts[activeParagraph - 1]", first)
        self.assertIn("paragraphSentenceStarts[activeParagraph + 1]", first)
        self.assertIn("touch-action: pan-y", first)
        self.assertIn('id="chunk-gloss-toggle"', first)
        self.assertIn('let chunkGlossesVisible = false', first)
        self.assertIn('gloss.classList.toggle("is-concealed", !visible)', first)
        self.assertIn('meaning.className = "gloss is-concealed"', first)
        self.assertIn('meaning.setAttribute("aria-hidden", "true")', first)
        self.assertIn('.gloss.is-concealed {', first)
        self.assertIn('visibility: hidden;', first)
        self.assertNotIn('gloss.hidden = !chunkGlossesVisible', first)
        self.assertIn('? "Ocultar traduções"', first)
        self.assertIn(': "Mostrar traduções"', first)
        self.assertIn('panel.addEventListener("pointerdown"', first)
        self.assertIn('panel.addEventListener("pointerup"', first)
        self.assertIn("suppressClickAfterSwipe", first)
        self.assertIn("showPreviousSentence()", first)
        self.assertIn("showNextSentence()", first)
        self.assertIn('aria-label="Alternar furigana"', first)
        self.assertIn('id="sentence-copy"', first)
        self.assertIn('>⧉ Copiar</button>', first)
        self.assertIn('const sentenceCopy = document.querySelector("#sentence-copy")', first)
        self.assertIn('navigator.clipboard?.writeText', first)
        self.assertIn('document.execCommand("copy")', first)
        self.assertIn('const sentenceText = sentences[activeIndex]?.text', first)
        self.assertIn('sentenceCopy.addEventListener("click", copyActiveSentence)', first)
        self.assertIn('copied ? "✓ Copiado" : "Não copiado"', first)
        self.assertIn("grid-template-columns: minmax(0, 1fr);", first)
        self.assertIn("justify-self: end;", first)
        self.assertIn(".selected-sentence {\n        grid-row: 2;\n        width: 100%;", first)
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
            first.index('id="chunk-gloss-toggle"'),
        )
        self.assertLess(
            first.index('id="chunk-gloss-toggle"'),
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
        self.assertLess(
            first.index('id="chapter-progress"'),
            first.index('id="chunks-tab"'),
        )
        self.assertLess(
            first.index('id="chunks-tab"'),
            first.index('id="chunks-panel"'),
        )
        self.assertLess(
            first.index('id="incremental-tab"'),
            first.index('id="translation-tab"'),
        )
        self.assertLess(
            first.index('id="incremental-panel"'),
            first.index('id="translation-panel"'),
        )
        self.assertIn('setSentenceStudyTab(sentenceStudyTab, false)', first)
        self.assertIn('current_step: currentStep', first)
        self.assertIn('localStorage.setItem(sentenceStudyTabStorageKey, sentenceStudyTab)', first)

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

    def test_editable_book_may_start_without_chapters_or_paragraphs(self) -> None:
        editable = json.loads(
            (ROOT / "texts" / "rpg-ja.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertTrue(
            build_reader.validate_data(copy.deepcopy(editable))["page"]["editable"]
        )

        editable["chapters"] = [{"title": "Capítulo 1", "paragraphs": []}]
        validated = build_reader.validate_data(editable)
        self.assertEqual(validated["chapters"][0]["paragraphs"], [])

    def test_noneditable_book_requires_content(self) -> None:
        data = copy.deepcopy(self.data)
        data["chapters"] = []
        with self.assertRaisesRegex(build_reader.BuildError, "editable book"):
            build_reader.validate_data(data)

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
        self.assertIn('request.mode === "navigate"', worker)
        self.assertIn('self.registration.scope', worker)
        self.assertIn('const PWA_CACHE_PREFIX', worker)
        self.assertIn('const PWA_CACHE_NAME = `${PWA_CACHE_PREFIX}v9`', worker)
        self.assertIn('const PWA_SHELL_URLS', worker)
        self.assertIn('cache.addAll(PWA_SHELL_URLS)', worker)
        self.assertIn('name.startsWith(PWA_CACHE_PREFIX)', worker)
        for icon_url in (
            '"./icons/icon-32.png?v=2"',
            '"./icons/icon-180.png?v=2"',
            '"./icons/icon-192.png?v=2"',
            '"./icons/icon-512.png?v=2"',
            '"./icons/icon-maskable-512.png?v=2"',
            '"./icons/icon.svg?v=2"',
        ):
            self.assertIn(icon_url, worker)

    def test_pwa_manifest_icons_and_library_registration(self) -> None:
        manifest = json.loads(
            (ROOT / "site" / "manifest.webmanifest").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["id"], "./")
        self.assertEqual(manifest["start_url"], "./")
        self.assertEqual(manifest["scope"], "./")
        self.assertEqual(manifest["display"], "standalone")
        icon_declarations = [
            (icon["src"], icon["sizes"], icon["purpose"])
            for icon in manifest["icons"]
        ]
        self.assertIn(("icons/icon-192.png?v=2", "192x192", "any"), icon_declarations)
        self.assertIn(("icons/icon-maskable-512.png?v=2", "512x512", "maskable"), icon_declarations)
        self.assertEqual(len(manifest["shortcuts"]), 3)

        library = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<link rel="manifest" href="manifest.webmanifest?v=2">', library)
        self.assertIn('href="icons/icon.svg?v=2" type="image/svg+xml"', library)
        self.assertIn('href="icons/icon-32.png?v=2" sizes="32x32"', library)
        self.assertIn('href="icons/icon-180.png?v=2" sizes="180x180"', library)
        self.assertIn('navigator.serviceWorker.register("offline-sw.js", { updateViaCache: "none" })', library)
        self.assertIn('id="install-pwa"', library)
        self.assertIn('src="icons/icon-192.png?v=2"', library)
        self.assertIn('href="rpg/"', library)
        self.assertIn('>RPG<', library)

        worker = (ROOT / "site" / "offline-sw.js").read_text(encoding="utf-8")
        for shell_url in (
            '"./"',
            '"./index.html"',
            '"./princess-of-mars/"',
            '"./books/princess-of-mars-ja.json"',
            '"./mary-beard-spqr/"',
            '"./books/mary-beard-spqr-ja.json"',
            '"./rpg/"',
            '"./books/rpg-ja.json"',
        ):
            self.assertIn(shell_url, worker)

        for filename, expected_size in (
            ("icon-32.png", 32),
            ("icon-180.png", 180),
            ("icon-192.png", 192),
            ("icon-512.png", 512),
            ("icon-maskable-512.png", 512),
        ):
            payload = (ROOT / "site" / "icons" / filename).read_bytes()
            self.assertEqual(payload[:8], b"\x89PNG\r\n\x1a\n")
            self.assertEqual(struct.unpack(">II", payload[16:24]), (expected_size, expected_size))

        for required in (
            '"../index.html"',
            '"../manifest.webmanifest?v=2"',
            '"../icons/icon-32.png?v=2"',
            '"../icons/icon-180.png?v=2"',
            '"../icons/icon-192.png?v=2"',
            '"../icons/icon-512.png?v=2"',
            '"../icons/icon-maskable-512.png?v=2"',
            '"../icons/icon.svg?v=2"',
            'updateViaCache: "none"',
            "await registration.update()",
        ):
            self.assertIn(required, self.template)

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
