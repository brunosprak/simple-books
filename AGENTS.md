# Japanese Literary Translation Project

## Scope

This repository is for translating English prose supplied under `texts/` into natural, publication-quality modern Japanese. Apply these instructions whenever translating or revising a translation in this repository.

Do not translate an entire work in one pass unless the user explicitly asks. Translate exactly one source paragraph per execution so that the user can review style and terminology before translation continues.

## Source and Output Workflow

- Treat files under `texts/` as immutable source material. Do not edit them unless the user explicitly requests a source correction.
- Translate the file or passage named by the user. If the user says only to continue, resume the source whose Japanese output was most recently updated.
- Write the translation beside the source file, using the same basename followed by `-ja` before the extension. For example, `texts/book.txt` becomes `texts/book-ja.txt`.
- Keep the matching `-ja.json` file synchronized with the Japanese TXT. It is the canonical source for the interactive reader and must contain the page metadata, paragraph and sentence structure, Portuguese sentence translations, and each chunk's Japanese surface, reading, and concise Portuguese gloss.
- Generate `site/index.html` with `python3 tools/build_reader.py` after changing the JSON. Do not edit generated book content directly in `site/index.html`; change the JSON or `site/reader.template.html` and regenerate it.
- Run `python3 tools/build_reader.py --check` before completing reader-related work.
- On the first execution for a source file, create its Japanese output and translate the front matter before the prose—such as title, author, and the first section or chapter heading—followed by exactly the first prose paragraph.
- On every later execution, append exactly one new source paragraph to the same Japanese output file. If a section or chapter heading occurs before that paragraph, append the heading together with the paragraph.
- Treat a blank-line-delimited prose block as one paragraph. Never split a paragraph across executions, even when it is long.
- Before appending, compare the end of the Japanese output with the source to identify the next untranslated paragraph. Preserve voice, spelling, naming, formatting, and established terminology.
- Never silently skip, duplicate, summarize, or reorder source material. Verify that the appended paragraph immediately follows the material already translated.
- Preserve paragraph breaks when practical. Preserve deliberate headings, letters, quotations, chants, inscriptions, and other embedded forms, adapting their typography naturally for Japanese publishing.
- Do not add translator's notes, explanations, romanization, alternative renderings, or commentary to translation files unless the user explicitly asks.

## Translation Standard

Produce natural Japanese fiction, not a sentence-by-sentence rendering of English syntax. The result should read like a professionally published Japanese translation of a Western science-fiction, fantasy, horror, or adventure novel: clear, economical, highly readable, and cinematic in rhythm.

### Style and register

- Use straightforward, economical narration with mostly short-to-medium sentences.
- Favor concrete verbs and direct descriptions of actions, movement, sounds, and events.
- Keep the narrator neutral, observational, and unobtrusive unless the source voice requires otherwise.
- Preserve changes in pace. Calm passages should remain measured; action should become compact and rapid. Natural sentence fragments are acceptable during fast action.
- Avoid needless poetic ornament, archaism, academic diction, or conspicuously sophisticated wording unless the source specifically calls for it.
- Do not make the prose resemble a textbook, language-learning material, or an exaggerated contemporary light novel.
- Prefer common, transparent expressions over obscure literary synonyms when both are equally accurate.

### Natural Japanese

- Prioritize idiomatic Japanese over English sentence structure. Freely divide, combine, or reorder sentences when needed for natural flow, while preserving meaning and emphasis.
- Avoid translationese. Do not mechanically reproduce English subjects, pronouns, conjunctions, passive constructions, or sentence boundaries.
- Omit subjects and pronouns when context makes them unnecessary.
- Use connective forms such as `～とき`, `～と`, `～ながら`, `～ため`, `～ので`, `すると`, `それに`, and `そこで` only where they sound natural; do not rely on them mechanically.
- Use ordinary standard kanji appropriate for general adult or young-adult fiction. Do not avoid kanji merely to simplify the text.
- Do not explain what the source merely shows.

### Dialogue

- Write genuinely spoken Japanese suited to each character's personality, age, relationship, social position, and immediate situation.
- Translate for conversational effect rather than literally. Natural endings and contractions such as `～んだ`, `～んだな`, `～だろう`, `～じゃないか`, `～ぞ`, and `～さ` may be used when justified.
- Preserve meaningful contrasts in politeness and register.
- Do not invent stereotyped speech patterns, verbal tics, or characterization absent from the source.

### Names and terminology

- Use established Japanese translations or transliterations for well-known proper nouns when they exist.
- Render foreign personal names, places, organizations, vehicles, weapons, technologies, and invented terms in forms natural to Japanese publishing; use katakana where conventional.
- For invented terminology, choose a natural rendering and keep it internally consistent across parts.
- Check the progress record and prior translated parts before changing any established rendering. If a correction is necessary, update affected earlier parts and the terminology record consistently rather than introducing an unexplained variant.

### Fidelity

- Preserve meaning, characterization, atmosphere, tone, narrative perspective, factual details, and the amount of information available to the narrator.
- Do not summarize, censor, soften, embellish, or introduce details or Japanese cultural elements absent from the source.
- Do not explain terminology unless the source explains it.
- Preserve deliberate ambiguity instead of arbitrarily resolving it.
- Retain the historical or social attitudes present in the source without silently modernizing them; translate their narrative function accurately.

## Quality Check for Each Part

Before marking a part complete:

1. Compare the translation against every source paragraph in the selected range for omissions, additions, factual drift, and accidental repetition.
2. Read the Japanese independently for idiomatic flow, clear reference, consistent viewpoint, and brisk narrative rhythm.
3. Check names, terminology, dates, measurements, quotations, and formatting against the earlier content in the Japanese output file.
4. Revise any passage whose English structure remains perceptible beneath the Japanese.

When the user requests translation text in the response, output only the Japanese translation itself. Do not append explanations, notes, alternatives, romanization, or a summary.
