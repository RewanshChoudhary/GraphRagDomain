import json
import logging

logger = logging.getLogger(__name__)


def insert_documents(conn, documents):
    ids = []

    if not isinstance(documents, list):
        documents = [documents]

    with conn.cursor() as cur:
        for doc in documents:
            cur.execute(
                """
                INSERT INTO document (
                    title,
                    content,
                    metadata
                )
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (
                    doc.title,
                    doc.content,
                    json.dumps(doc.metadata),
                ),
            )
            ids.append(cur.fetchone()[0])

    logger.info("Inserted %d document(s)", len(ids))
    return ids
