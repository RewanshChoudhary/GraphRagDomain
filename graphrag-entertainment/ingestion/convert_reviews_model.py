from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class Document:
    title: str
    content: str
    metadata: dict[str, Any]


@dataclass
class Chunk:
    document_id: int = field(default=0)
    chunk_index: int = 0
    content: str = ""
    token_count: int = 0
    embedding: np.ndarray = field(default_factory=lambda: np.array([]))


