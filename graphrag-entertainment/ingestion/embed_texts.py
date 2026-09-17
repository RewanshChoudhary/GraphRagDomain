import logging

import numpy as np

from ingestion.models import Chunk


def embed_text(chunks:list[Chunk])->list[list[float]]:
    model = SentenceTransformer("all-MiniLM-L6-v2")

    valid_texts=[
        chunk.content for chunk in chunks
        if chunk is not None and chunk.content !=""
    ]

    embeddings=model.encode(valid_texts)
    logging.info(f"Embeddings shape: {embeddings.shape}")

    return embeddings.tolist()







