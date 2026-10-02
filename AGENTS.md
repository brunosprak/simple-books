# Japanese Literary Translation Project

## Scope

This repository is for translating English prose supplied under `texts/` into natural, publication-quality modern Japanese. Apply these instructions whenever translating or revising a translation in this repository.

If the user does not specify an amount, translate exactly one source paragraph per execution so that style and terminology can be reviewed before translation continues. When the user explicitly requests a number of paragraphs, a range, all available paragraphs, or an entire work, translate the requested amount in that execution.

## Source and Output Workflow

- Treat the original English files under `texts/` as immutable source material. Do not edit them unless the user explicitly requests a source correction. The matching `-ja.json` file is the sole canonical translation and reader-data source.
- Translate the file or passage named by the user. If the user says only to continue, resume the source whose Japanese output was most recently updated.
- Write and revise the translation in a JSON file beside the source, using the same basename followed by `-ja.json`. For example, `texts/book.txt` becomes `texts/book-ja.json`.
- Use JSON schema version `2`. The root must contain `schema_version`, `source_file`, optional `source_url`, `languages`, `page`, and `chapters`. Each `chapters[]` object contains its own `title` and `paragraphs`; each paragraph is an array of sentence objects with `text`, `pt`, and `chunks`. Each chunk is `[Japanese surface, reading, concise Portuguese gloss]`.
- When the English source comes from a stable public edition, record its canonical download URL in root-level `source_url`. Keep `source_file` as the local filename; the URL does not replace the local source.
- Do not maintain a separate Japanese TXT by hand. When the user requests a clean TXT for reading or download, generate it deterministically from the canonical JSON with `python3 tools/build_reader.py --data <json-path> --output <html-path> --text-output texts/<book-slug>-ja.txt`. A generated TXT is disposable and must never be used to determine translation progress.
- Give every book its own directory under `site/`, with its generated HTML inside that directory. Use `site/<book-slug>/index.html`; do not place multiple book readers directly in the root of `site/`.
- Store paragraphs inside their chapter object under `chapters[].paragraphs`; do not keep a root-level `paragraphs` array or duplicate chapter titles in `page`. Generate the runtime reader and its public JSON with `python3 tools/build_reader.py --data <json-path> --output site/<book-slug>/index.html --data-url ../books/<book-slug>-ja.json --json-output site/books/<book-slug>-ja.json` after changing the canonical JSON.
- Do not edit generated book content directly in a book's HTML. Change the matching JSON or `site/reader.template.html` and regenerate the page.
- Run the corresponding generation command with `--check`, including `--data-url` and `--json-output`, before completing reader-related work.
- On the first execution for a source file, create its Japanese output and translate the front matter before the prose—such as title, author, and the first section or chapter heading—followed by the amount of prose requested by the user. If no amount is specified, translate exactly the first prose paragraph.
- On every later execution, append the number of source paragraphs requested by the user. If no amount is specified, append exactly one. If a section or chapter heading occurs before the selected paragraph or range, append the heading together with it.
- Translation progress is tracked independently inside each chapter. When the user explicitly names a chapter or passage, work there even if an earlier chapter is incomplete; preserve source order within the selected chapter and do not treat gaps in other chapters as translated. If the user says only to continue, resume immediately after the most recently updated paragraph in the most recently updated chapter.
- Treat a blank-line-delimited prose block as one paragraph. Never split a paragraph across executions, even when it is long.
- Before appending, compare the final translated paragraph of the selected chapter with that chapter in the English source to identify the next untranslated paragraph. Do not infer whole-book progress from the last chapter stored in the JSON. Preserve voice, spelling, naming, formatting, and established terminology.
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
- Use ordinary standard kanji appropriate for general adult or young-adult fiction. Simplifying vocabulary does not mean rewriting ordinary kanji in hiragana; retain conventional kanji unless the written form itself is unusually difficult or unnatural for the intended reader.
- Do not explain what the source merely shows.

### Vocabulary accessibility and simplicity

