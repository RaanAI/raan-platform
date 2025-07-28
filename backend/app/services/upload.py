"""Document ingestion and embedding service."""

import io
from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile
from sentence_transformers import SentenceTransformer
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Document, KnowledgeBaseChunk
from ..utils.db import get_session
from ..vector_store import qdrant

router = APIRouter(prefix="/upload", tags=["upload"])
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


async def extract_text(file: UploadFile) -> str:
    if file.content_type == "application/pdf":
        from pdfminer.high_level import extract_text

        data = await file.read()
        with io.BytesIO(data) as fh:
            text = extract_text(fh)
    else:
        data = await file.read()
        text = data.decode("utf-8", errors="ignore")
    return text


def chunk_text(text: str, size: int = 500) -> list[str]:
    words = text.split()
    chunks = [" ".join(words[i : i + size]) for i in range(0, len(words), size)]
    return chunks


@router.post("/{tenant_id}")
async def upload_document(
    tenant_id: str,
    user_id: str,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    text = await extract_text(file)
    chunks = chunk_text(text)
    document = Document(
        tenant_id=tenant_id,
        user_id=user_id,
        filename=file.filename,
        content_type=file.content_type or "text/plain",
    )
    session.add(document)
    await session.commit()
    await session.refresh(document)

    embeddings = model.encode(chunks).tolist()
    metadatas = []
    for chunk_text in chunks:
        emb_id = str(uuid4())
        metadatas.append(
            {
                "embedding_id": emb_id,
                "tenant_id": tenant_id,
                "doc_id": str(document.id),
                "user_id": user_id,
                "agent_id": None,
            }
        )
        session.add(
            KnowledgeBaseChunk(
                id=emb_id,
                tenant_id=tenant_id,
                doc_id=document.id,
                user_id=user_id,
                text=chunk_text,
                embedding_id=emb_id,
            )
        )
    await session.commit()

    await qdrant.upsert_embeddings(embeddings, metadatas)
    return {"document_id": document.id, "chunks": len(chunks)}
