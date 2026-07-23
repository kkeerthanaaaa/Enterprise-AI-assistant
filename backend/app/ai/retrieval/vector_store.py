import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import DocumentChunk, Document
from app.ai.embeddings.embedder import get_embedder


def similarity_search(
    db: Session,
    company_id: uuid.UUID,
    query: str,
    top_k: int = 6,
    department_id: uuid.UUID | None = None,
) -> list[dict]:
    """Cosine-similarity search over document_chunks, HARD-scoped to
    company_id. department_id is optional extra scoping (e.g. department SOPs
    should not leak to other departments) but company_id is never optional.
    """
    embedder = get_embedder()
    query_vec = embedder.embed_one(query)

    stmt = (
        select(
            DocumentChunk,
            Document.title,
            Document.doc_type,
            DocumentChunk.embedding.cosine_distance(query_vec).label("distance"),
        )
        .join(Document, Document.id == DocumentChunk.document_id)
        .where(DocumentChunk.company_id == company_id)  # <-- tenant isolation, non-negotiable
        .where(Document.is_active.is_(True))
        .order_by("distance")
        .limit(top_k)
    )

    rows = db.execute(stmt).all()
    results = []
    for chunk, title, doc_type, distance in rows:
        results.append(
            {
                "document_id": chunk.document_id,
                "title": title,
                "doc_type": doc_type,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "score": 1 - float(distance),
            }
        )
    return results
