import json
import time

from langsmith import traceable

from config import openai_client
from target import (
    SYSTEM_PROMPT,
    format_criteria,
    validate_results,
    derive_screening_summary,
)


# ---------------------------------------------------------
# Models and current API pricing
# Prices are USD per 1 million tokens.


MODEL_CONFIGS = {
    "gpt-4o-mini": {
        "input_price": 0.15,
        "output_price": 0.60,
    },
    "gpt-4.1": {
        "input_price": 2.00,
        "output_price": 8.00,
    },
}


# ---------------------------------------------------------
# Generic target implementation


def run_model(
    inputs: dict,
    model: str,
) -> dict:
    """
    Run the same clinical-trial screening task with a
    specified OpenAI model and collect usage/latency metrics.
    """

    if model not in MODEL_CONFIGS:
        raise ValueError(
            f"Unknown model configuration: {model}"
        )

    patient_note = inputs["patient_note"]
    trial_title = inputs["trial_title"]
    criteria = inputs["criteria"]

    user_prompt = f"""
Clinical trial:
{trial_title}

PATIENT NOTE:
{patient_note}

ELIGIBILITY CRITERIA:
{format_criteria(criteria)}

Return JSON in exactly this structure:

{{
  "criteria": [
    {{
      "criterion_id": 123,
      "label": "MET",
      "evidence": [
        "Exact supporting text from the patient note."
      ],
      "reasoning": "Brief explanation."
    }}
  ]
}}
"""

    start_time = time.perf_counter()

    response = openai_client.chat.completions.create(
        model=model,
        temperature=0,
        response_format={
            "type": "json_object"
        },
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )

    latency_seconds = (
        time.perf_counter() - start_time
    )

    content = response.choices[0].message.content

    parsed = json.loads(content)
    results = parsed["criteria"]

    validate_results(
        results=results,
        input_criteria=criteria,
    )

    # -----------------------------------------------------
    # Token usage
   

    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    total_tokens = response.usage.total_tokens

    prices = MODEL_CONFIGS[model]

    estimated_cost_usd = (
        input_tokens
        / 1_000_000
        * prices["input_price"]
        +
        output_tokens
        / 1_000_000
        * prices["output_price"]
    )

    return {
        "criteria": results,

        "screening_summary": (
            derive_screening_summary(results)
        ),

        "_metrics": {
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "latency_seconds": latency_seconds,
            "estimated_cost_usd": estimated_cost_usd,
        },
    }


# ---------------------------------------------------------
# Model-specific LangSmith targets


@traceable(
    name="clinical-trial-target-gpt-4o-mini",
    metadata={"model": "gpt-4o-mini"},
)
def target_gpt4o_mini(
    inputs: dict,
) -> dict:

    return run_model(
        inputs=inputs,
        model="gpt-4o-mini",
    )


@traceable(
    name="clinical-trial-target-gpt-4.1",
    metadata={"model": "gpt-4.1"},
)
def target_gpt4_1(
    inputs: dict,
) -> dict:

    return run_model(
        inputs=inputs,
        model="gpt-4.1",
    )

# smoke test

if __name__ == "__main__":

    from pathlib import Path

    DATA_FILE = (
        Path(__file__).resolve().parent
        / "data"
        / "curated_examples.json"
    )

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        examples = json.load(file)

    # Use one simple case only.
    test_example = examples[0]

    print(
        f"Testing: {test_example['id']}"
    )

    for target in [
        target_gpt4o_mini,
        target_gpt4_1,
    ]:

        result = target(
            test_example["inputs"]
        )

        print("\n" + "=" * 60)

        print(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            )
        )