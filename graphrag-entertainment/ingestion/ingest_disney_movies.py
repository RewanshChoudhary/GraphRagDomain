import math

import pandas as pd

from ingestion.chunking_documents import chunk_document, insert_chunk
from ingestion.db_conn import get_postgres_connection
from ingestion.document_store import insert_documents
from ingestion.models import Document

CSV_PATH = (
    "/home/rewansh57/Programming/GraphRagForMovies/"
    "graphrag-entertainment/movies_with_reviews_cleaned.csv"
)


def ensure_schema():
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS document (
                    id BIGSERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata JSONB,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS chunk (
                    id BIGSERIAL PRIMARY KEY,
                    document_id BIGINT NOT NULL
                        REFERENCES document(id) ON DELETE CASCADE,
                    chunk_index INT NOT NULL,
                    content TEXT NOT NULL,
                    token_count INT,
                    UNIQUE(document_id, chunk_index)
                )
            """)

        conn.commit()

    finally:
        conn.close()


def load_disney_movies(csv_path: str) -> pd.DataFrame:
    df:pd.DataFrame = pd.read_csv(csv_path)

    # Remove the pandas index column if it exists
    df:pd.DataFrame = df.drop(columns=["Unnamed: 0"], errors="ignore")

    # Make filtering safe when production_company contains NaN
    df["production_company"] = (
        df["production_company"]
        .fillna("")
        .astype(str)
    )

    disney_df = df[
        df["production_company"]
        .str.contains("Disney", case=False, na=False)
    ]

  
    disney_df:pd.DataFrame = disney_df.dropna(
        subset=["movie_title", "review_content"]
    )

    disney_df = disney_df[
        disney_df["review_content"]
        .astype(str)
        .str.strip()
        != ""
    ]

    print(
        f"Found {len(disney_df)} Disney review rows "
        f"across {disney_df['movie_title'].nunique()} movies"
    )

    return disney_df


def sanitize_metadata(metadata: dict) -> dict:
    return {
        key: (
            None
            if isinstance(value, float) and math.isnan(value)
            else value
        )
        for key, value in metadata.items()
    }


def build_documents(df: pd.DataFrame) -> list[Document]:
    documents = []

    for _, row in df.iterrows():

        content = row.get("review_content", "")

        if pd.isna(content) or not (content).strip():
            continue

        critic = row.get("critic_name", "Unknown")
        movie_title = row.get("movie_title", "")

        title = f"{movie_title} - {critic}"

        metadata = sanitize_metadata({
            "movie_title": movie_title,
            "critic_name": critic,
            "publisher_name": row.get("publisher_name", ""),
            "review_type": row.get("review_type", ""),
            "review_score": str(row.get("review_score", "")),
            "review_date": str(row.get("review_date", "")),
            "production_company": row.get("production_company", ""),
            "genres": row.get("genres", ""),
            "directors": row.get("directors", ""),
            "actors": row.get("actors", ""),
            "content_rating": row.get("content_rating", ""),
            "runtime": str(row.get("runtime", "")),
            "original_release_date": str(
                row.get("original_release_date", "")
            ),
            "tomatometer_status": row.get(
                "tomatometer_status", ""
            ),
            "tomatometer_rating": str(
                row.get("tomatometer_rating", "")
            ),
            "audience_status": row.get(
                "audience_status", ""
            ),
            "audience_rating": str(
                row.get("audience_rating", "")
            ),
        })

        documents.append(
            Document(
                title=title,
                content=str(content),
                metadata=metadata
            )
        )

    print(f"Built {len(documents)} document objects")

    return documents


def ingest_documents_and_chunks(documents: list[Document]):
    conn = get_postgres_connection()

    try:

        for document in documents:
            document_id = insert_documents(
                conn,
                document
            )[0]

            chunks = chunk_document(
            document,
            document_id
            )

       

            for chunk in chunks:
                insert_chunk(
                    conn,
                    chunk
                )
        conn.commit()

        print(
            f"Successfully inserted "
            f"{len(documents)} documents and their chunks"
        )

    except Exception:

       
        conn.rollback()

        raise

    finally:

        conn.close()


def main():


    ensure_schema()

    df = load_disney_movies(CSV_PATH)

    documents = build_documents(df)

    ingest_documents_and_chunks(documents)


if __name__ == "__main__":
    main()
