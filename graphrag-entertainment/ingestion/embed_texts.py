import logging


from sentence_transformers import SentenceTransformer

from ingestion.models import Chunk

logger = logging.getLogger(__name__)
model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(chunks: list[Chunk]) -> list[list[float]]:
    logger.info("Embedding %d chunks", len(chunks))


    valid_texts = [
        chunk.content for chunk in chunks
        if chunk is not None and chunk.content != ""
    ]

    embeddings = model.encode(valid_texts)
    logger.info("Embeddings shape: %s", embeddings.shape)

    return embeddings.tolist()







