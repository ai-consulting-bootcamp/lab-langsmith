"""Evaluators for the Intellectus Operations/CX LangSmith experiment.

The evaluation suite combines:
- semantic correctness against reference criteria;
- groundedness against supplied evidence;
- deterministic contract checks for evidence references and validation rules.

LLM judges score meaning rather than exact wording. Deterministic checks protect
invariants that should not depend on judge interpretation.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langsmith import traceable
from openai import OpenAI
from pydantic import BaseModel, Field


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE, override=True)

DEFAULT_JUDGE_MODEL = "gpt-5.4"
JUDGE_MODEL = os.getenv("JUDGE_MODEL", DEFAULT_JUDGE_MODEL)

client = OpenAI()


class JudgeResult(BaseModel):
    """Compact evaluator output suitable for LangSmith feedback."""

    score: float = Field(ge=0.0, le=1.0)
    reasoning: str = Field(
        description="Short explanation focused on the evaluation criteria."
    )


CORRECTNESS_PROMPT = """You are evaluating an Operations/CX analysis system.

Compare the generated output with the reference criteria. Do not require exact
wording. Judge whether the generated result satisfies the intended behaviour.

Pay particular attention to:
- finding type: observed, inferred, hypothesis, or unknown;
- required and excluded evidence IDs;
- validation requirements;
- explicit forbidden claims or recommendations;
- mixed cases where more than one finding is expected;
- cautious handling of unsupported or contradictory evidence.

Scoring:
1.0 = fully satisfies the reference criteria
0.75 = materially correct with a minor omission
0.5 = partially correct but misses an important criterion
0.25 = mostly incorrect
0.0 = contradicts the expected behaviour

Return a concise score and reasoning.
"""


GROUNDEDNESS_PROMPT = """You are evaluating grounding for an Operations/CX analysis.

Judge only whether the generated findings are supported by the supplied
evidence. Do not use outside knowledge.

A grounded response:
- uses only evidence with domain exactly "operations_cx";
- does not invent internal processes, ownership, automation, or follow-up;
- does not convert inference, hypothesis, contradiction, or unknown evidence
  into an observed fact;
- cites only evidence IDs that actually exist in the supplied case;
- remains cautious when evidence is insufficient.

Scoring:
1.0 = every material claim is grounded
0.75 = one minor unsupported detail
0.5 = mixed grounded and unsupported content
0.25 = substantial unsupported inference
0.0 = materially fabricated or contradicted by the evidence

Return a concise score and reasoning.
"""


def _judge(system_prompt: str, payload: dict) -> JudgeResult:
    """Run a structured LLM judge without exposing evaluator implementation details."""
    response = client.responses.parse(
        model=JUDGE_MODEL,
        input=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": json.dumps(payload, ensure_ascii=False, indent=2),
            },
        ],
        text_format=JudgeResult,
    )

    if response.output_parsed is None:
        raise RuntimeError("Judge returned no parseable output.")

    return response.output_parsed


@traceable(
    name="correctness_judge",
    run_type="llm",
    metadata={
        "ls_provider": "openai",
        "ls_model_name": JUDGE_MODEL,
    },
)
def correctness_evaluator(
    inputs: dict,
    outputs: dict,
    reference_outputs: dict,
) -> dict:
    """Score semantic correctness against the dataset reference criteria."""
    result = _judge(
        CORRECTNESS_PROMPT,
        {
            "inputs": inputs,
            "generated_output": outputs,
            "reference_criteria": reference_outputs,
        },
    )

    return {
        "key": "correctness",
        "score": result.score,
        "comment": result.reasoning,
    }


@traceable(
    name="groundedness_judge",
    run_type="llm",
    metadata={
        "ls_provider": "openai",
        "ls_model_name": JUDGE_MODEL,
    },
)
def groundedness_evaluator(
    inputs: dict,
    outputs: dict,
    reference_outputs: dict | None = None,
) -> dict:
    """Score whether generated findings remain supported by supplied evidence."""
    result = _judge(
        GROUNDEDNESS_PROMPT,
        {
            "question": inputs.get("question"),
            "evidence": inputs.get("evidence", []),
            "candidate_claim": inputs.get("candidate_claim"),
            "generated_output": outputs,
        },
    )

    return {
        "key": "groundedness",
        "score": result.score,
        "comment": result.reasoning,
    }


def contract_compliance_evaluator(
    inputs: dict,
    outputs: dict,
    reference_outputs: dict | None = None,
) -> dict:
    """Check non-negotiable output invariants without an LLM judge."""
    evidence = inputs.get("evidence", [])
    allowed_ids = {
        item.get("evidence_id")
        for item in evidence
        if item.get("domain") == "operations_cx"
    }

    findings = outputs.get("findings", []) if isinstance(outputs, dict) else []
    issues: list[str] = []

    if not isinstance(findings, list) or not findings:
        return {
            "key": "contract_compliance",
            "score": 0.0,
            "comment": "No findings were returned.",
        }

    for index, finding in enumerate(findings, start=1):
        finding_type = finding.get("finding_type")
        evidence_ids = finding.get("evidence_ids", [])
        requires_validation = finding.get("requires_validation")
        validation_question = finding.get("validation_question")

        invalid_ids = [evidence_id for evidence_id in evidence_ids if evidence_id not in allowed_ids]
        if invalid_ids:
            issues.append(
                f"Finding {index} references invalid/non-Operations evidence IDs: {invalid_ids}."
            )

        if finding_type in {"inferred", "hypothesis", "unknown"}:
            if requires_validation is not True:
                issues.append(
                    f"Finding {index} ({finding_type}) must require validation."
                )
            if not validation_question:
                issues.append(
                    f"Finding {index} ({finding_type}) requires a validation question."
                )

        if finding_type == "observed":
            if requires_validation is True:
                issues.append(
                    f"Finding {index} is observed but still marked for validation."
                )

    score = 1.0 if not issues else max(0.0, 1.0 - (0.25 * len(issues)))

    return {
        "key": "contract_compliance",
        "score": score,
        "comment": "All contract checks passed." if not issues else " ".join(issues),
    }


EVALUATORS = [
    correctness_evaluator,
    groundedness_evaluator,
    contract_compliance_evaluator,
]
