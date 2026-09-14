import json

from ingestion.db_conn import get_postgres_connection


def insert_document(document):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cur:
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
                    document.title,
                    document.content,
                    json.dumps(document.metadata),
                ),
            )

            document_id = cur.fetchone()[0]

        conn.commit()

        return document_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def insert_documents(documents):
    conn = get_postgres_connection()
    ids = []

    try:
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

        conn.commit()

        return ids

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
