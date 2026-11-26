"""Custom LangSmith dataset + evaluation: an EU AI Act / GDPR Q&A assistant for small businesses.

Lab "Micromanage your agents", Steps 2-9:
  Step 2  connect to LangSmith (tracing on) and wrap the model client so every call is logged
  Step 3  12 examples written from the course materials (Week 7 slides and TA revision notes)
  Step 4  upload them as a LangSmith dataset (skipped if the dataset already exists)
  Step 5  target function with @traceable: question -> answer
  Step 6  correctness evaluator: LLM-as-judge using OpenEvals' built-in CORRECTNESS_PROMPT
  Step 7  run the experiment with client.evaluate()
  Step 9  pull the scores back and save them to results/langsmith_results.json

Provider: Gemini (free tier) through its native REST API, because the student has no paid OpenAI key.
The first version used the OpenAI-compatible endpoint wrapped with LangSmith's wrap_openai, as in the
class notebook; on the student's machine those calls timed out, so the model call is now a plain
`requests` call decorated with @traceable(run_type="llm"), which LangSmith records the same way.

Secrets live in a local .env (GEMINI_API_KEY, LANGSMITH_API_KEY, LANGSMITH_TRACING=true), never committed.
If your LangSmith account is on the EU site (eu.smith.langchain.com), also add
LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com to .env.
"""
import json
import os
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")
load_dotenv(HERE.parent / ".env")
# Also reuse the student's Project 3 .env (it already holds GEMINI_API_KEY); values above win.
load_dotenv(Path.home() / "OneDrive" / "Escritorio" / "Bootcamp_IA" / "Semana 6" / "proyecto3-agente-editorial" / ".env")
os.environ.setdefault("LANGSMITH_TRACING", "true")
os.environ.setdefault("LANGSMITH_PROJECT", "ai-act-gdpr-qa-week7")

import requests  # noqa: E402
from langsmith import Client, traceable  # noqa: E402  (after env vars are loaded)
from openevals.prompts import CORRECTNESS_PROMPT  # noqa: E402

for var in ("GEMINI_API_KEY", "LANGSMITH_API_KEY"):
    if not os.getenv(var):
        sys.exit(f"{var} not found. Put it in a .env file next to this script.")

DATASET_NAME = "ai-act-gdpr-sme-qa-v1"
MODELS = [os.getenv("TARGET_MODEL", "gemini-3.5-flash"), "gemini-3-flash-preview", "gemini-flash-latest", "gemini-2.5-flash"]
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
KEY = os.environ["GEMINI_API_KEY"]

ls_client = Client()

