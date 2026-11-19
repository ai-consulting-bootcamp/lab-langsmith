# Lab proof: EU AI Act Q&A evaluation in LangSmith

This page is the entry point. It shows how the lab works, one run from input to output, the evidence it produced, and the problems I ran into.

## 1. Code and workflow
Everything is in [`lab_langsmith_eu_ai_act.ipynb`](lab_langsmith_eu_ai_act.ipynb):

1. **Setup:** LangSmith tracing on (EU endpoint), project `lab-langsmith-eu-ai-act`, OpenAI client wrapped with `wrap_openai` so every call is traced.
2. **Dataset:** 19 hand-written examples (question + article summary as context → reference answer, with category/difficulty/source as metadata), checked for missing keys and empty fields, uploaded as `eu-ai-act-qa-v1`.
3. **Target:** `gpt-4o-mini`, temperature 0. It answers from the context only, with a verdict and an article citation.
4. **Evaluators:** an LLM judge for correctness (`gpt-5.4-mini`, OpenEvals) and a rule-based article-citation check.
5. **Experiment:** `client.evaluate()` over all 19 examples → results to CSV → pass rates by category/difficulty → error analysis.

## 2. One run: input → output
**Input** (example 1, category `prohibited_practices`, difficulty `easy`):
- **Question:** Can we use AI to detect employees' emotions during video calls?
- **Context:** Article 5(1)(f) (summary): The use of AI systems to infer the emotions of a natural person in the areas of workplace and education institutions is prohibited, except where the AI system is intended to be used for medical or safety reasons.

**Model output (gpt-4o-mini):**
> No, the use of AI systems to infer the emotions of a natural person in the workplace is prohibited under Article 5(1)(f), except for medical or safety reasons.

**Reference answer:**
> No. Emotion recognition in the workplace is prohibited under Article 5(1)(f), unless it is used for medical or safety reasons.

**Evaluation:**
- `correctness` = **True**. The judge said the answer gives a clear "No" and correctly reflects the prohibition and the medical/safety exception.
- `cites_correct_article` = **True** (Article 5 is cited).

## 3. Evidence
- **Trace of this run:** `outputs/screenshot_trace.png`
- **Experiment table:** `outputs/screenshot_experiment.png`. Live link: https://eu.smith.langchain.com/o/6a443e3e-a646-46d2-8426-409f0215ab77/datasets/516fe224-9104-44fa-99fd-fd6dfd3bf85a/compare?selectedSessions=eefea85a-9afb-4420-b164-c0021d1d4f89
- **Dataset in LangSmith:** `outputs/screenshot_dataset.png`
- **Results:** `outputs/results_main.csv`, `outputs/results_analysed.csv`, `outputs/pass_rate_by_category.png`

## 4. Final output
| Metric | Final run | Range over 3 runs |
|---|---|---|
| Correctness (LLM judge) | 100% (19/19) | 95–100% |
| Cites correct article (rule-based) | 100% (19/19) | 100% |

Summary: [`evaluation_summary.md`](evaluation_summary.md)

## 5. Failures and limitations I hit
- **Bug in my own evaluator.** I tested the rule-based check on a deliberately wrong answer ("…under Article 50"), and it still passed: the text "article 5" is contained in "article 50". I fixed it with a word-boundary match (`\b`), and after the fix the wrong answer correctly fails. Without testing the evaluator first, I would have trusted a check that passes wrong answers.
- **Results change between runs, even at temperature 0.** Correctness was 100% → 95% → 100% over three runs. In the 95% run one hard example failed: for an HR tool that only checks forms for missing fields, the model correctly said it is not automatically high-risk (Article 6(3)) but left out the Article 6(4) duty to document the assessment. In that run the two evaluators disagreed: the article check passed, the judge failed it. The same question passed in the other runs.
- **The dataset is too easy.** Each context already states the rule and its exception, so the task is close to reading comprehension. 100% does not prove the assistant is ready for client use. A `-v2` should add multi-part and borderline questions where the context is close but not sufficient.
- **Setup issue:** my first LangSmith key gave 401/403 errors until I used a key created on the EU site together with the EU endpoint (`https://eu.api.smith.langchain.com`).
