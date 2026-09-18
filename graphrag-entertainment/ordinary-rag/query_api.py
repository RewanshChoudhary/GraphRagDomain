import logging

from fastapi import FastAPI

from process_query import process_query
from query_extract import extract_answer

app = FastAPI()
logger = logging.getLogger(__name__)


@app.post("/api/create/{query}")
async def get_query(query: str):
    logger.info("received query: %s", query)

    context = process_query(query)
    result = extract_answer(query, context)

    return result
