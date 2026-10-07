# Reader Functional Specification

This document defines the user-visible behavior and compatibility requirements of the static Japanese reader. Implementation guidance for agents belongs in `AGENTS.md`; reader product rules belong here and should be enforced by automated tests wherever practical.

## Current book content

`A Princess of Mars` has 28 source chapters. Chapters 1 through 4 are currently translated in full, comprising 122 source paragraphs and 462 Japanese sentence cards. The canonical content is `texts/princess-of-mars-ja.json`; the public JSON and reader HTML are generated from it.

## Generated architecture

- `texts/<book-slug>-ja.json` is the canonical book and study data.
- `site/books/<book-slug>-ja.json` is its generated public copy.
- `site/<book-slug>/index.html` is generated from the shared `site/reader.template.html` and loads the public JSON at runtime.
- Optional `page.audio` metadata enables sentence audio for a book and defines its base URL, voice label, allowed playback speeds, and default speed.
- `site/<book-slug>/audio/` contains generated MP3 files and their manifest when audio is enabled.
- A translation-only change may update the public JSON without changing the generated HTML bytes.

## Reading modes

The mode selector appears in the normal document flow and exposes three modes.

### Frases

- Shows one Japanese sentence at a time with furigana, interlinear chunks, concise Portuguese glosses, and the full Portuguese translation.
- The sentence/paragraph navigation and gloss import/export row appear in the normal document flow before the sentence content.
- Previous and next controls move by sentence.
- When the current book declares audio metadata, a play/pause control and playback-speed selector appear for the active sentence. Books without audio metadata do not show an inactive player.
- `−¶` and `＋¶` move to the previous or next paragraph.
- The paragraph counter is relative to the current chapter, while the sentence counter is relative to the current paragraph.
- A horizontal swipe moves by sentence.
- The Japanese sentence has a first-line indent only when it is the first sentence of a paragraph.
- Except on the last sentence of a paragraph, the beginning of the following sentence appears in gray after the current sentence only when it fits in the remaining space on the same final line. The preview never wraps, clips a character, or becomes part of the accessible sentence content.
- The last sentence ends without an added paragraph marker or a separate end-of-paragraph label.

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
- Furigana visibility persists per book across mode changes and page reloads.
- The font-size controls appear at the end of the reader content, immediately before the page footer.
- Font-size controls affect Japanese text in all three modes.
- The selected font level survives mode changes and page reloads and is currently shared across readers.

## Position and navigation persistence

Each mode keeps an independent reading position:

- `Frases`: the most recently read sentence in every chapter; selecting a chapter restores its last sentence and paragraph instead of returning to the beginning.
- `Corrido`: current chapter and vertical page position.
- `Vertical`: current chapter, page position, and vertical-writing page number.

Switching modes restores the last position used in the destination mode. Switching chapters in `Frases` restores that chapter's last sentence, including after a page reload. Reloading the page restores the active mode and that mode's saved position. Sentence and chapter positions are scoped to the current book; the active mode is currently shared across readers.

## Paragraphs and chunks

- Source paragraph boundaries remain visible in all reading modes.
- A chunk represents a lexical or grammatical study unit and never consists only of punctuation.
- Adjacent or sentence-final punctuation belongs to the preceding chunk's surface and reading. It does not receive a separate gloss.
- The ordered concatenation of chunk surfaces, allowing only deliberately uncovered formatting gaps accepted by the validator, reproduces the Japanese sentence text.

## Sentence audio

