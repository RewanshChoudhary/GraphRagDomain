import os

import spacy
from dotenv import load_dotenv

load_dotenv()
CHUNK_MAX_CHARS=os.getenv("CHUNK_MAX_SIZE")
CHUNK_MAX_SENTENCES=os.getenv("CHUNK_MAX_SENTENCES")
nlp =spacy.blank("en")
nlp.add_pipe("sentencizer",config={
        "punct_chars": [".", "!", "?"]
    })

def split_sentences(text)-> list[str]:
    if not text:
        return []
    doc=nlp(text)

    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]


def group_sentences(sentences: list[str]) -> list[str]:
    chunks = []

    current_sentences = []
    current_length = 0

    for sentence in sentences:

        sentence_length = len(sentence)


        exceeds_sentence_limit = (
            len(current_sentences) >= int(CHUNK_MAX_SENTENCES)
        )

        exceeds_length_limit = (
            current_length + sentence_length > (CHUNK_MAX_CHARS)
        )

        if current_sentences and (
            exceeds_sentence_limit or exceeds_length_limit
        ):
            chunks.append(" ".join(current_sentences))

            current_sentences = []
            current_length = 0

        current_sentences.append(sentence)
        current_length += sentence_length


    if current_sentences:
        chunks.append(" ".join(current_sentences))

    return chunks


