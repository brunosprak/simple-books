# Sentence audio

The reader's sentence audio is generated from the canonical Japanese JSON and stored as static MP3 files. Audio is not generated in the browser and no API token or speech service is required when a reader presses play.

## Current implemented state

`A Princess of Mars` currently has a complete checked-in audio set:

- 224 sentence MP3 files generated successfully;
- approximately 19 MB total;
- one file for every sentence currently present in the canonical JSON;
- a manifest that pins the source text hash, voice/model settings, encoding settings, and file size;
- automated checks for path stability, complete sentence coverage, stale hashes, missing files, obsolete files, and manifest drift;
- a `Frases` player with play/pause and playback choices from `0.70×` through `1.30×` in `0.05×` increments;
- per-book speed persistence, immediate speed changes during playback, and automatic stop when sentence or reading mode changes.

Voice-comparison samples remain separate from published book audio under `samples/audio/`. They are reference artifacts and are not loaded by the reader.

## Architecture and runtime contract

The canonical `texts/<book-slug>-ja.json` enables audio with optional page metadata:

```json
{
  "page": {
    "audio": {
      "base_url": "audio",
      "voice": "Nise",
      "speed_levels_percent": [70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130],
      "default_speed_percent": 100
    }
  }
}
```

Books without `page.audio` keep the same shared reader but do not expose audio controls. This lets audio be introduced book by book.

At runtime, the reader derives the current sentence path from the same chapter, paragraph, and sentence indexes used by navigation. It loads the file only after the user presses play. The source is always the `1.0×` recording; speed changes use the browser's playback rate and do not duplicate assets.

## Published layout

Each book keeps its audio below its own reader directory:

```text
site/<book-slug>/audio/
  chapter-01/
    paragraph-001/
      sentence-001.mp3
  manifest.json
```

Chapter, paragraph, and sentence numbers are one-based. Chapter numbers use two digits; paragraph and sentence numbers use three digits. For example, chapter 2, paragraph 4, sentence 5 is:

```text
site/princess-of-mars/audio/chapter-02/paragraph-004/sentence-005.mp3
```

## Princess of Mars voice and encoding

`A Princess of Mars` uses the AivisSpeech model `にせ` (Nise), normal style, at generation speed `1.0`. The model UUID and SHA-256 are pinned in `tools/build_audio.py`. The model is distributed under ACML 1.0.

MP3 output is mono at 44.1 kHz using `libmp3lame` quality level 2. The manifest records the full pinned configuration so a changed model, encoding setting, or sentence invalidates reuse.

## Generation and verification

Start AivisSpeech Engine with the pinned Nise model installed, then run:

```bash
python3 tools/build_audio.py \
  --data texts/princess-of-mars-ja.json \
  --output-dir site/princess-of-mars/audio
```

The generator reuses a file only when its sentence hash and all pinned settings still match the manifest. It generates new or changed sentences and rewrites the manifest atomically.

Verify the complete set without running AivisSpeech:

```bash
python3 tools/build_audio.py \
  --data texts/princess-of-mars-ja.json \
  --output-dir site/princess-of-mars/audio \
  --check
```

Run the reader builder and test suite after changing canonical text, audio metadata, the shared template, or audio tooling. The reader builder validates the optional audio metadata independently from the MP3 manifest.

## Browser-synthesized marked glosses

The `▶ Glosses` control is intentionally separate from static sentence narration. It sends only the marked Japanese terms to the browser's built-in Web Speech API, selects an available `ja` voice when possible, and requires no network speech API. Its voice, pronunciation, and availability vary by browser and operating system, so it is a convenience for comparison rather than a reproducible audio asset.

## Future roadmap

The current architecture deliberately leaves room for these later stages:

1. Publish the current static audio snapshot with the reader and verify range requests, caching, and mobile playback on GitHub Pages.
2. Add a CI or release check that runs `build_audio.py --check` so text changes cannot ship with stale or missing sentence audio.
3. Add an explicit operator workflow for incremental synthesis after translation updates; unchanged sentence files should continue to be reused.
4. Consider preloading only the next sentence after playback begins, based on real network measurements. Avoid eager chapter-wide downloads.
5. Evaluate optional continuous paragraph or chapter playback. This should compose existing sentence files and must preserve manual sentence navigation rather than introduce duplicate narration assets.
6. Reassess storage if the complete translated novel approaches repository or hosting limits. The deterministic paths allow migration to a CDN or object storage by changing `base_url` without changing sentence identity.
7. Add more books or voices only through book-specific metadata and a separately pinned generation profile; do not make a global voice assumption in the shared reader.

These roadmap items are planned, not implemented, unless they are later moved into the current-state section with corresponding tests and generated artifacts.
