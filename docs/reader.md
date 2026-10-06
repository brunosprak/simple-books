# Reader Functional Specification

This document defines the user-visible behavior and compatibility requirements of the static Japanese reader. Implementation guidance for agents belongs in `AGENTS.md`; reader product rules belong here and should be enforced by automated tests wherever practical.

## Generated architecture

- `texts/<book-slug>-ja.json` is the canonical book and study data.
- `site/books/<book-slug>-ja.json` is its generated public copy.
- `site/<book-slug>/index.html` is generated from the shared `site/reader.template.html` and loads the public JSON at runtime.
- A translation-only change may update the public JSON without changing the generated HTML bytes.

## Reading modes

The mode selector appears in the normal document flow and exposes three modes.

### Frases

- Shows one Japanese sentence at a time with furigana, interlinear chunks, concise Portuguese glosses, and the full Portuguese translation.
- The sentence/paragraph navigation and gloss import/export row appear in the normal document flow before the sentence content.
- Previous and next controls move by sentence.
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

- `Frases`: active sentence index and its chapter.
- `Corrido`: current chapter and vertical page position.
- `Vertical`: current chapter, page position, and vertical-writing page number.

Switching modes restores the last position used in the destination mode. Reloading the page restores the active mode and that mode's saved position. Sentence and chapter positions are scoped to the current book; the active mode is currently shared across readers.

## Paragraphs and chunks

- Source paragraph boundaries remain visible in all reading modes.
- A chunk represents a lexical or grammatical study unit and never consists only of punctuation.
- Adjacent or sentence-final punctuation belongs to the preceding chunk's surface and reading. It does not receive a separate gloss.
- The ordered concatenation of chunk surfaces, allowing only deliberately uncovered formatting gaps accepted by the validator, reproduces the Japanese sentence text.

## Marked glosses

- Interlinear chunks can be marked or unmarked in `Frases`.
- The marked-gloss count updates immediately.
- Marked glosses persist in browser storage and are included in exported reader data.

## Import and export

The reader downloads its backup as `dados-de-leitura.json`.

### Backup schema version 2

Version 2 contains:

- `source_file`, identifying the book;
- export timestamp;
- marked glosses;
- active reading mode;
- active sentence index;
- font level;
- furigana visibility;
- the independent positions for `Frases`, `Corrido`, and `Vertical`.

Version 2 reader state may be applied only when `source_file` matches the currently open book. The complete payload is validated before any gloss or reader state is changed, so a failed import is atomic.

### Legacy compatibility

The importer continues to accept schema version 1 files containing only marked glosses. Importing a version 1 file updates glosses without replacing reader positions or preferences.

## Accessibility and interaction

- All reader controls and navigation sections remain in the normal document flow. No reader element uses `position: sticky` or `position: fixed` to remain suspended while the page scrolls.
- Controls use descriptive accessible names and expose pressed or disabled state where applicable.
- Keyboard activation works for furigana toggles and interactive Japanese text.
- Touch gestures do not suppress ordinary vertical page scrolling.
- A swipe does not also trigger the click action that toggles furigana.

## Regression expectations

Changes to the reader preserve all rules above. Update automated tests with behavior changes, run the generated-output checks for every book affected by the shared template, and perform local browser verification for gesture, scrolling, persistence, or import/export changes when practical.
