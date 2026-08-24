"""
Target function(s) for the coaching-eval-lab.

Given a conversation history + the employee's latest message, generates
the coach's next response using an ICF-style reflective coaching prompt.
Wrapped with @traceable so every call is automatically logged to
LangSmith.

Provides two ready-made target functions sharing the same prompt/logic,
differing only in model — used for the cost/performance A/B comparison
in ab_evaluation_run.py:
- coach_target_mini  -> gpt-4o-mini (also used as the default target in evaluation_run.py)
- coach_target_gpt4o -> gpt-4o
"""

from dotenv import load_dotenv
from langsmith import traceable
from langsmith.wrappers import wrap_openai
from openai import OpenAI

load_dotenv()

openai_client = wrap_openai(OpenAI())

SYSTEM_PROMPT = """You are an ICF-style coach in a workplace coaching conversation \
about goal-setting and performance.

Rules:
- Respond with exactly ONE question. Never ask two things at once (no "is it X or Y" \
style compound questions).
- The question must be open-ended (not answerable with yes/no).
- Never give advice, suggestions, solutions, or opinions.
- Ask a reflective question that helps the employee explore their own thinking.
- Keep your response to a single sentence.
- If there is prior conversation history, do not repeat a question you already asked.
- Do not add any preamble, explanation, or extra commentary — output only the question."""


def _format_history(conversation_history: list) -> str:
    """Turns a list of {"role": ..., "text": ...} turns into a readable transcript."""
    if not conversation_history:
        return "(This is the first message in the conversation.)"
    lines = [f"{turn['role'].upper()}: {turn['text']}" for turn in conversation_history]
    return "\n".join(lines)


def _generate_coach_response(inputs: dict, model: str) -> dict:
    """Shared logic for generating a coach response with a given model."""
    try:
        history_text = _format_history(inputs.get("conversation_history", []))
        latest_message = inputs["latest_message"]

        user_content = (
            f"Conversation so far:\n{history_text}\n\n"
            f"EMPLOYEE: {latest_message}\n\n"
            f"Respond as the coach, following the rules."
        )

        response = openai_client.chat.completions.create(
            model=model,
            temperature=0.3,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )
        coach_response = response.choices[0].message.content.strip()
        return {"expected_output": coach_response}

    except Exception as e:
        # Return an error marker rather than crashing the whole eval run —
        # this example will simply score poorly / show up in the UI as an error.
        return {"expected_output": f"[ERROR: {e}]"}


@traceable(name="coach_target_mini")
def coach_target_mini(inputs: dict) -> dict:
    """Target function using gpt-4o-mini (the lab's original baseline model)."""
    return _generate_coach_response(inputs, model="gpt-4o-mini")


@traceable(name="coach_target_gpt4o")
def coach_target_gpt4o(inputs: dict) -> dict:
    """Target function using gpt-4o, for cost/performance comparison against the mini baseline."""
    return _generate_coach_response(inputs, model="gpt-4o")


# Backward-compatible alias — evaluation_run.py imports coach_target directly
coach_target = coach_target_mini


if __name__ == "__main__":
    # Quick manual test on 2-3 examples before running the full evaluation
    test_cases = [
        {"conversation_history": [], "latest_message": "I want to be a manager within two years."},
        {
            "conversation_history": [
                {"role": "employee", "text": "I already tried setting goals before and it didn't work."},
                {"role": "coach", "text": "What got in the way last time?"},
            ],
            "latest_message": "Honestly, I just lost interest after a few weeks.",
        },
        {"conversation_history": [], "latest_message": "I don't need coaching, I already know what I'm doing wrong."},
    ]

    for i, case in enumerate(test_cases, 1):
        result = coach_target_mini(case)
        print(f"--- Test {i} (gpt-4o-mini) ---")
        print(f"Latest message: {case['latest_message']}")
        print(f"Coach response: {result['expected_output']}\n")
