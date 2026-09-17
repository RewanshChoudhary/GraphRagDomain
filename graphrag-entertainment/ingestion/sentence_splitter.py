import os

import spacy
from dotenv import load_dotenv


load_dotenv()

CHUNK_MAX_CHARS = int(
    os.getenv("CHUNK_MAX_CHARS", "1500")
)

CHUNK_MAX_SENTENCES = int(
    os.getenv("CHUNK_MAX_SENTENCES", "5")
)


nlp = spacy.blank("en")

nlp.add_pipe(
    "sentencizer",
    config={
        "punct_chars": [".", "!", "?"]
    }
)


def split_sentences(text: str) -> list[str]:

    if not text:
        return []

    doc = nlp(text)

    return [
        sent.text.strip()
        for sent in doc.sents
        if sent.text.strip()
    ]


def group_sentences(sentences: list[str]) -> list[str]:

    chunks = []

    current_sentences = []
    current_length = 0

    for sentence in sentences:

        sentence_length = len(sentence)

        # Space required between this sentence
        # and the existing sentences.
        separator_length = 1 if current_sentences else 0

        new_length = (
            current_length
            + separator_length
            + sentence_length
        )

        exceeds_sentence_limit = (
            len(current_sentences) >= CHUNK_MAX_SENTENCES
        )

        exceeds_length_limit = (
            new_length > CHUNK_MAX_CHARS
        )

        if current_sentences and (
            exceeds_sentence_limit
            or exceeds_length_limit
        ):
            chunks.append(" ".join(current_sentences))

            current_sentences = []
            current_length = 0

        current_sentences.append(sentence)

        current_length += (
            sentence_length
            + (1 if len(current_sentences) > 1 else 0)
        )

    if current_sentences:
        chunks.append(" ".join(current_sentences))

    return chunks