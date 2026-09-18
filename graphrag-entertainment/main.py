import logging

from fastapi import FastAPI

from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
async def root():
    logger.debug("GET /")
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    logger.info("GET /hello/%s", name)
    return {"message": f"Hello {name}"}