# ---------- Step 3: examples (input = question, output = reference answer, metadata for analysis) ----------
EXAMPLES = [
    ("Under the EU AI Act, what is the key test that makes software an 'AI system'?",
     "Whether it infers its output from data (predictions, recommendations, decisions or content). Rules written by a person are not an AI system.",
     "ai_act", "easy"),
    ("Can a company use AI cameras to detect whether its employees are stressed at work?",
     "No. Emotion recognition in the workplace is a prohibited practice under Article 5 of the AI Act, except for medical or safety reasons.",
     "ai_act", "easy"),
    ("Is an AI tool that ranks job applicants' CVs high-risk under the AI Act?",
     "Yes. Recruitment and selection is an Annex III high-risk area (employment), and ranking candidates is profiling, so it is always high-risk.",
     "ai_act", "medium"),
    ("From when do the AI Act obligations for Annex III high-risk systems apply after the Digital Omnibus?",
     "From 2 December 2027 (Annex I product-related high-risk systems from 2 August 2028).",
     "ai_act", "hard"),
    ("What must a customer-service chatbot tell users under the AI Act transparency rules?",
     "That they are interacting with an AI system, unless this is obvious from the context (Article 50, applicable from August 2026).",
     "ai_act", "medium"),
    ("A startup sells an HR app under its own brand that is built entirely on OpenAI's model. Who is the provider of the app under the AI Act?",
     "The startup is the provider of the app. OpenAI is the provider of the general-purpose AI model; 'powered by' does not transfer responsibility.",
     "ai_act", "medium"),
    ("What are the six lawful bases for processing personal data under Article 6 GDPR?",
     "Consent, contract, legal obligation, vital interests, public task and legitimate interests.",
     "gdpr", "easy"),
    ("Is pseudonymised data still personal data under the GDPR?",
     "Yes. As long as someone can re-identify the person (for example with the key table), it is personal data. Only anonymised data falls outside the GDPR.",
     "gdpr", "medium"),
    ("Within how many hours must a company notify a personal data breach to the data protection authority?",
     "Within 72 hours of becoming aware of it, unless the breach is unlikely to result in a risk to people.",
     "gdpr", "easy"),
    ("Can legitimate interest be used as the extra condition to process health data under the GDPR?",
     "No. Health data is special category data: it needs an Article 6 basis plus an Article 9 condition such as explicit consent, and legitimate interest can never be that extra condition.",
     "gdpr", "hard"),
    ("In which three cases is a DPIA always required under the GDPR?",
     "Profiling or automated decisions with serious effects, large-scale processing of sensitive data, and large-scale monitoring of public places.",
     "gdpr", "hard"),
    ("What does a company need to send customers' personal data to a US-based AI provider?",
     "A data processing agreement with the provider, plus a transfer tool: the provider certified under the EU-US Data Privacy Framework, or standard contractual clauses. A plan B is advisable.",
     "gdpr", "medium"),
]


def create_dataset_if_missing():
    """Step 4: upload the examples once. Running the script again reuses the dataset."""
    if ls_client.has_dataset(dataset_name=DATASET_NAME):
        print(f"Dataset '{DATASET_NAME}' already exists: reusing it.")
        return
    ds = ls_client.create_dataset(
        dataset_name=DATASET_NAME,
        description="12 questions a small EU business might ask about the AI Act and GDPR, with reference answers "
                    "written from Ironhack Week 7 materials. Metadata: topic (ai_act/gdpr) and difficulty.",
    )
    for question, answer, topic, difficulty in EXAMPLES:
        ls_client.create_example(inputs={"question": question}, outputs={"answer": answer},
                                 metadata={"topic": topic, "difficulty": difficulty}, dataset_id=ds.id)
    print(f"Created dataset '{DATASET_NAME}' with {len(EXAMPLES)} examples.")


@traceable(run_type="llm", name="gemini_generate_content")
def call_model(messages, json_mode=False):
    """Call Gemini's native REST API (the OpenAI-compatible endpoint timed out on the student's machine).
    Traced as an LLM run so LangSmith shows the prompt, the answer and the latency."""
    system = " ".join(m["content"] for m in messages if m["role"] == "system")
    user = "\n\n".join(m["content"] for m in messages if m["role"] != "system")
    body = {"contents": [{"role": "user", "parts": [{"text": user}]}], "generationConfig": {"temperature": 0}}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    if json_mode:
        body["generationConfig"]["responseMimeType"] = "application/json"
    last = None
    for model in MODELS:
        for attempt in range(4):
            try:
                r = requests.post(GEMINI_URL.format(model=model), headers={"x-goog-api-key": KEY}, json=body, timeout=120)
                if r.status_code == 200:
                    parts = r.json()["candidates"][0]["content"].get("parts", [])
                    return "".join(p.get("text", "") for p in parts if not p.get("thought"))
                last = f"{model}: HTTP {r.status_code}"
                print(f"   {last}: {r.text.replace(KEY, '[REDACTED]')[:150]}", flush=True)
                if r.status_code in (400, 404):
                    break
            except (requests.RequestException, KeyError, IndexError, ValueError) as e:
                last = f"{model}: {type(e).__name__}"
                print(f"   {last}", flush=True)
            time.sleep(10 * (attempt + 1))
    raise RuntimeError(f"All models failed: {last}")


