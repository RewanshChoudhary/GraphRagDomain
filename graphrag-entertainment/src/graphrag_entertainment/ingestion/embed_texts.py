import logging

from sentence_transformers import SentenceTransformer

from .models import Chunk
from .token_counter import EMBEDDING_MODEL_NAME

logger = logging.getLogger(__name__)
model = SentenceTransformer(EMBEDDING_MODEL_NAME)

def embed_text(chunks: list[Chunk]) -> list[list[float]]:
    logger.info("Embedding %d chunks", len(chunks))


    valid_texts = [
        chunk.content for chunk in chunks
        if chunk is not None and chunk.content != ""
    ]

    embeddings = model.encode(valid_texts)
    logger.info("Embeddings shape: %s", embeddings.shape)

    return embeddings.tolist()






