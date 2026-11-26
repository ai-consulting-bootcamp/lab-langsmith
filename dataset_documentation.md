# Dataset documentation (Steps 1, 3 and 4)

## Domain and documents
**Domain:** questions a small EU business might ask about the **EU AI Act** and the **GDPR**.
**Source documents:** the Week 7 course materials (slides and revision notes on the AI Act, the Digital Omnibus changes and the GDPR). Every reference answer was written from those materials, not copied from the web, so the model cannot have memorised them.
**Why this domain:** it continues the scenario of the Week 7 Day 4 LLM-judges lab (an assistant for SMEs) and has clear right and wrong answers, which suits a correctness evaluator.

## LangSmith dataset
- **Name:** `ai-act-gdpr-sme-qa-v1`
- **Description:** "12 questions a small EU business might ask about the AI Act and GDPR, with reference answers written from Ironhack Week 7 materials. Metadata: topic (ai_act/gdpr) and difficulty."
- **Created by:** `create_dataset_if_missing()` in `langsmith_evaluation.py` (skipped if the dataset already exists).

## Data structure
Each example has:

| Field | Type | Example |
|---|---|---|
| `inputs.question` | string | "Within how many hours must a company notify a personal data breach to the data protection authority?" |
| `outputs.answer` | string (reference answer) | "Within 72 hours of becoming aware of it, unless the breach is unlikely to result in a risk to people." |
| `metadata.topic` | `ai_act` or `gdpr` | `gdpr` |
| `metadata.difficulty` | `easy`, `medium` or `hard` | `easy` |

## The 12 examples

| # | Topic | Difficulty | Question (shortened) |
|---|---|---|---|
| 1 | ai_act | easy | Key test that makes software an "AI system" |
| 2 | ai_act | easy | AI cameras detecting employees' stress |
| 3 | ai_act | medium | Is CV ranking high-risk? |
| 4 | ai_act | hard | Annex III dates after the Digital Omnibus |
| 5 | ai_act | medium | What a chatbot must tell users (Article 50) |
| 6 | ai_act | medium | Who is the provider of an app built on OpenAI's model |
| 7 | gdpr | easy | The six lawful bases (Article 6) |
| 8 | gdpr | medium | Is pseudonymised data personal data? |
| 9 | gdpr | easy | Breach notification deadline |
| 10 | gdpr | hard | Legitimate interest for health data |
| 11 | gdpr | hard | The three cases where a DPIA is always required |
| 12 | gdpr | medium | Sending personal data to a US AI provider |

Balance: 6 AI Act / 6 GDPR; 4 easy, 5 medium, 3 hard. Full text of questions and answers: `EXAMPLES` in `langsmith_evaluation.py`.
