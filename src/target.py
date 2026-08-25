"""LLM target for Intellectus Operations/CX evaluation.

The target mirrors the behavioural contract of Intellectus workflow
53_OPERATIONS_CX_AGENT, but uses an LLM so its behaviour can be evaluated and
compared in LangSmith.

The function returns structured findings only. It does not mutate source
evidence and does not make technology recommendations.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from langsmith import get_current_run_tree, traceable
from openai import OpenAI
from pydantic import BaseModel, Field


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"

# Project-local configuration should win over stale shell or Conda values.
load_dotenv(ENV_FILE, override=True)

DEFAULT_MODEL = "gpt-5.4-mini"
MODEL = os.getenv("TARGET_MODEL", DEFAULT_MODEL)

client = OpenAI()


FindingType = Literal["observed", "inferred", "hypothesis", "unknown"]


class Finding(BaseModel):
    """Single evidence-grounded Operations/CX finding."""

    finding: str = Field(
        description="Concise finding supported by the supplied evidence."
    )
    finding_type: FindingType
    evidence_ids: list[str] = Field(
        description="Evidence IDs that directly support this finding."
    )
    requires_validation: bool
    validation_question: str | None = Field(
        default=None,
        description=(
            "Required for inferred, hypothesis, unknown or contradictory cases; "
            "null for fully observed findings."
        ),
    )


class OperationsCXResult(BaseModel):
    """Structured target output consumed by LangSmith evaluators."""

    findings: list[Finding]


SYSTEM_PROMPT = """You are the Operations/CX analysis component of Intellectus.

Your job is to transform supplied evidence into cautious, traceable findings.

Rules:
1. Use only evidence whose domain is exactly "operations_cx".
2. Never use Revenue, Impact, or other-domain evidence to support an Operations/CX finding.
3. Treat a supported fact with no contradiction and no validation requirement as observed.
4. Treat an inference or partially supported evidence as inferred.
5. Preserve explicit hypotheses as hypothesis findings.
6. Treat contradicted, unknown, or insufficient evidence as unknown.
7. Never turn an internal process assumption into an observed fact.
8. Every evidence_id in the output must exist in the supplied Operations/CX evidence.
9. Inferred, hypothesis, unknown, and contradictory findings require a validation question.
10. Do not recommend technologies, platforms, CRMs, chatbots, automation, or implementation solutions.
11. Prefer a cautious unknown over an unsupported conclusion.
12. Keep findings concise and useful to a human consultant.

Return only the structured result requested by the schema.
"""


def _build_user_prompt(inputs: dict) -> str:
    """Serialize one evaluation case without adding assumptions to the evidence."""
    payload = {
        "question": inputs.get("question", ""),
        "evidence": inputs.get("evidence", []),
    }

    # Some cases deliberately include a candidate claim to test whether the
    # model rejects unsupported internal-process assertions.
    if "candidate_claim" in inputs:
        payload["candidate_claim"] = inputs["candidate_claim"]

    return (
        "Analyse this evaluation case according to the Intellectus "
        "Operations/CX rules.\n\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )


def _usage_metadata(response) -> dict:
    """Translate OpenAI Responses usage into LangSmith's recognised schema."""
    usage = getattr(response, "usage", None)
    if usage is None:
        return {}

    metadata = {
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
        "total_tokens": usage.total_tokens,
    }

    input_details = getattr(usage, "input_tokens_details", None)
    cached_tokens = getattr(input_details, "cached_tokens", 0) if input_details else 0

    if cached_tokens:
        metadata["input_token_details"] = {"cache_read": cached_tokens}

    return metadata


@traceable(
    name="openai_operations_cx_call",
    run_type="llm",
    metadata={
        "ls_provider": "openai",
        "ls_model_name": MODEL,
    },
)
def _invoke_model(messages: list[dict]) -> dict:
    """Call OpenAI and attach token usage to the active LangSmith LLM run."""
    response = client.responses.parse(
        model=MODEL,
        input=messages,
        text_format=OperationsCXResult,
    )

    parsed = response.output_parsed
    if parsed is None:
        raise RuntimeError("Model returned no parseable structured output.")

    usage_metadata = _usage_metadata(response)

    # LangSmith requires usage_metadata on the LLM run to populate token and
    # cost fields for custom model instrumentation.
    if usage_metadata:
        run = get_current_run_tree()
        run.set(usage_metadata=usage_metadata)

    return parsed.model_dump()


@traceable(name="intellectus_operations_cx_target")
def operations_cx_target(inputs: dict) -> dict:
    """Run one dataset example through the LLM target with LangSmith tracing."""
    if not isinstance(inputs, dict):
        raise TypeError("Target input must be a dictionary.")

    evidence = inputs.get("evidence")
    if not isinstance(evidence, list):
        raise ValueError("Target input must contain an 'evidence' list.")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": _build_user_prompt(inputs)},
    ]

    return _invoke_model(messages)


if __name__ == "__main__":
    # One-case smoke test before re-running the full evaluation.
    sample = {
        "question": "What Operations/CX finding is justified by the evidence?",
        "evidence": [
            {
                "evidence_id": "EV-OPS-SMOKE-001",
                "domain": "operations_cx",
                "claim": "The organisation publishes an online volunteer application form.",
                "evidence_type": "fact",
                "status": "supported",
                "confidence": 0.95,
                "requires_validation": False,
                "contradiction_ids": [],
            }
        ],
    }

    print(json.dumps(operations_cx_target(sample), indent=2, ensure_ascii=False))