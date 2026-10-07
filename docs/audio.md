# Sentence audio

The reader's sentence audio is generated from the canonical Japanese JSON and stored as static MP3 files. Audio is not generated in the browser and no API token or speech service is required when a reader presses play.

## Current implemented state

`A Princess of Mars` currently has a complete checked-in audio set for translated chapters 1 through 16:

- 1,701 sentence MP3 files generated successfully;
- approximately 171 MB total;
- one file for every sentence currently present in the canonical JSON;
- a manifest that pins the source text hash, voice/model settings, encoding settings, and file size;
- automated checks for path stability, complete sentence coverage, stale hashes, missing files, obsolete files, and manifest drift;
- a `Frases` player with play/pause, play-from-start, sentence and paragraph loop modes, optionally reading listening glosses as Japanese–Portuguese–Japanese, each Japanese gloss once, or the full Portuguese translation before each MP3, with a 500 ms gap between phases, and playback choices from `0.70×` through `1.30×` in `0.05×` increments;
- per-book speed persistence, immediate speed changes during playback, loop-mode continuity across sentence navigation, and automatic stop when sentence or reading mode changes.
- chapter-scoped or full-book offline caching of the public JSON, audio manifest, and sentence MP3s through the reader’s final-page controls.

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

### Persistent Docker engine and Nise model

The repository includes `docker-compose.aivis.yml`, which exposes AivisSpeech only on `127.0.0.1:10101`, stores its complete user-data directory in the named volume `simple-ja-aivis-data`, and uses the `unless-stopped` restart policy. The named volume preserves Nise across container replacement and host restarts. Do not run `docker compose down -v` unless the voice models should be deleted deliberately.

Start the engine and ensure that the exact pinned Nise model is installed and valid:

```bash
./tools/ensure_aivis_nise.sh
```

The script starts the Compose service, waits for the engine, installs Nise from AivisHub only when it is missing, verifies the `にせ` normal voice and speaker UUID, and checks the model file against the SHA-256 pinned in `tools/build_audio.py`. The first run also downloads AivisSpeech's default models and can take longer; later runs reuse the persistent volume.

Useful lifecycle commands:

```bash
docker compose -f docker-compose.aivis.yml ps
docker compose -f docker-compose.aivis.yml logs -f aivisspeech
docker compose -f docker-compose.aivis.yml restart aivisspeech
```

### Generate sentence MP3s

After `ensure_aivis_nise.sh` succeeds, generate new or changed sentence audio:

```bash
python3 tools/build_audio.py \
  --data texts/princess-of-mars-ja.json \
  --output-dir site/princess-of-mars/audio
```

The generator reuses a file only when its sentence hash and all pinned settings still match the manifest. It generates new or changed sentences and rewrites the manifest atomically. It is safe to rerun after each translated chapter: existing valid MP3s are skipped and only new or changed sentences are synthesized.

Verify the complete set without running AivisSpeech:

```bash
python3 tools/build_audio.py \
  --data texts/princess-of-mars-ja.json \
  --output-dir site/princess-of-mars/audio \
  --check
```

Run the reader builder and test suite after changing canonical text, audio metadata, the shared template, or audio tooling. The reader builder validates the optional audio metadata independently from the MP3 manifest.

## Browser-synthesized marked glosses

The `▶ Escuta` and `▶ JP` controls are intentionally separate from static sentence narration. Both send only glosses carrying the `listening` reason in the current sentence to the browser's built-in Web Speech API. `▶ Escuta` queues each gloss as Japanese (`ja-JP`), Portuguese (`pt-BR`), then Japanese again, selecting matching installed voices when possible. The adjacent `▶ JP` control, the one-shot `▶ JP + Ouvir` action, and the `Glosses JP` loop modes instead speak each marked Japanese surface exactly once. `▶ JP + Ouvir` is available only with the loop disabled; after the synthesized Japanese glosses it waits 500 ms and plays the static sentence MP3 once. Vocabulary-only marks are never spoken. These controls require no network speech API. Voice quality, pronunciation, and availability vary by browser and operating system, so they are conveniences for comparison rather than reproducible audio assets.

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
