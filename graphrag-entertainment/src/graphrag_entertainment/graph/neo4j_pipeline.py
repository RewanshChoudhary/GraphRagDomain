import logging
from typing import Any

from neo4j import ManagedTransaction
from graphrag_entertainment.ingestion.db_conn import (
    get_neo4j_driver,
    get_postgres_connection,
)
from graphrag_entertainment.ingestion.models import Chunk
from graphrag_entertainment.models.extraction import GraphExtraction
from graphrag_entertainment.model_interface import get_agent
from psycopg.rows import class_row

logger = logging.getLogger(__name__)

SYS_PROMPT = """You are a Knowledge Graph Information Extraction system.
Extract entities, relationships, and claims from the provided text chunk.
For each claim, set entity_name and entity_type to exactly match its subject
entity in entities. For each relationship, set source_chunk_id to the supplied
CHUNK_ID exactly. Do not invent source chunk IDs; the application assigns them."""


WRITE_ENTITIES = """
UNWIND $rows AS row
MERGE (e:Entity {name: row.name, type: row.type})
SET e.description = row.description
"""

WRITE_CHUNKS = """
UNWIND $rows AS row
MERGE (c:Chunk {id: row.id})
SET c.document_id = row.document_id,
    c.chunk_index = row.chunk_index,
    c.content = row.content
"""

WRITE_RELATIONSHIPS = """
UNWIND $rows AS row
MATCH (source:Entity {name: row.source})
MATCH (target:Entity {name: row.target})
MERGE (source)-[r:RELATED_TO {
    type: row.type,
    source_chunk_id: row.source_chunk_id
}]->(target)
SET r.description = row.description
"""

WRITE_CLAIMS = """
UNWIND $rows AS row
MATCH (e:Entity {name: row.entity_name, type: row.entity_type})
MATCH (c:Chunk {id: row.source_chunk_id})
MERGE (claim:Claim {
    entity_name: row.entity_name,
    entity_type: row.entity_type,
    description: row.description,
    source_chunk_id: row.source_chunk_id
})
MERGE (e)-[:HAS_CLAIM]->(claim)
MERGE (claim)-[:SUPPORTED_BY]->(c)
RETURN count(claim) AS written
"""


def write_extraction(
    tx: ManagedTransaction,
    chunk_row: dict[str, Any],
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]],
    claims: list[dict[str, Any]],
) -> None:
    tx.run(WRITE_CHUNKS, rows=[chunk_row]).consume()
    tx.run(WRITE_ENTITIES, rows=entities).consume()
    tx.run(WRITE_RELATIONSHIPS, rows=relationships).consume()

    result = tx.run(WRITE_CLAIMS, rows=claims)
    record = result.single(strict=True)
    written = record["written"]
    if written != len(claims):
        raise ValueError(
            f"Could not link all claims for chunk {chunk_row['id']}: "
            f"matched {written} of {len(claims)} claim(s). "
            "Check that each claim's entity name and type match an entity node."
        )


def create_graph():
    conn = get_postgres_connection()
    try:
        with conn.cursor(row_factory=class_row(Chunk)) as cur:
            cur.execute(
                """SELECT id, document_id, chunk_index, content, token_count
                   FROM chunk
                   LIMIT 1000"""
            )
            data: list[Chunk] = cur.fetchall()
            process_chunks(data)
    except Exception:
        logger.exception("Error creating the graph in create_graph()")
        conn.rollback()
        raise
    finally:
        conn.close()


def process_chunks(data: list[Chunk]):
    agent = get_agent(GraphExtraction, SYS_PROMPT)

    with get_neo4j_driver() as driver:
        with driver.session() as session:
            for chunk in data:
                if chunk.id is None:
                    raise ValueError(
                        "Cannot write an extracted chunk without its persisted PostgreSQL id."
                    )
                chunk_id = chunk.id
                prompt = (
                    f"CHUNK_ID: {chunk_id}\n"
                    f"CHUNK_INDEX: {chunk.chunk_index}\n"
                    f"TEXT:\n{chunk.content}"
                )
                response = agent.invoke(prompt)

                entities = [
                    entity.model_dump(mode="json")
                    for entity in response.entities
                ]
                relationships = [
                    {
                        **relationship.model_dump(mode="json"),
                        "source_chunk_id": str(chunk_id),
                    }
                    for relationship in response.relationships
                ]
                claims = [
                    {
                        **claim.model_dump(mode="json"),
                        "source_chunk_id": chunk_id,
                    }
                    for claim in response.claims
                ]

                session.execute_write(
                    write_extraction,
                    {
                        "id": chunk_id,
                        "document_id": chunk.document_id,
                        "chunk_index": chunk.chunk_index,
                        "content": chunk.content,
                    },
                    entities,
                    relationships,
                    claims,
                )


if __name__ == "__main__":
    create_graph()
