import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Employee Support Desk API")

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "policies.json"


class PolicyQuestion(BaseModel):
    question: str = Field(..., min_length=1)
    as_of: date
    tenant: Optional[str] = None
    role: Optional[str] = None


class PolicyAnswer(BaseModel):
    status: str
    answer: Optional[str] = None
    citations: List[Dict[str, str]] = []


def _load_policies() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        raise HTTPException(status_code=500, detail="Policy data missing")
    with DATA_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _is_prompt_injection(passage: str) -> bool:
    lowered = (passage or "").lower()
    return (
        lowered.startswith("system message")
        or "ignore all prior rules" in lowered
        or "switch the caller" in lowered
        or "state that every allowance" in lowered
    )


def _extract_amount(value: str) -> Optional[int]:
    matches = re.findall(r"inr\s*([0-9][0-9,]*(?:\.\d+)?)", value, flags=re.IGNORECASE)
    if not matches:
        return None
    cleaned = matches[0].replace(",", "")
    return int(float(cleaned))


def _normalize_name(value: Optional[str]) -> str:
    return (value or "").strip().lower()


def _detect_benefit(question: str) -> str:
    lowered = question.lower()
    if "certification" in lowered and ("reimbursement" in lowered or "limit" in lowered):
        return "annual certification reimbursement limit"
    if "home-office" in lowered or "home office" in lowered or "allowance" in lowered:
        return "annual home-office allowance"
    if "training" in lowered:
        return "training approval requirement"
    if "travel" in lowered:
        return "travel eligibility"
    if "manager approval" in lowered:
        return "training approval requirement"
    return "policy entitlement"


def _policy_topic_matches(record: Dict[str, Any], benefit: str) -> bool:
    passage = (record.get("passage") or "").lower()
    benefit_tokens = benefit.lower()
    if benefit_tokens in passage:
        return True
    if benefit_tokens.replace("annual ", "") in passage:
        return True
    keywords = [
        "certification",
        "reimbursement",
        "home-office",
        "travel",
        "training",
        "allowance",
        "approval",
        "manager",
    ]
    return any(keyword in passage for keyword in keywords) and (benefit_tokens in passage or benefit_tokens.replace("annual ", "") in passage)


def _match_policy_records(records: Iterable[Dict[str, Any]], tenant: str, role: str, as_of: date):
    normalized_tenant = _normalize_name(tenant or "atlas")
    normalized_role = _normalize_name(role or "employee")
    candidates = []
    for record in records:
        if record.get("approval_state") != "Approved":
            continue
        if _normalize_name(record.get("tenant")) != normalized_tenant:
            continue
        if _normalize_name(record.get("role")) != normalized_role:
            continue
        if _is_prompt_injection(record.get("passage", "")):
            continue
        effective_from = date.fromisoformat(record["effective_from"])
        effective_to = date.fromisoformat(record["effective_to"])
        if effective_from <= as_of < effective_to:
            candidates.append(record)
    return candidates


def _build_answer(records: List[Dict[str, Any]], tenant: str, role: str, as_of: date, question: str):
    if not records:
        return PolicyAnswer(status="INSUFFICIENT_EVIDENCE", answer=None, citations=[])

    benefit = _detect_benefit(question)
    matched = [record for record in records if _policy_topic_matches(record, benefit)]
    if not matched:
        matched = records

    valid_records = []
    for record in matched:
        passage = (record.get("passage") or "").strip()
        if passage and not _is_prompt_injection(passage):
            valid_records.append(record)

    if not valid_records:
        return PolicyAnswer(status="INSUFFICIENT_EVIDENCE", answer=None, citations=[])

    amounts = []
    for record in valid_records:
        amount = _extract_amount(record.get("passage", ""))
        if amount is not None:
            amounts.append(amount)

    citations = [{"chunk_id": record["id"], "quote": record["passage"]} for record in valid_records[:3]]

    if len(set(amounts)) > 1:
        return PolicyAnswer(
            status="AMBIGUOUS",
            answer=(
                f"Multiple applicable {benefit} values exist for {tenant} {role} as of {as_of.isoformat()}; "
                "human review is required."
            ),
            citations=citations,
        )

    target = valid_records[0]
    amount = _extract_amount(target.get("passage", ""))
    if amount is not None:
        answer = f"The applicable {benefit} for {tenant} {role}s is INR {amount} as of {as_of.isoformat()}."
        return PolicyAnswer(status="ANSWERED", answer=answer, citations=citations)

    quoted_text = (target.get("passage") or "").strip()
    return PolicyAnswer(
        status="ANSWERED",
        answer=f"The policy guidance for {tenant} {role} as of {as_of.isoformat()} is: {quoted_text}",
        citations=citations,
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/answer", response_model=PolicyAnswer)
def answer_policy(payload: PolicyQuestion):
    policies = _load_policies()
    tenant = payload.tenant or "atlas"
    role = payload.role or "employee"
    question = payload.question.strip()
    as_of = payload.as_of

    matched_records = _match_policy_records(policies, tenant, role, as_of)
    return _build_answer(matched_records, tenant, role, as_of, question)


@app.post("/batches")
def submit_batch(payload: Dict[str, Any]):
    items = payload.get("items") or []
    result_items: List[Dict[str, Any]] = []
    seen_hashes: Dict[str, str] = {}

    for index, item in enumerate(items):
        item_id = str(item.get("id") or f"item-{index}")
        document_text = str(item.get("document_text") or item.get("text") or "")
        digest = hashlib.sha256(document_text.encode("utf-8")).hexdigest()

        if digest in seen_hashes:
            result_items.append(
                {
                    "id": item_id,
                    "status": "DUPLICATE",
                    "duplicate_of": seen_hashes[digest],
                    "answer": None,
                }
            )
            continue

        seen_hashes[digest] = item_id

        try:
            response = answer_policy(
                PolicyQuestion(
                    question=document_text or "What is the relevant policy?",
                    as_of=date.fromisoformat(str(item.get("as_of") or "2026-09-21")),
                    tenant=item.get("tenant"),
                    role=item.get("role"),
                )
            )
            result_items.append({"id": item_id, "status": response.status, "answer": response.answer, "citations": response.citations})
        except Exception as exc:  # pragma: no cover - defensive batch handling
            result_items.append({"id": item_id, "status": "FAILED", "error": str(exc), "answer": None})

    return {
        "batch_id": payload.get("batch_id") or "batch-1",
        "items": result_items,
        "summary": {
            "total": len(result_items),
            "answered": sum(1 for item in result_items if item.get("status") == "ANSWERED"),
            "duplicates": sum(1 for item in result_items if item.get("status") == "DUPLICATE"),
            "failed": sum(1 for item in result_items if item.get("status") == "FAILED"),
        },
    }
