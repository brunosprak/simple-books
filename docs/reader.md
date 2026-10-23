# Reader Functional Specification

This document defines the user-visible behavior and compatibility requirements of the static Japanese text reader. Implementation guidance for agents belongs in `AGENTS.md`; reader product rules belong here and should be enforced by automated tests wherever practical. A book is one document kind, not the reader's domain model.

## Generic document model

- The normalized hierarchy is `Document → Section → Passage → Sentence → Chunk`. It is shared by books, game scripts, film scripts, articles, transcripts and future text kinds.
- `kind` describes the document (`book`, `game_script`, `article`, `screenplay`, and so on) without changing reading behavior. `labels` supplies user-facing names for sections and passages, so the same controls can say `Capítulo`/`Parágrafo`, `Cena`/`Fala`, or another appropriate pair.
- Every entity in schema version 3 has a stable `id`. Browser content, study state and future annotations are scoped by the document ID rather than by a book filename.
- `capabilities` enables optional behavior independently: editing, audio and incremental reading are document capabilities rather than assumptions tied to a book.
- Legacy schema version 2 book JSON remains accepted through the adapter in `site/modules/document-model.js`. New non-book documents use schema version 3. The complete schema and migration rules are in `docs/document-model.md`.

## Current book content

`A Princess of Mars` has 28 source chapters. Chapters 1 through 16 are currently translated in full, comprising 529 source paragraphs and 1,701 Japanese sentence cards. Every translated card has a matching pre-generated Nise MP3. The canonical content is `texts/princess-of-mars-ja.json`; the public JSON and reader HTML are generated from it.

## Generated architecture

- `texts/<document-slug>-ja.json` is the canonical document and study data.
- `site/books/<document-slug>-ja.json` is its generated public copy. The directory retains its historical name for URL compatibility.
- `site/<document-slug>/index.html` is generated from the shared `site/reader.template.html` and loads the public JSON at runtime.
- `site/modules/document-model.js` normalizes v2 books and v3 documents; `storage.js` provides namespaced persistence; `openai-client.js` owns Responses API transport, timeout and bounded error handling.
- Optional `page.audio` metadata enables sentence audio for a book and defines its base URL, voice label, allowed playback speeds, and default speed.
- `site/<book-slug>/audio/` contains generated MP3 files and their manifest when audio is enabled.
- A translation-only change may update the public JSON without changing the generated HTML bytes.

## Editable documents

- The library includes `RPG`, an initially empty `game_script` document whose canonical schema-v3 JSON enables `capabilities.editing`. An editable document may begin without sections, and a section may temporarily contain no passages.
- Its construction panel always remains available. The add-section and passage-management controls are collapsed curtains by default and use the labels declared by the document. The reader can add a locally named section without an API request, then choose it and submit one Japanese passage at a time.
- Adding a paragraph explicitly calls the OpenAI Responses API and may incur charges. It uses a strict Structured Outputs schema to request only sentence and chunk boundary indexes plus readings, concise Portuguese glosses, and each sentence's natural Portuguese translation. The API never supplies the Japanese text that is stored: the browser slices every sentence and chunk directly from the submitted paragraph, making the original Japanese immutable.
- The paragraph curtain reports progress, success, validation failures, connection failures, API status and the API's bounded error detail immediately below the generation button. While a request is active, the button reads `Gerando…`; a two-minute timeout restores the form with an actionable message instead of leaving it apparently inert.
- The browser accepts the generated paragraph only when the boundary indexes are increasing, contiguous, cover the submitted paragraph exactly, every sentence is nonempty, every chunk is valid, and no chunk consists only of punctuation. Leading and trailing characters from the textarea are retained instead of being trimmed. A failed request or validation does not partially alter the book.
- Sections and generated passages are stored in `localStorage`, scoped to the document ID. They are personal browser data and are not written back to the static public JSON. `Exportar documento` downloads the complete generic schema-v3 document; `Importar documento` restores compatible editable content in another browser.
- `Gerenciar parágrafos` also lists every saved paragraph with its chapter, ordinal, and text preview. Deleting the selected paragraph requires confirmation, removes only that paragraph, resets stale navigation positions, and removes or reindexes sentence-indexed incremental analyses while preserving unrelated chapter content.
- RPG has no sentence audio and hides offline-document download controls. As soon as it contains a generated passage, it exposes the same reading modes, chunks, incremental reading, translation, study marking, backup and API-assisted analyses as any other document.

## Reading modes

