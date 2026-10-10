import logging
import os

import psycopg
from dotenv import load_dotenv
from neo4j import Driver, GraphDatabase

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


def get_neo4j_driver() -> Driver:
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    logger.info("Connecting to Neo4j at %s", uri)
    driver = GraphDatabase.driver(
        uri,
        auth=(user, os.getenv("NEO4J_PASSWORD", "graphrag")),
    )
    try:
        driver.verify_connectivity()
    except Exception:
        driver.close()
        raise
    return driver



