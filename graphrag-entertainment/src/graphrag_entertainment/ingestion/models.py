from dataclasses import dataclass
from typing import Any


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
    id: int | None = None
