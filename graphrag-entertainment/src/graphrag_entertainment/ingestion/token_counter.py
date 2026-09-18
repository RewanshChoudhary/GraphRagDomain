import logging

from transformers import AutoTokenizer

logger = logging.getLogger(__name__)

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_tokenizer = None


def get_tokenizer():
    """Return the lazily loaded tokenizer used by the embedding model."""
    global _tokenizer

    if _tokenizer is None:
        logger.info("Loading tokenizer for %s", EMBEDDING_MODEL_NAME)
        _tokenizer = AutoTokenizer.from_pretrained(
            EMBEDDING_MODEL_NAME,
            use_fast=True,
        )

    return _tokenizer


def count_tokens(text: str | None) -> int:
    """Count the content tokens in ``text`` using the embedding tokenizer.

    Special tokens (e.g. ``[CLS]`` / ``[SEP]``) are excluded so the count
    reflects the chunk content only. Empty or missing text counts as ``0``.
    """
    if not text:
        return 0

    return len(
        get_tokenizer().encode(text, add_special_tokens=False)
    )