# ---------- Step 5: target function (traced) ----------
@traceable(name="ai_act_gdpr_assistant")
def target(inputs: dict) -> dict:
    system = ("You answer questions from small EU businesses about the EU AI Act and the GDPR. "
              "Answer in at most three sentences, name the article or category when relevant, "
              "and do not claim that anything is legally compliant.")
    answer = call_model([{"role": "system", "content": system},
                         {"role": "user", "content": inputs["question"]}])
    return {"answer": answer}


# ---------- Step 6: correctness evaluator (LLM-as-judge with OpenEvals' prompt) ----------
@traceable(name="correctness_judge")
def correctness(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    prompt = (CORRECTNESS_PROMPT
              .replace("{inputs}", inputs["question"])
              .replace("{outputs}", outputs["answer"])
              .replace("{reference_outputs}", reference_outputs["answer"]))
    prompt += ('\n\nReturn only JSON: {"reasoning": "<one or two sentences>", "score": true or false}')
    text = call_model([{"role": "user", "content": prompt}], json_mode=True)
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        verdict = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        verdict = json.loads(match.group(0)) if match else {"score": None, "reasoning": "parse error: " + text[:200]}
    score = verdict.get("score")
    if isinstance(score, str):
        score = score.strip().lower() == "true"
    return {"key": "correctness", "score": score, "comment": verdict.get("reasoning", "")}


def main():
    create_dataset_if_missing()
    print("Quick test of the target on one question:", target({"question": EXAMPLES[1][0]})["answer"][:200])

    # Step 7: run the experiment (concurrency 1 to stay inside free-tier rate limits)
    results = ls_client.evaluate(target, data=DATASET_NAME, evaluators=[correctness],
                                 experiment_prefix="gemini-flash-baseline", max_concurrency=1,
                                 metadata={"model": MODELS[0], "judge": MODELS[0], "provider": "gemini-native-rest"})

    # Step 9: collect the scores
    rows = []
    for r in results:
        ex = r["example"]
        ev = r["evaluation_results"]["results"][0] if r["evaluation_results"]["results"] else None
        rows.append({
            "question": ex.inputs["question"],
            "reference": ex.outputs["answer"],
            "topic": (ex.metadata or {}).get("topic"),
            "difficulty": (ex.metadata or {}).get("difficulty"),
            "answer": (r["run"].outputs or {}).get("answer"),
            "correct": ev.score if ev else None,
            "judge_comment": ev.comment if ev else None,
            "latency_s": round((r["run"].end_time - r["run"].start_time).total_seconds(), 2) if r["run"].end_time else None,
        })
    scored = [x for x in rows if x["correct"] is not None]
    by = lambda key: {v: f"{sum(1 for x in scored if x[key] == v and x['correct'])}/{sum(1 for x in scored if x[key] == v)}"
                      for v in sorted({x[key] for x in scored})}
    summary = {
        "experiment": results.experiment_name,
        "dataset": DATASET_NAME,
        "n_examples": len(rows),
        "correct": sum(1 for x in scored if x["correct"]),
        "accuracy": round(sum(1 for x in scored if x["correct"]) / len(scored), 3) if scored else None,
        "by_topic": by("topic"),
        "by_difficulty": by("difficulty"),
        "mean_latency_s": round(sum(x["latency_s"] or 0 for x in rows) / len(rows), 2),
    }
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "langsmith_results.json").write_text(
        json.dumps({"summary": summary, "rows": rows}, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n=== Summary ===")
    for k, v in summary.items():
        print(f"{k}: {v}")
    print("\n=== Wrong answers ===")
    for x in rows:
        if x["correct"] is False:
            print("-", x["question"], "\n   judge:", (x["judge_comment"] or "")[:200])
    print("\nSaved results/langsmith_results.json. Open LangSmith > Datasets & Experiments to see the traces.")


if __name__ == "__main__":
    main()