The mode selector appears in the normal document flow and exposes three modes.

### Frases

- Shows one Japanese sentence at a time. Sentence and passage navigation plus section progress are shared by three content tabs immediately below them: `Chunks`, `Leitura incremental`, and `Tradução`. The selected tab persists per document.
- `Chunks` is the default and preserves the established sentence experience: furigana, interlinear chunks, concise Portuguese glosses, audio and study actions. The full Portuguese sentence translation and its speech control appear in `Tradução`.
- In `Chunks`, a `Copiar` control adjacent to the main Japanese text copies only the complete active sentence, without furigana readings or the gray preview of the following sentence, and briefly confirms success or failure. On narrow screens it occupies a compact row above the sentence so the Japanese text retains the full reader width.
- Chunk glosses in Portuguese start visually hidden whenever the reader is opened, but their layout space is always reserved so chunks and surrounding text never move when translations are shown or hidden. Every chunk has a `🌐 Tradução` action in its five-button study bar that reveals or conceals only that chunk; its highlighted state indicates that the translation is visible. The `Mostrar traduções` control immediately above the chunks reveals all glosses in the current and subsequent sentence cards for the rest of that page session; while visible, it becomes `Ocultar traduções`.
- Sentence/paragraph navigation and chapter progress appear in the normal document flow above all three tabs. The gloss import/export row remains inside `Chunks` before its sentence content.
- Previous and next controls move by sentence.
- When the current book declares audio metadata, a play/pause control and playback-speed selector appear for the active sentence inside `Chunks`. Books without audio metadata do not show an inactive player.
- `−¶` and `＋¶` move to the previous or next paragraph.
- The paragraph counter is relative to the current chapter, while the sentence counter is relative to the current paragraph.
- A compact chapter progress indicator advances sentence by sentence and shows the percentage of sentence cards reached in the chapter.
- Its upper row, labelled `Parágrafos`, contains one equal-width segment for every paragraph in the current chapter. Earlier paragraphs are shown as completed, the current paragraph is highlighted, and later paragraphs remain inactive.
- Its lower row, labelled `Frases`, contains one equal-width segment for every sentence in the current paragraph. Earlier sentences are shown as completed, the current sentence is highlighted, and later sentences remain inactive. This row is rebuilt when paragraph navigation changes the active paragraph.
- The progress indicator's accessible value reports both the current sentence's position in the chapter and its position within the current paragraph.
- A horizontal swipe moves by sentence.
- The Japanese sentence has a first-line indent only when it is the first sentence of a paragraph.
- Except on the last sentence of a paragraph, the beginning of the following sentence appears in gray after the current sentence only when it fits in the remaining space on the same final line. The preview never wraps, clips a character, or becomes part of the accessible sentence content.
- The last sentence ends without an added paragraph marker or a separate end-of-paragraph label.

#### Leitura incremental

- Opening `Leitura incremental` for a sentence with no saved analysis does not start generation or open a confirmation dialog. The empty tab shows `Gerar leitura incremental`; only pressing that button asks for confirmation before sending the sentence and up to two preceding Japanese sentences to the OpenAI Responses API. A missing API key opens the existing key dialog after confirmation, and failures remain confined to this tab with a retry action.
- The response uses a strict Structured Outputs JSON schema. Every existing interlinear chunk is exactly one incremental step, in the same order: the model does not choose a second segmentation, and the browser supplies each step's Japanese surface and reading directly from the canonical chunk data.
- A saved analysis opens without another request. Navigating to a sentence without an analysis while the tab remains selected shows the explicit generation action rather than silently incurring an API charge.
- Each step contains its corresponding chunk, the canonical chunk reading, a cumulative Portuguese interpretation of every chunk revealed through that step, and zero to five grammar points relevant to processing the newly revealed chunk. The interpretation must read as authentic translated prose, never as metalinguistic commentary about a referent, description, or still-open structure. It is regenerated as a whole at every step and may reorganize or correct its earlier provisional wording when a new Japanese element clarifies the syntax. It must not anticipate hidden information. An incomplete prefix may end with ellipses and may use a minimal generic noun or pronoun implicit in the Japanese—such as `algo`, `alguém`, `uma coisa`, or `um ser`—without inventing a specific identity or fact. The final step is a natural translation of the complete sentence, preserving a deliberately suspended ending when present.
- For example, the successive prefixes `地層を`, `地層を調査したい`, `地層を調査したいエリアが`, and `地層を調査したいエリアが何箇所かあるんだけど……` may be rendered as `As camadas geológicas...`, `Quero investigar as camadas geológicas...`, `Há áreas nas quais quero investigar as camadas geológicas...`, and `Há alguns lugares onde quero investigar as camadas geológicas, mas...`. This progression illustrates that later steps repeat the accumulated meaning while revising Portuguese word order naturally.
- The current card displays, in order, the sentence and step identifiers with a `Regenerar` action, a clickable segmented progress bar, `Anterior` and `Continuar` controls (`Recomeçar` on the final step), accumulated Japanese with furigana, the current chunk interpretation, and `Principais pontos gramaticais`. The newly revealed chunk is visually distinguished from all earlier chunks. It never displays memory-management sections or per-point expansion controls.
- Progress-bar segments can jump directly to any step. Moving between steps updates Japanese, interpretation and grammar together without changing word order or revealing later segments.
- Entering the incremental tab enables furigana so kanji readings are immediately visible. Furigana and font-size controls remain shared with `Chunks`, and clicking or activating the incremental Japanese text toggles furigana normally afterward.
- Grammar points generated for an incremental step are the same saved analysis used by its corresponding chunk in `Chunks`. Their checkboxes and checked state are shared across both views, and the grammar total counts each selected point only once. Regenerating requires confirmation, replaces the saved incremental analysis only after a successful response, and refreshes the shared chunk grammar; a failure leaves the previous saved analysis available. Analyses saved before cumulative interpretations were introduced remain untouched and require `Regenerar` to adopt the cumulative format.
- The generated analysis and the zero-based current step persist per sentence and per document in browser storage and in version 9 reader backups.

