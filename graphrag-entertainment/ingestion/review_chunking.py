
from ingestion.models import Chunk, Document


def chunk_document(document:Document,document_id:int)-> list[Chunk]:
    return [
        Chunk(
            document_id=document_id,
            chunk_index=0,
            content=document.content

        )
    ]

def insert_chunk(conn, chunk):

    with conn.cursor() as cur:

        cur.execute(
            """
            INSERT INTO chunk (
                document_id,
                chunk_index,
                content,
                token_count
            )
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (
                chunk.document_id,
                chunk.chunk_index,
                chunk.content,
                chunk.token_count
            )
        )

        return cur.fetchone()[0]
