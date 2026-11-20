"""Target function and evaluators for the AML compliance Q&A evaluation."""
from dotenv import load_dotenv
load_dotenv()

from langsmith import Client, traceable, wrappers
from openai import OpenAI
from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT

client = Client()
oai = wrappers.wrap_openai(OpenAI())  # every OpenAI call is traced in LangSmith

DATASET_NAME = "aml-compliance-qa-v1"

SYSTEM_PROMPT = (
    "You are an AML compliance assistant. Answer concisely and accurately under "
    "the EU AML framework (AMLD, AMLR, FATF), citing the relevant article where possible."
)


# ---------- Target function (Step 5) ----------
@traceable(name="aml_qa_target")
def target(inputs: dict, model: str = "gpt-4o-mini") -> dict:
    """Answer one AML question. Input: {'question': str}. Output: {'answer': str}."""
    try:
        resp = oai.chat.completions.create(
            model=model,
            temperature=0,      # deterministic-ish answers
            max_tokens=400,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": inputs["question"]},
            ],
        )
        return {"answer": resp.choices[0].message.content}
    except Exception as e:  # don't crash the whole run on one API error
        return {"answer": f"ERROR: {e}"}


# ---------- Correctness evaluator (Step 6) ----------
correctness_judge = create_llm_as_judge(
    prompt=CORRECTNESS_PROMPT,
    model="openai:gpt-4o-mini",        # stronger model judges the weaker one
    feedback_key="correctness",
)

def correctness_evaluator(inputs: dict, outputs: dict, reference_outputs: dict):
    """LLM-as-judge: does the answer match the reference answer's substance?"""
    return correctness_judge(
        inputs=inputs, outputs=outputs, reference_outputs=reference_outputs
    )


# ---------- Quick test on 3 examples ----------
if __name__ == "__main__":
    examples = list(client.list_examples(dataset_name=DATASET_NAME, limit=3))
    for ex in examples:
        out = target(ex.inputs)
        result = correctness_evaluator(ex.inputs, out, ex.outputs)
        print("Q:", ex.inputs["question"])
        print("A:", out["answer"][:300])
        print("Score:", result["score"], "|", result["comment"][:200])
        print("-" * 60)