### Corrido

- Shows the entire current chapter as continuous Japanese prose.
- Preserves paragraph breaks but does not show chunks, interlinear glosses, or Portuguese translations.
- Swiping to the right changes to `Frases`; swiping to the left changes to `Vertical`.
- Previous and next chapter controls remain available without gestures.

### Vertical

- Shows the entire current chapter using Japanese vertical writing.
- Preserves the same content and paragraph structure as `Corrido`.
- The vertical columns are divided into viewport-sized pages instead of exposing free horizontal scrolling.
- Page boundaries always fall between complete vertical columns, with a one-column edge gutter preventing base text or furigana from being clipped or divided between pages.
- Swiping the text to the right or pressing the right arrow advances to the next page; the opposite directions return to the previous page.
- The upper toolbar places the next-chapter control on the left and the previous-chapter control on the right.
- The controls below the text place the next-page control on the left and the previous-page control on the right.
- Chapter-swipe gestures are limited to the toolbar so they do not conflict with page-turn gestures.

## Furigana and font size

- Clicking or activating Japanese text toggles furigana in every mode.
- The explicit furigana control and the Japanese text remain synchronized.
- Furigana visibility persists per document across mode changes and page reloads.
- The font-size controls appear at the end of the reader content, immediately before the page footer.
- Font-size controls affect Japanese text in all three modes.
- The selected font level survives mode changes and page reloads and is currently shared across readers.

## Position and navigation persistence

Each mode keeps an independent reading position:

- `Frases`: the most recently read sentence in every chapter; selecting a chapter restores its last sentence and paragraph instead of returning to the beginning.
- `Corrido`: current chapter and vertical page position.
- `Vertical`: current chapter, page position, and vertical-writing page number.

Switching modes restores the last position used in the destination mode. Switching sections in `Frases` restores that section's last sentence, including after a page reload. Reloading the page restores the active mode and that mode's saved position. Sentence and section positions are scoped to the current document; the active mode is currently shared across readers.

## Paragraphs and chunks

- Source paragraph boundaries remain visible in all reading modes.
- A chunk represents a lexical or grammatical study unit and never consists only of punctuation.
- Particles are not standalone chunks. Case, topic, quotation, and similar particles attach to the preceding word or short phrase whose role they mark, such as `彼女が`, `本を`, and `学校に`; compact inflectional and auxiliary material likewise remains with its predicate when splitting it would create merely morphological fragments.
- Adjacent or sentence-final punctuation belongs to the preceding chunk's surface and reading. It does not receive a separate gloss.
- The ordered concatenation of chunk surfaces, allowing only deliberately uncovered formatting gaps accepted by the validator, reproduces the Japanese sentence text.

## Sentence audio

