import uuid
from datetime import datetime
from pydantic import BaseModel

from app.models.enums import DocumentType, DocumentStatus


class DocumentOut(BaseModel):
    id: uuid.UUID
    title: str
    doc_type: DocumentType
    original_filename: str
    version: int
    status: DocumentStatus
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    conversation_id: uuid.UUID | None = None
    message: str


class Citation(BaseModel):
    document_id: uuid.UUID
    title: str
    doc_type: DocumentType
    chunk_index: int
    snippet: str


class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    answer: str
    citations: list[Citation]
    used_sql_context: bool
    used_business_rules: bool
