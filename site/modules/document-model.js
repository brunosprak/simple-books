const DEFAULT_LABELS = Object.freeze({
  section: "Seção",
  sections: "Seções",
  passage: "Passagem",
  passages: "Passagens"
});

function text(value, fallback = "") {
  return typeof value === "string" ? value : fallback;
}

function stableId(prefix, indexes) {
  return `${prefix}-${indexes.map((value) => value + 1).join("-")}`;
}

function normalizeChunk(chunk, indexes) {
  if (Array.isArray(chunk)) {
    return {
      id: stableId("chunk", indexes),
      surface: text(chunk[0]),
      reading: text(chunk[1]),
      gloss: text(chunk[2])
    };
  }
  return {
    id: text(chunk?.id, stableId("chunk", indexes)),
    surface: text(chunk?.surface),
    reading: text(chunk?.reading),
    gloss: text(chunk?.gloss)
  };
}

function normalizeSentence(sentence, indexes) {
  return {
    id: text(sentence?.id, stableId("sentence", indexes)),
    text: text(sentence?.text),
    pt: text(sentence?.pt),
    chunks: Array.isArray(sentence?.chunks)
      ? sentence.chunks.map((chunk, chunkIndex) => normalizeChunk(chunk, [...indexes, chunkIndex]))
      : []
  };
}

function normalizePassage(passage, indexes) {
  const legacySentences = Array.isArray(passage) ? passage : passage?.sentences;
  return {
    id: text(passage?.id, stableId("passage", indexes)),
    kind: text(passage?.kind, "paragraph"),
    speaker: text(passage?.speaker),
    sentences: Array.isArray(legacySentences)
      ? legacySentences.map((sentence, sentenceIndex) => (
        normalizeSentence(sentence, [...indexes, sentenceIndex])
      ))
      : []
  };
}

function normalizeSection(section, sectionIndex) {
  const legacyPassages = Array.isArray(section?.passages)
    ? section.passages
    : section?.paragraphs;
  return {
    id: text(section?.id, stableId("section", [sectionIndex])),
    title: text(section?.title, `Seção ${sectionIndex + 1}`),
    kind: text(section?.kind, "section"),
    passages: Array.isArray(legacyPassages)
      ? legacyPassages.map((passage, passageIndex) => (
        normalizePassage(passage, [sectionIndex, passageIndex])
      ))
      : []
  };
}

function legacyPage(data) {
  const page = data?.page || {};
  return {
    title: text(page.title, "Texto japonês"),
    creator: text(page.author),
    eyebrow: text(page.eyebrow),
    description: text(page.description),
    study_hint: text(page.study_hint),
    footer: text(page.footer),
    font_levels_percent: page.font_levels_percent,
    default_font_level_percent: page.default_font_level_percent,
    audio: page.audio || null
  };
}

export function normalizeDocument(data) {
  if (!data || typeof data !== "object") throw new Error("Documento inválido.");
  const isGeneric = data.schema_version === 3;
  const metadata = isGeneric ? data.metadata || {} : legacyPage(data);
  const sourceSections = isGeneric ? data.sections : data.chapters;
  const id = text(data.id, text(data.source_file, "document"));
  const kind = text(data.kind, "book");
  const kindLabels = kind === "book"
    ? { section: "Capítulo", sections: "Capítulos", passage: "Parágrafo", passages: "Parágrafos" }
    : DEFAULT_LABELS;
  const labels = { ...kindLabels, ...(data.labels || {}) };
  return {
    schema_version: 3,
    id,
    source_file: text(data.source_file, id),
    kind,
    editable: isGeneric ? data.editable === true : data.page?.editable === true,
    labels,
    languages: data.languages || { source: "ja", translation: "pt-BR", gloss: "pt-BR" },
    metadata: {
      title: text(metadata.title, "Texto japonês"),
      creator: text(metadata.creator, text(metadata.author)),
      eyebrow: text(metadata.eyebrow),
      description: text(metadata.description),
      study_hint: text(metadata.study_hint),
      footer: text(metadata.footer),
      font_levels_percent: metadata.font_levels_percent,
      default_font_level_percent: metadata.default_font_level_percent
    },
    capabilities: {
      editing: isGeneric ? data.capabilities?.editing === true : data.page?.editable === true,
      audio: isGeneric ? data.capabilities?.audio || null : data.page?.audio || null,
      incremental_reading: data.capabilities?.incremental_reading !== false
    },
    sections: Array.isArray(sourceSections)
      ? sourceSections.map(normalizeSection)
      : []
  };
}

export function documentFromReaderSections(baseDocument, sections) {
  return {
    schema_version: 3,
    id: baseDocument.id,
    source_file: baseDocument.source_file,
    kind: baseDocument.kind,
    editable: baseDocument.editable,
    labels: baseDocument.labels,
    languages: baseDocument.languages,
    metadata: baseDocument.metadata,
    capabilities: baseDocument.capabilities,
    sections: sections.map((section, sectionIndex) => ({
      id: text(section.id, stableId("section", [sectionIndex])),
      title: section.title,
      kind: text(section.kind, "section"),
      passages: section.passages.map((sentences, passageIndex) => ({
        id: text(section.passageEntities?.[passageIndex]?.id, stableId("passage", [sectionIndex, passageIndex])),
        kind: text(section.passageEntities?.[passageIndex]?.kind, "paragraph"),
        speaker: text(section.passageEntities?.[passageIndex]?.speaker),
        sentences: sentences.map((sentence, sentenceIndex) => ({
          id: text(sentence.id, stableId("sentence", [sectionIndex, passageIndex, sentenceIndex])),
          text: sentence.text,
          pt: sentence.pt,
          chunks: sentence.chunks.map((chunk, chunkIndex) => Array.isArray(chunk) ? {
            id: stableId("chunk", [sectionIndex, passageIndex, sentenceIndex, chunkIndex]),
            surface: chunk[0],
            reading: chunk[1],
            gloss: chunk[2]
          } : chunk)
        }))
      }))
    }))
  };
}

export function legacySentence(sentence) {
  return {
    id: sentence.id,
    text: sentence.text,
    pt: sentence.pt,
    chunks: sentence.chunks.map((chunk) => [chunk.surface, chunk.reading, chunk.gloss])
  };
}

export function legacyReaderSections(document) {
  return document.sections.map((section) => ({
    id: section.id,
    title: section.title,
    kind: section.kind,
    passageEntities: section.passages,
    passages: section.passages.map((passage) => passage.sentences.map(legacySentence))
  }));
}