- Audio is optional per book and is generated ahead of time; the browser never calls a speech-synthesis service.
- One MP3 maps to exactly one sentence through one-based chapter, paragraph, and sentence numbers. The runtime path is `audio/chapter-XX/paragraph-XXX/sentence-XXX.mp3` relative to the book reader.
- The player is available only in `Frases` and never starts automatically.
- `▶ Ouvir` alternates between play and pause, resuming from the paused position.
- With the loop disabled and at least one listening-marked gloss in the current sentence, `▶ JP + Ouvir` reads every marked Japanese surface once, waits 500 ms, and then plays the sentence MP3 once. It does not enable or repeat a loop.
- `↺ Início` immediately seeks to the beginning and plays, whether the sentence was paused or already playing.
- `↻ Loop` offers `Desligado`, `Frase`, `Glosses + frase`, `Glosses JP + frase`, `Tradução + frase`, `Parágrafo`, `Glosses + parágrafo`, `Glosses JP + parágrafo`, and `Tradução + parágrafo`. `Frase` repeats the current MP3. `Glosses + frase` reads every listening-marked gloss as Japanese, Portuguese, then Japanese before the sentence MP3; `Glosses JP + frase` reads each marked Japanese surface once before that MP3. `Tradução + frase` reads the full Portuguese translation before the current Japanese MP3 and repeats that pair without leaving the sentence. `Parágrafo` plays each sentence once in order, then wraps from the last sentence back to the first sentence of that same paragraph. The three paragraph variants follow this bounded traversal and precede each sentence with, respectively, the full gloss sequence, Japanese-only glosses, or the Portuguese translation; sentences without listening glosses go directly to the MP3. Every transition between a completed phase and the next phase waits 500 ms, while the first phase starts immediately. Gloss and translation modes require browser speech synthesis; gloss modes also require relevant listening marks. Navigating away, leaving `Frases`, or changing the loop mode cancels a pending phase.
- Navigating to another sentence or leaving `Frases` stops playback and returns it to the beginning.
- The selectable speeds come from the book metadata. Changing speed updates the current playback immediately without selecting or generating another MP3.
- Playback speed persists per book. The generated source remains at `1.0×`, and the browser preserves pitch while changing playback rate where supported.
- Loading and playback failures remain local to the player and do not block reading or navigation.
- Voice generation, manifest verification, storage layout, and the audio roadmap are specified in `docs/audio.md`.

## Marked glosses

- Each interlinear chunk has two independent reasons: `★` for a chunk the reader wants to retain and `🎧` for a chunk that was difficult to recognize in sentence audio. A gloss may have either reason, both, or neither.
- Every chunk ends with one uniform five-button study bar: `★ Chunk`, `🎧 Escuta`, `📖＋/✓ Vocabulário`, `🧩＋/✓ Gramática`, and `🌐 Tradução`. The three latter symbols request monochrome text presentation and inherit the button's dark or light foreground instead of using attention-grabbing emoji colors. Chunk and listening marks toggle independently, and only their active buttons are highlighted; marking either reason does not change the chunk card's background or border. The Japanese body is not an implicit control.
- The compact summary displays global per-book totals as `★ chunks · 🎧 listening · 📖 checked vocabulary · 🧩 checked grammar topics`. Its vocabulary and grammar symbols use the same monochrome presentation. All four totals update immediately when their corresponding marks change and are restored from saved or imported data.
- Marked glosses persist in browser storage and are included in exported reader data with a `reasons` array.
- Stored or imported glosses without `reasons` are treated as `vocabulary`, preserving all marks created before the two-reason model.
- When at least one gloss in the current sentence has `🎧` and the browser supports the Web Speech API, `▶ Escuta` reads only those glosses in sentence order. For each gloss it reads Japanese, Portuguese, and Japanese again, using separate language settings. The adjacent `▶ JP` control reads each of the same glosses once, only in Japanese. Pressing the active control again stops its sequence; selecting the other control switches sequences.
- Browser-synthesized gloss speech is an optional convenience and is separate from the pinned Nise sentence MP3s; voice quality and availability depend on the operating system and browser.
- `▶ PT`, beside the full Portuguese translation at the end of the sentence card, reads only that translation with the browser's `pt-BR` speech synthesis. While active it becomes `■ PT`; pressing it again stops playback. Starting sentence audio, gloss speech, navigation, or another reading mode also stops it.

## On-demand vocabulary lists

