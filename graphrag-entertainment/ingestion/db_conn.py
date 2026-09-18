import logging
import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def get_postgres_connection():
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    dbname = os.getenv("POSTGRES_DB", "graphrag")
    logger.info("Connecting to postgres://%s:%s/%s", host, port, dbname)
    return psycopg.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
    )


