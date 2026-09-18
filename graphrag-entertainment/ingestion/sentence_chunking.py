import logging

from ingestion.models import Chunk, Document
from ingestion.sentence_splitter import group_sentences, split_sentences

logger = logging.getLogger(__name__)


def chunk_document_sentence(document: Document, document_id: int) -> list[Chunk]:
    sentence_list: list[str] = split_sentences(document.content)
    sentence_groups = group_sentences(sentence_list)
    logger.debug("Document %d: %d sentences -> %d chunks", document_id, len(sentence_list), len(sentence_groups))

    return [
        Chunk(
            document_id=document_id,
            chunk_index=i,
            content=sent,
        ) for i, sent in enumerate(sentence_groups)
    ]


def insert_chunks_sentence(chunk: Chunk, conn,embedding:list[float]):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO chunk (document_id,
                               chunk_index,
                               content,
                               token_count,embedding)  
            VALUES (%s, %s, %s, %s, %s) RETURNING id
            """,
            (
                chunk.document_id,
                chunk.chunk_index,
                chunk.content,
                chunk.token_count,
                embedding
            )
        )

        return cur.fetchone()[0]





