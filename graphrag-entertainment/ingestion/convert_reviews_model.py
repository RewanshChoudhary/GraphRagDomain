from dataclasses import dataclass
from typing import Any


@dataclass
class Document:
    title: str
    content: str
    metadata: dict[str, Any]
# @dataclass
# class Chunk:
#     chunk_index:int
#     text