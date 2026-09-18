from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field


@dataclass
class Document:
    title: str
    content: str
    metadata: dict[str, Any]
@dataclass
class Chunk:
    document_id: int
    chunk_index: int
    content: str
    token_count: int | None = None
    start_sentence:int | None = None
    end_sentence:int | None = None
    vector: list[float] | None = None



class Entity(BaseModel):
    name: str
    type: str


class Relationship(BaseModel):
    source: str
    target: str
    type: str
    source_chunk_id: int | None = None


class GraphExtraction(BaseModel):
    entities: list[Entity] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)