- Audio is optional per book and is generated ahead of time; the browser never calls a speech-synthesis service.
- One MP3 maps to exactly one sentence through one-based chapter, paragraph, and sentence numbers. The runtime path is `audio/chapter-XX/paragraph-XXX/sentence-XXX.mp3` relative to the book reader.
- The player is available only in `Frases` and never starts automatically.
- `▶ Ouvir` alternates between play and pause, resuming from the paused position.
- `↺ Início` immediately seeks to the beginning and plays, whether the sentence was paused or already playing.
- `↻ Loop` offers `Desligado`, `Frase`, `Glosses + frase`, `Glosses JP + frase`, `Tradução + frase`, `Parágrafo`, `Glosses + parágrafo`, `Glosses JP + parágrafo`, and `Tradução + parágrafo`. `Frase` repeats the current MP3. `Glosses + frase` reads every listening-marked gloss as Japanese, Portuguese, then Japanese before the sentence MP3; `Glosses JP + frase` reads each marked Japanese surface once before that MP3. `Tradução + frase` reads the full Portuguese translation before the current Japanese MP3 and repeats that pair without leaving the sentence. `Parágrafo` plays each sentence once in order, then wraps from the last sentence back to the first sentence of that same paragraph. The three paragraph variants follow this bounded traversal and precede each sentence with, respectively, the full gloss sequence, Japanese-only glosses, or the Portuguese translation; sentences without listening glosses go directly to the MP3. Every transition between a completed phase and the next phase waits 500 ms, while the first phase starts immediately. Gloss and translation modes require browser speech synthesis; gloss modes also require relevant listening marks. Navigating away, leaving `Frases`, or changing the loop mode cancels a pending phase.
- Navigating to another sentence or leaving `Frases` stops playback and returns it to the beginning.
- The selectable speeds come from the book metadata. Changing speed updates the current playback immediately without selecting or generating another MP3.
- Playback speed persists per book. The generated source remains at `1.0×`, and the browser preserves pitch while changing playback rate where supported.
- Loading and playback failures remain local to the player and do not block reading or navigation.
- Voice generation, manifest verification, storage layout, and the audio roadmap are specified in `docs/audio.md`.

## Marked glosses

- Each interlinear chunk has two independent reasons: `★` for unknown or study-worthy vocabulary and `🎧` for a term that was difficult to recognize in sentence audio. A gloss may have either reason, both, or neither.
- Clicking the main body of a chunk marks both `★` and `🎧` together when either is absent; clicking it again while both are active removes both. The two compact reason buttons on the right continue to toggle vocabulary and listening independently.
- The compact summary displays global totals as `★ vocabulary · 🎧 listening` and updates immediately.
- Marked glosses persist in browser storage and are included in exported reader data with a `reasons` array.
- Stored or imported glosses without `reasons` are treated as `vocabulary`, preserving all marks created before the two-reason model.
- When at least one gloss in the current sentence has `🎧` and the browser supports the Web Speech API, `▶ Escuta` reads only those glosses in sentence order. For each gloss it reads Japanese, Portuguese, and Japanese again, using separate language settings. The adjacent `▶ JP` control reads each of the same glosses once, only in Japanese. Pressing the active control again stops its sequence; selecting the other control switches sequences.
- Browser-synthesized gloss speech is an optional convenience and is separate from the pinned Nise sentence MP3s; voice quality and availability depend on the operating system and browser.
- `▶ PT`, beside the full Portuguese translation at the end of the sentence card, reads only that translation with the browser's `pt-BR` speech synthesis. While active it becomes `■ PT`; pressing it again stops playback. Starting sentence audio, gloss speech, navigation, or another reading mode also stops it.

## Import and export

The reader downloads its backup as `dados-de-leitura.json`.

### Backup schema version 3

Version 3 contains:

- `source_file`, identifying the book;
- export timestamp;
- marked glosses with one or both reasons (`vocabulary`, `listening`);
- active reading mode;
- active sentence index;
- the most recently read sentence index for every chapter;
- font level;
- furigana visibility;
- the independent positions for `Frases`, `Corrido`, and `Vertical`.

Version 3 reader state may be applied only when `source_file` matches the currently open book. Backups made before per-chapter sentence positions existed remain valid: their single active sentence is retained and other chapters begin at their first sentence. The complete payload is validated before any gloss or reader state is changed, so a failed import is atomic.

### Legacy compatibility

The importer continues to accept schema versions 1 and 2. Version 1 updates glosses without replacing reader positions or preferences; version 2 retains its reader state. In either legacy version, every gloss without a `reasons` field is migrated to `reasons: ["vocabulary"]`.

## Offline reading

- The site is an installable PWA with a web app manifest, 192 px and 512 px icons, standalone display, theme colors, and a root-scoped Service Worker. Installation is offered by compatible browsers through their normal install interface.
- Installing the PWA caches only the application shell: library page, reader, public book JSON, manifest, and icons. Sentence MP3s remain opt-in through the chapter and full-book download controls, avoiding an automatic download of the complete audio collection.
- The installed app starts directly in `A Princess of Mars`; ordinary browser use and the library page remain available.
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
