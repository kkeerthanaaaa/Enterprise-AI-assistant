import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.deps import get_current_user, require_role, CurrentUser
from app.models.enums import RoleEnum, DocumentType, DocumentStatus
from app.models.document import Document
from app.schemas.document import DocumentOut
from app.services.document_service import save_upload, process_document

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentOut, dependencies=[Depends(require_role(RoleEnum.HR))])
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    doc_type: DocumentType = Form(DocumentType.OTHER),
    department_id: uuid.UUID | None = Form(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    content = file.file.read()
    file_path = save_upload(current_user.company_id, file.filename, content)

    document = Document(
        id=uuid.uuid4(),
        company_id=current_user.company_id,
        department_id=department_id,
        uploaded_by=current_user.id,
        title=title,
        doc_type=doc_type,
        file_path=file_path,
        original_filename=file.filename,
        mime_type=file.content_type or "text/plain",
        status=DocumentStatus.PROCESSING,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    # In production: dispatch to a queue (Celery/RQ) instead of BackgroundTasks
    background_tasks.add_task(process_document, db, document)

    return document


@router.get("", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    return (
        db.query(Document)
        .filter(Document.company_id == current_user.company_id, Document.is_active.is_(True))
        .order_by(Document.created_at.desc())
        .all()
    )


@router.delete("/{document_id}", dependencies=[Depends(require_role(RoleEnum.HR))])
def delete_document(document_id: uuid.UUID, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    doc = (
        db.query(Document)
        .filter(Document.id == document_id, Document.company_id == current_user.company_id)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc.is_active = False
    db.commit()
    return {"status": "archived"}
