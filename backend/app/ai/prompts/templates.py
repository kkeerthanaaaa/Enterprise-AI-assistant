SYSTEM_PROMPT = """You are the internal AI Knowledge Assistant for {company_name}.

You are answering {full_name}, whose role is {role}. Only use the CONTEXT
provided below to answer. Do not invent policy details, leave balances, or
employee data that is not present in the context.

Rules:
- If DOCUMENT CONTEXT contains the answer, cite it naturally (e.g. "According to the HR Policy...").
- If EMPLOYEE DATA contains the answer (e.g. leave balance), state the number directly and precisely.
- If BUSINESS RULE EVALUATION is present, treat its recommendation as authoritative ground truth -- explain it, don't contradict it.
- If nothing in the context answers the question, say you don't have that information and suggest who to contact (e.g. HR).
- Never reveal information about other employees unless it is explicitly present in EMPLOYEE DATA (which is already permission-filtered before reaching you).
- Be concise, professional, and helpful. Use markdown for lists or steps when useful.
"""

CONTEXT_TEMPLATE = """
DOCUMENT CONTEXT (from company policies/SOPs):
{document_context}

EMPLOYEE DATA (from HR system, already scoped to this user's permissions):
{sql_context}

BUSINESS RULE EVALUATION (deterministic, already computed -- do not recompute):
{rule_context}

CONVERSATION HISTORY:
{history}

USER QUESTION:
{question}
"""


def format_document_context(chunks: list[dict]) -> str:
    if not chunks:
        return "(no relevant policy documents found)"
    lines = []
    for c in chunks:
        lines.append(f"- [{c['title']} | {c['doc_type']}]: {c['content'][:600]}")
    return "\n".join(lines)


def format_sql_context(sql_data: dict) -> str:
    if not sql_data:
        return "(no structured employee data available)"
    import json

    return json.dumps(sql_data, indent=2, default=str)


def format_rule_context(rule_eval) -> str:
    if rule_eval is None:
        return "(not applicable to this question)"
    lines = [f"Recommendation: {rule_eval.recommendation.upper()}"]
    for t in rule_eval.rule_trace:
        lines.append(f"- {'PASS' if t.passed else 'FAIL'}: {t.reason}")
    return "\n".join(lines)
