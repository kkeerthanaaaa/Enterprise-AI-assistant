from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.deps import get_current_user, CurrentUser
from app.schemas.document import ChatRequest, ChatResponse
from app.ai.chat_pipeline import run_chat_pipeline

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    result = run_chat_pipeline(db, current_user, payload.message, payload.conversation_id)
    return ChatResponse(**result)
