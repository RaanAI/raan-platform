"""Knowledge base search endpoints."""

from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import KnowledgeBaseChunk
from ..utils.db import get_session
from ..vector_store import qdrant

router = APIRouter(prefix="/kb", tags=["knowledge_base"])
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


class SearchQuery(BaseModel):
    tenant_id: str
    query: str
    top_k: int = 5


class SearchChunk(BaseModel):
    doc_id: str
    text: str
    score: float


@router.post("/search", response_model=List[SearchChunk])
async def search_kb(params: SearchQuery, session: AsyncSession = Depends(get_session)):
    embedding = model.encode(params.query).tolist()
    results = await qdrant.query_embeddings(
        embedding,
        top_k=params.top_k,
        filter_={"must": [{"key": "tenant_id", "match": {"value": params.tenant_id}}]},
    )
    chunks: list[SearchChunk] = []
    for point in results:
        result = await session.execute(select(KnowledgeBaseChunk).where(KnowledgeBaseChunk.embedding_id == point.id))
        chunk = result.scalars().first()
        if not chunk:
            continue
        chunks.append(SearchChunk(doc_id=str(chunk.doc_id), text=chunk.text, score=point.score))
    return chunks
