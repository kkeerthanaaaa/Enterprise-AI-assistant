"""Deterministic business-rule engine for leave reasoning.

This is intentionally NOT left to the LLM to "figure out" from prose policy
text — leave-balance arithmetic and notice-period checks are computed here in
plain Python against the SQL data, and the *result* of that computation is
handed to the LLM as ground truth to phrase into a natural-language answer.
This avoids the classic RAG failure mode of an LLM hallucinating a leave
balance number from a similarity-matched paragraph.
"""
from dataclasses import dataclass, field
from datetime import date
from sqlalchemy.orm import Session

from app.models.leave import LeaveBalance, LeaveRequest
from app.models.leave import LeaveType
from app.models.enums import LeaveStatus


@dataclass
class RuleResult:
    passed: bool
    reason: str


@dataclass
class LeaveEvaluation:
    balance_ok: bool
    notice_period_ok: bool
    overlapping_requests: bool
    remaining_days: float
    days_requested: float
    notice_days_given: int
    required_notice_days: int
    recommendation: str  # "approve" | "reject" | "review"
    rule_trace: list[RuleResult] = field(default_factory=list)


# Minimum notice (in days) required before the leave start date, per type.
# In a real deployment this would be loaded per-company from the Policy
# table rather than hardcoded; kept simple here for clarity.
NOTICE_REQUIREMENTS = {
    LeaveType.ANNUAL: 3,
    LeaveType.SICK: 0,
    LeaveType.MATERNITY: 30,
    LeaveType.PATERNITY: 7,
    LeaveType.UNPAID: 14,
    LeaveType.WFH: 1,
}


def evaluate_leave_request(
    db: Session,
    company_id,
    user_id,
    leave_type: LeaveType,
    start_date: date,
    end_date: date,
    today: date | None = None,
) -> LeaveEvaluation:
    today = today or date.today()
    days_requested = (end_date - start_date).days + 1

    year = start_date.year
    balance = (
        db.query(LeaveBalance)
        .filter(
            LeaveBalance.company_id == company_id,
            LeaveBalance.user_id == user_id,
            LeaveBalance.leave_type == leave_type,
            LeaveBalance.year == year,
        )
        .first()
    )
    remaining = balance.remaining_days if balance else 0.0

    trace: list[RuleResult] = []

    balance_ok = remaining >= days_requested
    trace.append(
        RuleResult(
            balance_ok,
            f"Remaining {leave_type.value} balance is {remaining} day(s); requested {days_requested}.",
        )
    )

    required_notice = NOTICE_REQUIREMENTS.get(leave_type, 0)
    notice_given = (start_date - today).days
    notice_ok = notice_given >= required_notice
    trace.append(
        RuleResult(
            notice_ok,
            f"{notice_given} day(s) notice given; policy requires {required_notice} day(s) for {leave_type.value} leave.",
        )
    )

    overlapping = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.company_id == company_id,
            LeaveRequest.user_id == user_id,
            LeaveRequest.status.in_([LeaveStatus.PENDING, LeaveStatus.APPROVED]),
            LeaveRequest.start_date <= end_date,
            LeaveRequest.end_date >= start_date,
        )
        .count()
        > 0
    )
    if overlapping:
        trace.append(RuleResult(False, "An overlapping leave request already exists."))

    if balance_ok and notice_ok and not overlapping:
        recommendation = "approve"
    elif not balance_ok:
        recommendation = "reject"
    else:
        recommendation = "review"

    return LeaveEvaluation(
        balance_ok=balance_ok,
        notice_period_ok=notice_ok,
        overlapping_requests=overlapping,
        remaining_days=remaining,
        days_requested=days_requested,
        notice_days_given=notice_given,
        required_notice_days=required_notice,
        recommendation=recommendation,
        rule_trace=trace,
    )