- `★ Chunk` is the manual, no-API shortcut formerly labelled `★ Palavra`. It marks the original chunk together with its existing Portuguese gloss and remains independent from generated vocabulary.
- Every chunk has a separate `Vocabulário` action. Its first activation asks for confirmation and then sends the target chunk plus the complete sentence as context to the OpenAI Responses API. The result includes lexical material only from that chunk, ignores particles and other function words, and includes only nouns, dictionary-form verbs, dictionary-form い and な adjectives, adverbs, and idiomatic expressions. Before generation the button shows `📖＋`; afterward its own icon becomes `📖✓ N`, where `N` is the number of checked vocabulary entries, including zero. A saved result opens immediately without another request or confirmation.
- Every generated entry has its common modern dictionary spelling. If the source writes in kana a word normally written with common kanji, the generated form restores that kanji; kana remains when it is the normal or predominant modern spelling. When the dictionary form contains kanji, its hiragana reading appears directly above it as furigana and is also retained as a separate data field. The entry additionally has a best-effort JLPT estimate (`N5`, `N4`, `N3`, `N2`, `N1`, or `Acima de N1`), a part of speech, and a concise Portuguese meaning. Pitch accent is neither requested nor stored.
- The sentence context is used only to identify and disambiguate the lexeme. The Portuguese meaning represents the word's central, general meaning across contexts rather than narrowing it to a specialized, technical, figurative, or incidental use in the current sentence. It should preferably contain one word and never more than two.
- The response uses a strict Structured Outputs JSON schema and is validated again in the browser before being stored. Entries have independent checkboxes, and generated chunk analyses and checked entries persist per document in browser storage.
- `↓ Vocabulário` downloads `vocabulario-selecionado.json`, containing only the unique checked entries from all generated lists and only their five vocabulary fields, inside a version 2 vocabulary-export envelope. In version 2, `jlpt_level` replaces the former pitch-accent field.

## On-demand grammar analyses

- Every interlinear chunk has an explicit `Gramática` action in the same study bar as the other four actions. Its icon is `🧩＋` before generation and `🧩✓ N` when a saved analysis exists, where `N` is the number of checked grammar topics, including zero; its highlighted state indicates that the analysis is open. Activating it without saved data asks for confirmation before making a request to the OpenAI Responses API. Canceling the confirmation performs no request and does not open the API-key dialog. Collapsing an analysis does not delete it.
- The request uses `gpt-6-luna` with the complete Japanese sentence as syntactic context and the selected chunk as the target. The prompt asks for two to four concise, nonredundant grammar points in Portuguese and prevents an unnecessary full-sentence translation.
- While a request is running, the chunk shows a loading message and prevents a duplicate request. Failures remain local to the chunk and can be retried.
- Successful responses are rendered below the chunk with a larger font and a safe Markdown subset for headings, numbered or bulleted lists, bold, and emphasis. The renderer creates text and DOM elements directly and never inserts model output as executable HTML. Saved analyses start collapsed; their generated state and checked count remain visible on the `Gramática` button itself. Analyses persist per document in browser storage, and reopening one never requires another API call, confirmation, or configured key.
- Every numbered or bulleted grammar topic has an independent checkbox. Newly generated and legacy topics start unchecked; checking or unchecking one updates browser storage and the button count immediately without affecting the chunk's vocabulary or listening marks. The count is restored after navigation, reload, or import.
- The top-level `🔑 API` control opens a dialog for saving, replacing, or deleting the reader's OpenAI API key. The key is stored in `localStorage`, sent directly from the browser to OpenAI, shared by readers on the same origin, and never added to backups, generated files, logs, or book data.
- The key dialog warns that browser-side secret storage can be read by other scripts on the same origin and that API use may incur charges. After grammar, vocabulary, or incremental-reading generation is confirmed, a missing key opens this dialog and resumes that request after a key is saved without asking for the same confirmation twice.

## Import and export

The reader downloads its backup as `dados-de-leitura.json`.

### Backup schema version 9

Version 9 contains:

- `document_id`, identifying new exports, plus `source_file` for backward compatibility;
- export timestamp;
- marked glosses with one or both reasons (`vocabulary`, `listening`);
- saved grammar analyses, identified by the complete sentence text, chunk index, and chunk surface, including the zero-based indexes of checked topics in `checked_topics`;
- saved vocabulary analyses, identified by complete sentence text, chunk index, and chunk surface, including normalized entries and the zero-based indexes of checked entries in `checked_entries`;
- saved incremental analyses, identified by sentence index and exact sentence text, including ordered steps and the zero-based current step in `current_step`;
- active reading mode;
- active sentence-content tab (`chunks`, `incremental`, or `translation`);
- active sentence index;
- the most recently read sentence index for every chapter;
- font level;
- furigana visibility;
- the independent positions for `Frases`, `Corrido`, and `Vertical`.

