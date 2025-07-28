"""Qdrant client helper."""

from typing import Iterable

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qmodels

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "knowledge_base"

client = AsyncQdrantClient(url=QDRANT_URL)


async def ensure_collection(vector_size: int = 384) -> None:
    await client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=qmodels.VectorParams(size=vector_size, distance=qmodels.Distance.COSINE),
        optimizers_config=qmodels.OptimizersConfigDiff(memmap_threshold=20000),
        shard_number=1,
        init_from=None,
    )


async def upsert_embeddings(vectors: Iterable[list[float]], metadatas: list[dict]) -> None:
    points = [qmodels.PointStruct(id=meta["embedding_id"], vector=vec, payload=meta) for vec, meta in zip(vectors, metadatas)]
    await client.upsert(COLLECTION_NAME, points)


async def query_embeddings(query: list[float], top_k: int = 5, filter_: dict | None = None):
    result = await client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query,
        limit=top_k,
        query_filter=qmodels.Filter(**filter_) if filter_ else None,
    )
    return result
