from pgvector import Vector
from pgvector.asyncpg import register_vector
from sentence_transformers import SentenceTransformer

from graphrag_entertainment.ingestion.db_conn import get_postgres_connection


def process_query(query:str):
    model=SentenceTransformer("all-MiniLM-L6-v2")
    embed_query=model.embed_text(query).tolist()
    res_rows=similarity_search(embed_query)

    context=build_context(res_rows)
    return context


def build_context(results):

    context_parts = []

    for result in results:

        context_parts.append(
            f"""
            Chunk_content:
            {result["content"]}
            
            {result["metadata"]}
            {result["title"]}
            """
        )

    return "\n\n".join(context_parts)



def similarity_search(query_embed:list[float],k:int =5):
    conn=get_postgres_connection()

    register_vector(conn)
    query_vector=Vector(query_embed)
    rows = conn.execute(
        """
        SELECT c.id AS chunk_id,
               c.document_id,
               c.content,
               d.title,
               d.metadata,
               1 - (c.embedding <=> %s) AS similarity
        FROM chunk c
                 JOIN document d
                      ON c.document_id = d.id
        WHERE c.embedding IS NOT NULL
        ORDER BY c.embedding <=> %s
        LIMIT %s;
        """,
        (query_vector, query_vector, k)
    ).fetchall()
    return rows
