# Experiment status

| Item | Status | Evidence |
|---|---|---|
| Custom dataset prepared | Complete | `data/evaluation_examples.json` contains 12 validated examples |
| Target function implemented | Complete | `src/run_evaluation.py` uses `@traceable` and the wrapped OpenAI Responses client |
| Evaluators implemented | Complete | Exact match, format compliance, and OpenEvals correctness judge |
| Credential-free validation | Complete | `data/offline_validation_results.csv` and metrics JSON |
| LangSmith dataset upload | Pending local credentials | Run `python src/create_dataset.py` |
| Live LangSmith experiment | Pending local credentials | Run `python src/run_evaluation.py` |
| LangSmith experiment URL | Pending live run | Automatically saved to `data/langsmith_run_metadata.json` |

No API key, fabricated experiment identifier, or invented LangSmith screenshot is included. The live run requires `LANGSMITH_API_KEY` and `OPENAI_API_KEY` in a local `.env` file that is excluded by `.gitignore`.

