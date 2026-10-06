"""Pydantic data models for the Movie GraphRAG system.

These classes define the entities that flow through the GraphRAG pipeline:

* **Ingestion** - :class:`Document` and :class:`Chunk`
* **Graph extraction** - :class:`Entity`, :class:`EntityMention`,
  :class:`Relationship`, :class:`Claim`
* **Community layer** - :class:`Community` and :class:`CommunitySummary`
* **Question answering** - :class:`Query` and :class:`QueryCommunityAnswer`

All primary keys are plain strings so they can be UUIDs, URL hashes, or
database-generated keys. A fresh UUID string is generated automatically
whenever an ``id`` is not supplied.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


def new_id() -> str:
    """Return a fresh UUID string, used as the default primary key."""
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """Return the current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


class EntityType(StrEnum):
    """The kind of entity stored in the graph (also used as node labels)."""

    ACTOR = "ACTOR"
    DIRECTOR = "DIRECTOR"
    FRANCHISE = "FRANCHISE"
    STUDIO = "STUDIO"
    FILM = "FILM"
    CRITIC = "CRITIC"
    PUBLICATION = "PUBLICATION"


class Document(BaseModel):
    """A source document (news article, review, press release, ...) ingested into the pipeline."""

    id: str = Field(default_factory=new_id, description="Primary key of the document")
    title: str = Field(description="Headline / title of the document")
    source_url: str = Field(description="Canonical URL where the document was found")
    publication: str | None = Field(default=None, description="Publication or outlet name (if known)")
    author: str | None = Field(default=None, description="Author name (if known)")
    published_date: date | None = Field(default=None, description="Publication date (if known)")
    raw_text: str = Field(description="Full unprocessed text of the document")


class Chunk(BaseModel):
    """A fixed-size text chunk cut from a :class:`Document` during preprocessing."""

    id: str = Field(default_factory=new_id, description="Primary key of the chunk")
    document_id: str = Field(description="Foreign key to the parent document")
    text: str = Field(description="Chunk text content")
    token_count: int = Field(ge=0, description="Number of tokens in this chunk")
    chunk_index: int = Field(ge=0, description="Zero-based position of the chunk within its document")


class Entity(BaseModel):
    """A canonical graph node, e.g. a film, actor, studio, critic, or publication."""

    id: str = Field(default_factory=new_id, description="Primary key of the entity")
    name: str = Field(description="Display name of the entity")
    type: EntityType = Field(description="Node label / type of the entity")
    description: str = Field(description="Canonical (aggregated) description of the entity")


class EntityMention(BaseModel):
    """A raw, pre-aggregation mention of an entity inside a single chunk.

    Identified by the composite key ``(entity_id, chunk_id)`` - there is no
    dedicated ``id`` field.
    """

    entity_id: str = Field(description="Foreign key to the referenced entity")
    chunk_id: str = Field(description="Foreign key to the chunk containing the mention")
    raw_description: str = Field(description="Description text as found verbatim in the chunk")


class Relationship(BaseModel):
    """A directed, weighted edge between two entities."""

    id: str = Field(default_factory=new_id, description="Primary key of the relationship")
    source_entity_id: str = Field(description="Foreign key to the source entity")
    target_entity_id: str = Field(description="Foreign key to the target entity")
    description: str = Field(description="Human-readable description of the relationship")
    weight: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence weight in [0, 1]")


class Claim(BaseModel):
    """A factual statement about an entity, traced back to a source chunk."""

    id: str = Field(default_factory=new_id, description="Primary key of the claim")
    entity_id: str = Field(description="Foreign key to the subject entity")
    description: str = Field(description="Text of the claim")
    source_chunk_id: str = Field(description="Foreign key to the chunk the claim was extracted from")


class Community(BaseModel):
    """A community in the hierarchical (e.g. Leiden) clustering of the entity graph."""

    id: str = Field(default_factory=new_id, description="Primary key of the community")
    level: int = Field(ge=0, description="Hierarchy level (0 = most granular)")
    parent_community_id: str | None = Field(
        default=None, description="Parent community at the coarser level; None for the root"
    )
    entity_ids: list[str] = Field(default_factory=list, description="Entities contained in this community")


class CommunitySummary(BaseModel):
    """An LLM-generated summary report for a single community."""

    community_id: str = Field(description="Foreign key to the summarized community")
    title: str = Field(description="Short headline for the community")
    summary: str = Field(description="Natural-language summary generated by the LLM")
    rating: float = Field(description="Rating / usefulness score assigned by the LLM")
    findings_json: dict[str, Any] = Field(default_factory=dict, description="Structured findings (free-form JSON)")


class Query(BaseModel):
    """A user question and its final synthesized answer."""

    id: str = Field(default_factory=new_id, description="Primary key of the query")
    question: str = Field(description="User question text")
    answer: str = Field(description="Final synthesized answer text")
    created_at: datetime = Field(default_factory=utc_now, description="UTC timestamp when the query was created")


class QueryCommunityAnswer(BaseModel):
    """A partial answer contributed by a single community during global search.

    Identified by the composite key ``(query_id, community_id)`` - there is no
    dedicated ``id`` field.
    """

    query_id: str = Field(description="Foreign key to the parent query")
    community_id: str = Field(description="Foreign key to the contributing community")
    partial_answer: str = Field(description="Partial answer text produced by this community")
    helpfulness_score: float = Field(
        ge=0.0, le=1.0, description="Predicted helpfulness of the partial answer in [0, 1]"
    )


__all__ = [
    "EntityType",
    "Document",
    "Chunk",
    "Entity",
    "EntityMention",
    "Relationship",
    "Claim",
    "Community",
    "CommunitySummary",
    "Query",
    "QueryCommunityAnswer",
    "new_id",
    "utc_now",
]