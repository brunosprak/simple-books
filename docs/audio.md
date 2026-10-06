# Sentence audio

The reader's sentence audio is generated from the canonical Japanese JSON and is
stored as static MP3 files. Audio is not generated in the browser.

## Published layout

Each book keeps its audio below its own reader directory:

```text
site/<book-slug>/audio/
  chapter-01/
    paragraph-001/
      sentence-001.mp3
  manifest.json
```

Chapter, paragraph, and sentence numbers are one-based. Chapter numbers use two
digits; paragraph and sentence numbers use three digits.

## Princess of Mars voice

`A Princess of Mars` uses the AivisSpeech model `にせ` (Nise), normal style, at
generation speed `1.0`. The model is pinned by UUID and SHA-256 in
`tools/build_audio.py`. The model is distributed under ACML 1.0.

The browser may change playback speed later without creating additional audio
files. The checked-in MP3 is always the original `1.0` generation.

## Generation

Start AivisSpeech Engine with the pinned Nise model installed, then run:

```bash
python3 tools/build_audio.py \
  --data texts/princess-of-mars-ja.json \
  --output-dir site/princess-of-mars/audio
```

The generator reuses files whose sentence text and pinned settings still match
the manifest. Verify the complete set without running AivisSpeech:

```bash
python3 tools/build_audio.py \
  --data texts/princess-of-mars-ja.json \
  --output-dir site/princess-of-mars/audio \
  --check
```
