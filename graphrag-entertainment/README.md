# graphrag-entertainment

Python project for ingesting entertainment reviews and experimenting with
ordinary RAG and knowledge graph extraction.

## Setup

From this directory, copy `.env.example` to `.env`, configure the services you
use, start PostgreSQL with `docker compose up -d`, and install dependencies
with `uv sync`. Apply `db/schema.sql` to PostgreSQL before ingesting data.

## Where things live

| Location | Purpose |
| --- | --- |
| `src/graphrag_entertainment/ingestion/` | Read reviews, chunk text, create embeddings, and store documents/chunks in PostgreSQL. |
| `src/graphrag_entertainment/graph/` | Graph extraction and graph database pipelines. |
| `src/graphrag_entertainment/models/` | Shared database and LLM response schemas. |
| `src/graphrag_entertainment/main.py` | FastAPI application entry point. |
| `experiments/ordinary_rag/` | Ordinary RAG experiment scripts. |
| `tests/integration/api_requests.http` | HTTP requests for manual API exploration. |
| `data/` | Raw input and processed datasets. |
| `db/` | PostgreSQL schema and migrations. |

There are two graph pipelines under `graph/`: `extraction.py` batches and
validates model output from PostgreSQL chunks; `neo4j_pipeline.py` extracts
individual chunks and writes results to Neo4j. The first currently stops
before database persistence.

`ingestion/models.py` contains dataclasses shaped for PostgreSQL row handling;
`models/` contains the Pydantic schemas used for graph extraction and LLM data.

The cleaned review dataset is `data/processed/movies_with_reviews_cleaned.csv`.
The original raw CSV was not present in this checkout.
