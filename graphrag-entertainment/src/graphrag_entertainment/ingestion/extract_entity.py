from collections import defaultdict
from collections.abc import Iterator, Sequence
from typing import TypedDict

from psycopg.rows import dict_row

from graphrag_entertainment.ingestion.db_conn import get_postgres_connection
from graphrag_entertainment.ingestion.models import GraphExtraction
from graphrag_entertainment.model_interface import get_agent

MAX_CHUNKS_PER_BATCH = 15
MAX_BATCH_TOKENS = 2_000


class ChunkRow(TypedDict):
    """One row of the ``document ⋈ chunk`` query used for graph extraction."""

    document_id: int
    movie_title: str
    chunk_id: int
    chunk_index: int
    content: str
    token_count: int | None


#: A batch of chunk rows sent to the LLM in a single extraction call.
ChunkBatch = list[ChunkRow]


ENTITY_TYPES: list[str] = [
    "MOVIE",
    "PERSON",
    "CHARACTER",
    "ACTOR",
    "DIRECTOR",
    "WRITER",
    "GENRE",
    "STUDIO",
    "CRITIC",
    "PUBLICATION",
    "CONCEPT",
    "LOCATION",
]


RELATIONSHIP_TYPES: list[str] = [
    "DIRECTED_BY",
    "WRITTEN_BY",
    "STARRED",
    "HAS_GENRE",
    "PRODUCED_BY",
    "REVIEWED_BY",
    "PUBLISHED_BY",
    "PRAISED",
    "CRITICIZED",
    "COMPARED_TO",
    "RELATED_TO",
]



_SYS_PROMPT_TEMPLATE = """
You are a Knowledge Graph Information Extraction system specialized in
movies, films, actors, directors, critics, reviews, and entertainment.

Your task is to extract a structured knowledge graph from the provided
movie-review chunks.

The graph consists of:
1. Entities (nodes)
2. Relationships between entities (edges)

Your extraction must be grounded strictly in the supplied text.

==================================================
ENTITY EXTRACTION
==================================================

Extract entities that are explicitly mentioned in the text and are useful
for representing the movie, people, organizations, concepts, opinions,
or other meaningful information contained in the text.

An entity should be:
- explicitly mentioned in the text, OR
- an unambiguous reference to an entity explicitly mentioned in the text.

Do NOT create entities from:
- generic nouns
- adjectives
- isolated descriptive words
- unsupported assumptions
- information from your own knowledge
- information not present in the input

Each entity MUST have exactly one entity type from the allowed list.

Allowed entity types:

{ENTITY_TYPES}

Do not invent new entity types.

==================================================
RELATIONSHIP EXTRACTION
==================================================

Extract relationships between entities.

A relationship MUST satisfy all of the following:

1. Both source and target entities exist in the extracted entity list.
2. The relationship is explicitly stated or directly supported by the text.
3. The relationship type belongs to the allowed relationship list.
4. The relationship direction is correct.
5. Do not infer relationships using outside knowledge.
6. Do not create a relationship merely because two entities occur
   in the same batch.

The batch provides context for entity resolution, NOT evidence of
relationships.

Allowed relationship types:

{RELATIONSHIP_TYPES}

Do not invent new relationship types.

The source and target fields MUST contain entity names,
NOT entity types.

Example:

Correct:

{{
    "source": "The Lion King",
    "target": "Jon Favreau",
    "type": "DIRECTED_BY"
}}

Incorrect:

{{
    "source": "MOVIE",
    "target": "PERSON",
    "type": "DIRECTED_BY"
}}

==================================================
RELATIONSHIP GROUNDING
==================================================

Only extract relationships supported by the supplied text.

For example:

Text:
"Jon Favreau directed The Lion King."

Extract:

{{
    "source": "The Lion King",
    "target": "Jon Favreau",
    "type": "DIRECTED_BY"
}}

If the text only says:

"Jon Favreau and The Lion King are both mentioned in this review."

Do NOT infer a DIRECTED_BY relationship.

==================================================
ENTITY RESOLUTION
==================================================

The supplied chunks may belong to the same movie.

Use the surrounding chunks to resolve obvious references.

For example:

Chunk 1:
"The Lion King features Donald Glover."

Chunk 2:
"The actor delivers a strong performance."

If "the actor" clearly refers to Donald Glover based on the supplied
context, resolve the reference to Donald Glover.

Do not resolve ambiguous references.

The canonical movie title supplied in the input should be used when
resolving references such as:

- the movie
- the film
- this film
- the picture

==================================================
DUPLICATES
==================================================

Do not return the same entity multiple times.

If the same entity appears across multiple chunks, return it once.

For example:

Chunk 1:
"Jon Favreau directed the film."

Chunk 2:
"Favreau's direction was praised."

Return:

{{
    "name": "Jon Favreau",
    "type": "PERSON"
}}

only once.

==================================================
CROSS-CHUNK RELATIONSHIPS
==================================================

A relationship may use information from multiple chunks if the
relationship can be directly established from the supplied text.

However, mentioning two entities in different chunks is NOT sufficient
evidence of a relationship.

Every relationship must be supported by one or more specific chunks.

The source_chunk_id field must identify the chunk containing the
supporting evidence.

==================================================
OUTPUT
==================================================

Return ONLY structured data matching the required schema.

Return:

{{
    "entities": [
        {{
            "name": "entity name",
            "type": "ENTITY_TYPE"
        }}
    ],
    "relationships": [
        {{
            "source": "source entity name",
            "target": "target entity name",
            "type": "RELATIONSHIP_TYPE",
            "source_chunk_id": 123
        }}
    ]
}}

If no entities are found:

{{
    "entities": [],
    "relationships": []
}}

If entities are found but no relationships are supported:

{{
    "entities": [...],
    "relationships": []
}}

==================================================
FINAL VALIDATION
==================================================

Before returning the result, verify:

- Every entity type is in the allowed entity type list.
- Every relationship type is in the allowed relationship list.
- Every relationship source exists in the entity list.
- Every relationship target exists in the entity list.
- No duplicate entities exist.
- No unsupported relationships were inferred.
- Relationships are grounded in the supplied chunks.
- source_chunk_id refers to a supplied chunk.
- No outside knowledge was introduced.
"""