Version 9 reader state and all three analysis collections may be applied only when `document_id`, when present, and `source_file` match the currently open document. Importing a version 9 backup replaces grammar, vocabulary, and incremental analyses for that document. The API key is deliberately excluded. The complete payload is validated before any gloss, analysis, or reader state is changed, so a failed import is atomic.
Grammar analyses exported before topic marking existed remain valid: a missing `checked_topics` field is normalized to an empty list, so every imported topic begins unchecked.

### Legacy compatibility

The importer continues to accept schema versions 1 through 8. Version 1 updates glosses without replacing reader positions or preferences; versions 2 and 3 retain their reader state. Versions 4 and 5 replace grammar analyses. Version 5 sentence-level vocabulary lists are deliberately not imported into the new per-chunk format, so existing per-chunk vocabulary remains unchanged. Version 6 replaces grammar and per-chunk vocabulary analyses but leaves incremental analyses and the selected sentence-content tab unchanged. Version 7 incremental analyses whose old model-selected segmentation does not exactly match the canonical chunks are discarded during import; its other valid data is preserved. Version 8 vocabulary entries still carrying pitch accent have no trustworthy JLPT replacement and are discarded during import, while its other valid data is preserved. Earlier versions likewise leave unsupported newer analysis collections unchanged. Backups made before per-chapter sentence positions existed remain valid: their single active sentence is retained and other chapters begin at their first sentence. In any legacy version, every gloss without a `reasons` field is migrated to `reasons: ["vocabulary"]`.

## Offline reading

- The site is an installable PWA with a web app manifest, dedicated favicon and Apple touch assets, visible 192 px and 512 px install icons, a separate maskable icon, standalone display, theme colors, and a root-scoped Service Worker. Icon URLs are versioned so browsers and installed applications can detect replacements instead of indefinitely reusing stale metadata or images. The library exposes an installation button; when a programmatic prompt is unavailable, it directs the reader to the browser’s “Install” or “Add to Home Screen” action.
- Installing the PWA caches only the application shell: the library page, every available reader and public book JSON, the manifest, and icons. Sentence MP3s remain opt-in through the chapter and full-book download controls, avoiding an automatic download of the complete audio collection.
- The installed app starts at the library page, where every available book can be selected.
- Service Worker registration bypasses the HTTP cache when checking for an update. A new shell version replaces obsolete PWA shell caches, and an offline navigation that has no exact cached page falls back to the cached library rather than a browser error page.
- The final page section exposes `↓ Capítulo atual`, `↓ Livro completo`, and `Gerenciar` controls when Service Worker and Cache Storage APIs are available.
- A chapter download stores the current reader page, public book JSON, offline worker, audio manifest, and every sentence MP3 in the selected chapter. A full-book download stores the same shell plus every chapter MP3 and the library page.
- Download progress is announced and shown visually. A scope is marked available only after every required file has been cached successfully; interrupted downloads remain retryable.
- Offline files are versioned from the canonical public JSON and shared reader template. When a version changes, the controls mark previously saved chapters as needing an update. An update always refreshes the HTML, public JSON, worker, and manifest, while unchanged MP3s are copied from the prior cache only when voice, encoding, text hash, and byte size still match. Old caches remain available until every previously saved chapter has been migrated; completing the migration or updating the whole book removes them.
- The current chapter follows the active chapter in all reading modes. Downloaded chapters and full-book state persist per book in the current browser.
- `Gerenciar` reports origin-level browser storage usage and can remove every offline cache for the current book. Removing offline files does not remove reading position, gloss marks, or other reader preferences.
- Browser speech voices are not site assets and may remain unavailable offline. Pre-generated sentence MP3s continue to work.

## Accessibility and interaction

- All reader controls and navigation sections remain in the normal document flow. No reader element uses `position: sticky` or `position: fixed` to remain suspended while the page scrolls.
- Controls use descriptive accessible names and expose pressed or disabled state where applicable.
- Keyboard activation works for furigana toggles and interactive Japanese text.
- Touch gestures do not suppress ordinary vertical page scrolling.
- A swipe does not also trigger the click action that toggles furigana.

## Regression expectations

Changes to the reader preserve all rules above. Update automated tests with behavior changes, run the generated-output checks for every book affected by the shared template, and perform local browser verification for gesture, scrolling, persistence, or import/export changes when practical.
