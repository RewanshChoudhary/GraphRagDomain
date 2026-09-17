
from ingestion.models import Document, Chunk
from ingestion.sentence_splitter import split_sentences, group_sentences


def chunk_document_sentence(document:Document,document_id:int) ->list[Chunk]:


    sentence_list: list[str]=split_sentences(document.content)
    sentence_groups = group_sentences(sentence_list)


    return [
        Chunk(
            document_id=document_id,
            chunk_index=i,
            content=sent,

        ) for i,sent in enumerate(sentence_groups)
    ]



    
def insert_chunks_sentence(chunk:Chunk,conn):

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO chunk (document_id,
                               chunk_index,
                               content,
                               token_count)
            VALUES (%s, %s, %s, %s) RETURNING id
            """,
            (
                chunk.document_id,
                chunk.chunk_index,
                chunk.content,
                chunk.token_count
            )
        )

        return cur.fetchone()[0]





