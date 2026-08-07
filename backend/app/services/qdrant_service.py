import os
import uuid

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)


load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

COLLECTION_NAME = "study_companion"
VECTOR_SIZE = 768


if not QDRANT_URL:
    raise ValueError("QDRANT_URL is missing from .env")

if not QDRANT_API_KEY:
    raise ValueError("QDRANT_API_KEY is missing from .env")


client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)


def ensure_collection():
    """Create the Qdrant collection if it does not already exist."""

    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            ),
        )


def store_chunks(
    chunks: list[str],
    embeddings: list[list[float]],
    filename: str
) -> int:
    """Store document chunks and embeddings in Qdrant."""

    ensure_collection()

    points = []

    for index, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "text": chunk,
                "filename": filename,
                "chunk_index": index
            }
        )

        points.append(point)

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    return len(points)

def search_chunks(
    query_embedding: list[float],
    limit: int = 3
) -> list[dict]:
    """Search Qdrant and return the most relevant document chunks."""

    ensure_collection()

    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=limit,
        with_payload=True
    )

    results = []

    for point in response.points:
        payload = point.payload or {}

        results.append({
            "score": point.score,
            "text": payload.get("text", ""),
            "filename": payload.get("filename", ""),
            "chunk_index": payload.get("chunk_index")
        })

    return results