SYS_PROMPT = _SYS_PROMPT_TEMPLATE.format(
    ENTITY_TYPES=", ".join(ENTITY_TYPES),
    RELATIONSHIP_TYPES=", ".join(RELATIONSHIP_TYPES),
)



agent = get_agent(
    GraphExtraction,
    SYS_PROMPT,
)
conn = get_postgres_connection()
def fetch_chunks() -> list[ChunkRow]:
    """
    Fetch all chunks ordered by document and chunk position.

    Returns rows containing:
        document_id
        movie_title
        chunk_id
        chunk_index
        content
        token_count
    """

    query = """
        SELECT
            d.id AS document_id,
            d.title AS movie_title,
            c.id AS chunk_id,
            c.chunk_index,
            c.content,
            c.token_count
        FROM document d
        JOIN chunk c
            ON c.document_id = d.id
        ORDER BY
            d.id,
            c.chunk_index;
    """

    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute(query)
        return cursor.fetchall()



def group_chunks_by_document(
    rows: Sequence[ChunkRow],
) -> dict[int, ChunkBatch]:
    """
    Group chunks by document/movie.

    The document_id is used as the grouping key rather than movie title.
    """

    documents: dict[int, ChunkBatch] = defaultdict(list)

    for row in rows:
        documents[row["document_id"]].append(row)

    return documents



