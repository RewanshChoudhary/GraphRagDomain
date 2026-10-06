# graphrag-entertainment

An experimental GraphRAG application for entertainment reviews. The current
implementation provides PostgreSQL-backed document and chunk ingestion, text
embedding, an ordinary RAG experiment, and model schemas for a broader graph
pipeline.

## Setup

1. Copy `.env.example` to `.env` and fill in the LLM settings you plan to use.
2. Start PostgreSQL and pgAdmin with `docker compose up -d`.
3. Install dependencies with `uv sync`.
4. Apply `db/schema.sql` to the configured PostgreSQL database, then run the
   ingestion entry point in `src/graphrag_entertainment/ingestion/` as needed.

The CLI entry point is `graphrag-entertainment`. Run the HTTP application with
`uv run graphrag-entertainment`.

## Repository layout

- `data/raw/` and `data/processed/` hold source and derived datasets.
- `db/` contains the PostgreSQL schema and future migrations.
- `src/graphrag_entertainment/` contains the Python package.
- `experiments/` contains exploratory retrieval implementations.
- `notebooks/` contains exploration notebooks.
- `tests/` is organized by unit and integration test area.

The raw `movies_with_reviews.csv` dataset was not included in this checkout.
The cleaned dataset is kept under `data/processed/`.
