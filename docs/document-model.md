# Generic document model

The reader treats every source as a text document. A book, game script, film script, article or transcript differs through metadata, labels and capabilities—not through a separate rendering implementation.

## Canonical hierarchy

```text
Document
└── Section
    └── Passage
        └── Sentence
            └── Chunk
```

- A **section** is a navigable large unit: a chapter, scene, quest, episode or article section.
- A **passage** preserves a meaningful source boundary: a paragraph, speech turn, subtitle cue or text box.
- A **sentence** is the unit used by the sentence reader and incremental analysis.
- A **chunk** is the smallest displayed lexical or grammatical study unit.

Every entity has a stable string `id`. IDs must be unique inside a document and should survive textual corrections whenever the entity still represents the same logical unit.

## Schema version 3

```json
{
  "schema_version": 3,
  "id": "sample-script",
  "source_file": "sample-script.local",
  "kind": "game_script",
  "editable": true,
  "labels": {
    "section": "Cena",
    "sections": "Cenas",
    "passage": "Fala",
    "passages": "Falas"
  },
  "languages": {
    "source": "ja",
    "translation": "pt-BR",
    "gloss": "pt-BR"
  },
  "metadata": {
    "title": "RPG",
    "creator": "",
    "eyebrow": "ROTEIRO DE JOGO",
    "description": "Roteiro japonês para leitura e estudo.",
    "study_hint": "",
    "footer": "Dados pessoais ficam neste navegador.",
    "font_levels_percent": [80, 90, 100, 110, 120, 140, 160],
    "default_font_level_percent": 100
  },
  "capabilities": {
    "editing": true,
    "audio": null,
    "incremental_reading": true
  },
  "sections": [
    {
      "id": "scene-1",
      "kind": "scene",
      "title": "Cena 1",
      "passages": [
        {
          "id": "speech-1",
          "kind": "speech",
          "speaker": "",
          "sentences": [
            {
              "id": "sentence-1",
              "text": "彼女が来た。",
              "pt": "Ela veio.",
              "chunks": [
                {
                  "id": "chunk-1",
                  "surface": "彼女が",
                  "reading": "かのじょが",
                  "gloss": "ela"
                },
                {
                  "id": "chunk-2",
                  "surface": "来た。",
                  "reading": "きた。",
                  "gloss": "veio"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

`kind` values are open strings. They describe content without branching the core reader. `labels` controls visible domain vocabulary. `capabilities` controls optional features independently.

## Compatibility

Schema version 2 remains the canonical format for the existing translated books. At runtime, `site/modules/document-model.js` maps `chapters` to `sections`, `paragraphs` to `passages`, page metadata to document metadata and array chunks to chunk objects. Deterministic fallback IDs are derived from entity positions.

`tools/build_reader.py` validates both schemas. For v3 it first verifies the generic hierarchy and globally unique IDs, then adapts the content to the established sentence/chunk validation so text coverage, punctuation and reading rules remain identical.

New non-book documents should use v3. Existing books can migrate separately without requiring a flag day or changing public URLs.

## Runtime modules

- `document-model.js`: normalization plus compatibility adapters and editable-document serialization.
- `storage.js`: safe, document-namespaced browser persistence.
- `openai-client.js`: the single Responses API transport with timeout and normalized errors.
- `reader.template.html`: presentation and feature orchestration. Historical `chapter` and `paragraph` names may remain in DOM IDs or local implementation details for backup compatibility, but domain data enters through the generic model.

Reader study backups and editable document exports are separate. `dados-de-leitura.json` carries study state and analyses; `<id>.documento-ja.json` carries the editable text itself.

## Adding a document kind

1. Create a schema-v3 canonical JSON with a unique document ID, desired `kind`, labels and capabilities.
2. Keep the common section/passage/sentence/chunk hierarchy; do not add a parallel reader data structure.
3. Generate its reader and public JSON with `tools/build_reader.py`.
4. Add the reader to the library and offline shell.
5. Run all tests, JavaScript syntax checks and generated-output checks.