def create_batches(
    chunks: Sequence[ChunkRow],
    max_chunks: int = MAX_CHUNKS_PER_BATCH,
    max_tokens: int = MAX_BATCH_TOKENS,
) -> Iterator[ChunkBatch]:
    """
    Create token-aware batches while keeping chunks from the same
    document together.

    A batch is closed when either:
        - max_chunks is reached, or
        - max_tokens would be exceeded.
    """

    batch: ChunkBatch = []
    current_tokens = 0

    for chunk in chunks:

        chunk_tokens = chunk["token_count"] or 0

        # If adding this chunk would exceed the token limit,
        # emit the current batch first.
        if (
            batch
            and (
                len(batch) >= max_chunks
                or current_tokens + chunk_tokens > max_tokens
            )
        ):
            yield batch

            batch = []
            current_tokens = 0

        batch.append(chunk)
        current_tokens += chunk_tokens

    if batch:
        yield batch


def build_batch_input(
    movie_title: str,
    batch: Sequence[ChunkRow],
) -> str:
    """
    Convert a batch of database rows into a clearly structured
    LLM input.
    """

    parts = [
        f"MOVIE: {movie_title}",
        "",
        "The following chunks belong to this movie.",
        "",
    ]

    for chunk in batch:
        parts.append(
            f"CHUNK_ID: {chunk['chunk_id']}\n"
            f"CHUNK_INDEX: {chunk['chunk_index']}\n"
            f"TEXT:\n{chunk['content']}\n"
        )

    return "\n".join(parts)


def extract_graph_from_batch(
    movie_title: str,
    batch: Sequence[ChunkRow],
) -> GraphExtraction:
    """
    Extract entities and relationships from one batch of chunks.
    """

    prompt = build_batch_input(
        movie_title,
        batch,
    )

    result = agent.invoke(prompt)

    return result

# validates entities and relationships

def validate_extraction(
    result: GraphExtraction,
    batch: Sequence[ChunkRow],
) -> None:
    """
    Perform application-level validation in addition to LLM/Pydantic
    validation.
    """

    valid_entity_types = set(ENTITY_TYPES)
    valid_relationship_types = set(RELATIONSHIP_TYPES)

    valid_chunk_ids = {
        chunk["chunk_id"]
        for chunk in batch
    }

    entity_names = {
        entity.name
        for entity in result.entities
    }


    for entity in result.entities:

        if entity.type not in valid_entity_types:
            raise ValueError(
                f"Invalid entity type: {entity.type}"
            )


    for relationship in result.relationships:

        if relationship.type not in valid_relationship_types:
            raise ValueError(
                f"Invalid relationship type: "
                f"{relationship.type}"
            )

        if relationship.source not in entity_names:
            raise ValueError(
                f"Relationship source does not exist: "
                f"{relationship.source}"
            )

        if relationship.target not in entity_names:
            raise ValueError(
                f"Relationship target does not exist: "
                f"{relationship.target}"
            )

        if relationship.source_chunk_id not in valid_chunk_ids:
            raise ValueError(
                f"Invalid source_chunk_id: "
                f"{relationship.source_chunk_id}"
            )

def extract_graph() -> None:
    """
    Main graph extraction pipeline.

    Flow:

        PostgreSQL
            ↓
        Group by movie
            ↓
        15-chunk batches
            ↓
        LLM extraction
            ↓
        Validation
    """

    rows: list[ChunkRow] = fetch_chunks()

    documents: dict[int, ChunkBatch] = group_chunks_by_document(rows)

    for document_id, chunks in documents.items():

        movie_title = chunks[0]["movie_title"]

        print(
            f"Processing movie: {movie_title} "
            f"(document_id={document_id})"
        )

        batches = create_batches(chunks)

        for batch_number, batch in enumerate(
            batches,
            start=1,
        ):

            print(
                f"  Processing batch {batch_number}: "
                f"{len(batch)} chunks"
            )

            result = extract_graph_from_batch(
                movie_title,
                batch,
            )

            validate_extraction(
                result,
                batch,
            )

            print(
                f"    Entities: "
                f"{len(result.entities)}"
            )

            print(
                f"    Relationships: "
                f"{len(result.relationships)}"
            )

            # Database persistence comes next.
            #
            # save_entities(...)
            # save_relationships(...)