- Prefer common, immediately understandable modern Japanese vocabulary whenever it preserves the source's meaning, tone, atmosphere, and factual detail.
- When a rare, formal, literary, or technical expression has a natural everyday equivalent, use the simpler equivalent. For example, forms comparable to `危険な` instead of `凶暴な`, `盗賊` instead of `略奪者`, `隠れる` instead of `潜む`, `殺す` instead of `命を奪う`, or an explicit phrase instead of a compact literary expression may be preferable.
- Favor transparent verbs and concrete descriptions over nominal, abstract, or compressed constructions. Prefer `武器を持つ` to `武装する`, `跡を追うのがうまい` to `追跡に長ける`, and similarly direct wording when no important nuance is lost.
- Simplify sentence structure when it improves readability, but do not make the prose childish, choppy, explanatory, or unnaturally casual. The result should remain polished narrative fiction.
- Do not simplify established proper nouns, essential historical terms, fictional terminology, or precise technical distinctions when doing so would create factual drift.
- Prefer accessibility when perfect equivalence and simpler vocabulary cannot both be maintained. A small loss of intensity, precision, register, or nuance is acceptable when it allows a substantially more common word or transparent phrase, provided the central action, fact, characterization, and narrative function remain intact. Do not censor, reverse, or materially alter the event.
- When the user requests simplification beginning at a particular card, paragraph, or sentence, apply the simpler vocabulary consistently from that point onward and keep all earlier material unchanged unless explicitly asked.
- After simplifying Japanese text, update the JSON sentence text, readings, chunks, Portuguese glosses, and generated HTML together. If a disposable TXT export already exists, regenerate it or remove it so that stale text is not mistaken for canonical data. Card numbering does not need to be preserved: sentences may be split or combined when that produces clearer Japanese.

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

### Interlinear chunks and Portuguese glosses

- Divide each Japanese sentence into small, meaningful lexical or grammatical chunks. A chunk should normally contain one content word, a short compound, or a compact grammatical construction—not an entire clause merely because it has a natural Portuguese translation.
- Split subjects, destinations, adverbs, verbs, objects, auxiliaries, and clause endings when each part is independently useful to a learner. Keep elements together only when separating them would obscure an idiom, fixed expression, compound term, or grammatical construction.
- Make Portuguese glosses concise prompts, not miniature sentence translations. Prefer one to three words; use four only when needed to preserve the function or meaning of a compact construction.
- Prefer dictionary-like meanings such as `equipamento`, `à civilização`, `voltar`, and `por ser rudimentar`. Avoid repeating complete Portuguese clauses such as `como o equipamento era rudimentar` when the Japanese can be divided naturally.
- Do not force Portuguese word order onto the Japanese chunks. Each gloss should describe its own Japanese unit; the separate `pt` field carries the natural translation of the full sentence.
- Include particles or inflectional material in the chunk where they make the relationship or grammatical function clearer, but keep the Portuguese gloss economical.
- During review, inspect the rendered card at large font sizes. If a chunk becomes a multi-line sentence-like block, re-evaluate whether it should be split further.

### Fidelity

- Preserve the central meaning, characterization, atmosphere, narrative perspective, factual events, and the amount of information available to the narrator. Minor losses of intensity, precision, register, or nuance are permitted only under the vocabulary-simplicity rules above.
- Do not summarize, censor, materially soften, embellish, or introduce details or Japanese cultural elements absent from the source. Replacing a difficult expression with a slightly broader but substantially more common expression is not considered material softening when the central event and narrative function remain intact.
- Do not explain terminology unless the source explains it.
- Preserve deliberate ambiguity instead of arbitrarily resolving it.
- Retain the historical or social attitudes present in the source without silently modernizing them; translate their narrative function accurately.

## Quality Check for Each Part

Before marking a part complete:

1. Compare the translation against every source paragraph in the selected range for omissions, additions, factual drift, and accidental repetition.
2. Read the Japanese independently for idiomatic flow, clear reference, consistent viewpoint, and brisk narrative rhythm.
3. Check names, terminology, dates, measurements, quotations, and formatting against the earlier content in the canonical Japanese JSON.
4. Revise any passage whose English structure remains perceptible beneath the Japanese.
5. Check that interlinear chunks are minimal meaningful units and that their Portuguese glosses are short prompts rather than clause-level retranslations.
6. Check for unnecessarily difficult vocabulary and replace it with a common modern equivalent wherever meaning and tone remain intact.

When the user requests translation text in the response, output only the Japanese translation itself. Do not append explanations, notes, alternatives, romanization, or a summary.
