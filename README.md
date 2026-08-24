# School Book Order Extraction — LangSmith Evaluation Lab

## Domain & Dataset

Custom LangSmith dataset (`school-orders-extraction`, 13 examples) evaluating LLM extraction of structured school book orders — school, class, title, qty — from raw WhatsApp-style order messages. Built from real school book-order and catalogue data (Sai Vidyanikethan, NJR EM School, Bramharshi Vidya Mandir), mirroring the production extraction task in my father's book-order-bot n8n workflow. Quantities are real where sourced from Sai Vidyanikethan's requirement sheet, synthetic (clearly marked in each example's metadata as `qty_source`) elsewhere, since the other source sheets were catalogue lists without quantities.

## Approach

1. Structured 13 examples (raw message → expected `items` list) and uploaded them to LangSmith as a dataset.
2. Built a target function (`target.py`) calling gpt-4o-mini with a system prompt to extract structured orders, with `@traceable` tracing enabled.
3. Built an LLM-as-judge correctness evaluator (`evaluator.py`) — semantic match against reference, ignoring formatting differences.
4. Ran the evaluation (`run_eval.py`), reviewed results in the LangSmith UI, and analyzed the failure pattern.
5. (Optional) Added a custom completeness evaluator measuring item-level coverage, independent of field accuracy.
6. (Optional) Ran an A/B comparison against gpt-4o to compare cost, latency, correctness, and completeness.

## Key Finding

All correctness failures (6/13) traced to one root cause: unresolved school-name abbreviations ("njr", "bvm") or typo'd school names not normalized to canonical form — not a general extraction weakness. The completeness evaluator confirmed this: it scored 1.00 across all 13 examples, meaning the model never dropped or hallucinated items. Full details in `evaluation_summary.md`.

The optional A/B test found gpt-4o-mini outperforming gpt-4o on correctness, completeness, latency, and cost — see `optimization_summary.md`.

## How to Run

Requires a LangSmith account (EU region) and an OpenAI API key.

```bash
pip install langsmith openai python-dotenv
```

Create a `.env` file with:
```
LANGSMITH_API_KEY=your_key
LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
LANGSMITH_TRACING=true
OPENAI_API_KEY=your_key
```

Then run in order:
```bash
python create_dataset.py   # uploads the 13 examples to LangSmith (skips if dataset already exists)
python target.py           # sanity-checks the target function on 2-3 examples
python evaluator.py        # sanity-checks correctness + completeness evaluators
python run_eval.py         # runs the full evaluation(s) against the dataset
```

## File Map

| File | Purpose |
|---|---|
| `create_dataset.py` | Structures the 13 examples and uploads them to LangSmith as the `school-orders-extraction` dataset |
| `target.py` | Target functions: `target` (gpt-4o-mini) and `target_gpt4o` (gpt-4o) — extract structured orders from raw messages |
| `evaluator.py` | `correctness_evaluator` (LLM-as-judge semantic match) and `completeness_evaluator` (item-coverage scoring) |
| `run_eval.py` | Runs the evaluation(s) against the dataset with the chosen target/evaluator combination |
| `evaluation_summary.md` | Required deliverable — methodology, results, and analysis for the core evaluation |
| `optimization_summary.md` | Required deliverable — cost/performance comparison between gpt-4o-mini and gpt-4o |
| `screenshots/` | LangSmith UI screenshots (dataset, experiment comparison views) |

## LangSmith Links

- Dataset: `school-orders-extraction` (id `02546789-3dc8-41e6-a346-b6671e206b0b`)
- Baseline experiment: `gpt-4o-mini-baseline-78937335`
- With completeness evaluator: `gpt-4o-mini-with-completeness-161fdcfc`
- Final comparison: `gpt-4o-mini-final-69b227b3` vs `gpt-4o-final-c156c8e4`