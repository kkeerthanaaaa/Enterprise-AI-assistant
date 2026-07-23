import re
import uuid
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser
from app.models.company import Company
from app.models.conversation import Conversation, Message
from app.models.enums import LeaveType
from app.ai.retrieval.vector_store import similarity_search
from app.ai.retrieval.sql_context import get_employee_sql_context, get_direct_reports_context
from app.ai.rules.leave_rules import evaluate_leave_request
from app.ai.prompts.templates import (
    SYSTEM_PROMPT,
    CONTEXT_TEMPLATE,
    format_document_context,
    format_sql_context,
    format_rule_context,
)
from app.ai.llm import get_llm_client

LEAVE_TYPE_KEYWORDS = {
    "sick": LeaveType.SICK,
    "maternity": LeaveType.MATERNITY,
    "paternity": LeaveType.PATERNITY,
    "unpaid": LeaveType.UNPAID,
    "wfh": LeaveType.WFH,
    "work from home": LeaveType.WFH,
    "annual": LeaveType.ANNUAL,
    "leave": LeaveType.ANNUAL,  # default fallback
}

DAYS_PATTERN = re.compile(r"(\d+)\s*day", re.IGNORECASE)


def _detect_leave_intent(message: str) -> LeaveType | None:
    lowered = message.lower()
    if "leave" not in lowered and "wfh" not in lowered and "work from home" not in lowered:
        return None
    for kw, ltype in LEAVE_TYPE_KEYWORDS.items():
        if kw in lowered:
            return ltype
    return None


def _estimate_date_range(message: str) -> tuple[date, date] | None:
    """Very lightweight heuristic date extraction so the demo pipeline can run
    the business rule engine on natural language like 'take 7 days leave next
    week'. A production system should use a proper NL date parser (e.g.
    duckling, dateparser) here -- swap this function out for that."""
    lowered = message.lower()
    match = DAYS_PATTERN.search(lowered)
    num_days = int(match.group(1)) if match else 1

    today = date.today()
    if "next week" in lowered:
        start = today + timedelta(days=(7 - today.weekday()))
    elif "tomorrow" in lowered:
        start = today + timedelta(days=1)
    else:
        start = today + timedelta(days=3)
    end = start + timedelta(days=max(num_days - 1, 0))
    return start, end


def _get_or_create_conversation(db: Session, current_user: CurrentUser, conversation_id: uuid.UUID | None) -> Conversation:
    if conversation_id:
        convo = (
            db.query(Conversation)
            .filter(Conversation.id == conversation_id, Conversation.company_id == current_user.company_id, Conversation.user_id == current_user.id)
            .first()
        )
        if convo:
            return convo
    convo = Conversation(company_id=current_user.company_id, user_id=current_user.id, title="New conversation")
    db.add(convo)
    db.commit()
    db.refresh(convo)
    return convo


def _recent_history_text(db: Session, convo: Conversation, limit: int = 6) -> str:
    msgs = (
        db.query(Message)
        .filter(Message.conversation_id == convo.id)
        .order_by(Message.created_at.desc())
        .limit(limit)
        .all()
    )
    msgs.reverse()
    return "\n".join(f"{m.role}: {m.content}" for m in msgs) or "(no prior messages)"


def run_chat_pipeline(db: Session, current_user: CurrentUser, message: str, conversation_id: uuid.UUID | None):
    """The 7-step retrieval pipeline described in the spec:
    1. Auth is already resolved (current_user, from JWT dependency)
    2. company/department/role are on current_user
    3. retrieve relevant documents (vector search, tenant-scoped)
    4. retrieve employee info from SQL (tenant + self scoped)
    5. combine context (+ business rule evaluation when relevant)
    6. LLM reasoning
    7. return personalized answer with citations
    """
    company = db.query(Company).filter(Company.id == current_user.company_id).first()

    convo = _get_or_create_conversation(db, current_user, conversation_id)
    history_text = _recent_history_text(db, convo)

    # Step 3: document retrieval
    doc_chunks = similarity_search(db, current_user.company_id, message, top_k=6, department_id=current_user.department_id)

    # Step 4: SQL context
    sql_context = get_employee_sql_context(db, current_user)
    if current_user.role.value in ("manager", "hr", "admin"):
        sql_context.update(get_direct_reports_context(db, current_user))

    # Step 5: business rule engine, only triggered for leave-shaped questions
    rule_eval = None
    used_business_rules = False
    leave_type = _detect_leave_intent(message)
    if leave_type:
        start, end = _estimate_date_range(message)
        rule_eval = evaluate_leave_request(db, current_user.company_id, current_user.id, leave_type, start, end)
        used_business_rules = True

    system_prompt = SYSTEM_PROMPT.format(
        company_name=company.name if company else "your company",
        full_name=current_user.full_name,
        role=current_user.role.value,
    )
    user_context = CONTEXT_TEMPLATE.format(
        document_context=format_document_context(doc_chunks),
        sql_context=format_sql_context(sql_context),
        rule_context=format_rule_context(rule_eval),
        history=history_text,
        question=message,
    )

    # Step 6: LLM reasoning
    llm = get_llm_client()
    answer = llm.chat(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_context},
        ]
    )

    citations = [
        {
            "document_id": str(c["document_id"]),
            "title": c["title"],
            "doc_type": c["doc_type"].value if hasattr(c["doc_type"], "value") else c["doc_type"],
            "chunk_index": c["chunk_index"],
            "snippet": c["content"][:280],
        }
        for c in doc_chunks[:3]
    ]

    # Step 7: persist + return
    db.add(Message(conversation_id=convo.id, role="user", content=message))
    db.add(Message(conversation_id=convo.id, role="assistant", content=answer, citations=citations))
    db.commit()

    return {
        "conversation_id": convo.id,
        "answer": answer,
        "citations": citations,
        "used_sql_context": bool(sql_context),
        "used_business_rules": used_business_rules,
    }
