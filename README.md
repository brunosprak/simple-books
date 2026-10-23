# Japanese text reader

This repository builds a static Japanese study reader for books, game scripts and other text documents. The shared domain model is:

```text
Document → Section → Passage → Sentence → Chunk
```

Existing translated books use legacy schema version 2 through a compatibility adapter. New non-book content uses generic schema version 3 with stable entity IDs, customizable labels and optional capabilities.

See [docs/document-model.md](docs/document-model.md) for the data model and [docs/reader.md](docs/reader.md) for reader behavior.

## Build and verify

```sh
python3 tools/build_reader.py \
  --data texts/rpg-ja.json \
  --output site/rpg/index.html \
  --data-url ../books/rpg-ja.json \
  --json-output site/books/rpg-ja.json

python3 -m unittest discover -s tests
git diff --check
```

Use the same build command with `--check` to verify generated artifacts without rewriting them.
