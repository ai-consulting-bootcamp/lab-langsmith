# Part 1: Domain and Documents

**Domain:** repository/documentation Q&A for the OpenEvals project.

The dataset evaluates whether an LLM can answer short factual questions about the official OpenEvals documentation when the relevant documentation context is supplied with each question. This is a practical AI/technology knowledge use case because the same pattern can be used for developer-documentation assistants.

**Source document:**
- Official `langchain-ai/openevals` README: https://github.com/langchain-ai/openevals/blob/main/README.md

A good example has one clear documentation question, a short supporting context passage, and a concise reference answer. The 10 examples were selected from different README topics such as installation, setup, LLM-as-judge, scoring, LangSmith integration, agent evaluation, and other evaluator types. Lab-meta questions were excluded so the dataset stays focused on the real OpenEvals domain.

**Example structure:**
- `inputs.question`: documentation question
- `inputs.context`: supporting documentation information
- `outputs.answer`: expected reference answer
- `metadata.source`: source label
- `metadata.source_url`: source link
- `metadata.source_section`: relevant README section
- `metadata.topic`: analysis category
- `metadata.difficulty`: easy or medium
