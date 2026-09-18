from dataclasses import dataclass, Field
from typing import Any
import numpy as np

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

@dataclass
class Entity:
    type:str
    name:str
    description:str | None =None

