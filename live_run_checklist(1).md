# Live LangSmith run checklist

1. Create a LangSmith account and API key, and make sure the OpenAI API account has available credits.
2. Copy `.env.example` to `.env` and enter both keys locally. Do not paste keys into GitHub or screenshots.
3. For an EU LangSmith workspace, set `LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com`. Otherwise keep the default US endpoint.
4. Install dependencies: `python -m pip install -r requirements.txt`.
5. Run the credential-free checks: `python src/offline_validate.py` and `pytest -q`.
6. Upload the dataset: `python src/create_dataset.py`.
7. Run the traced experiment: `python src/run_evaluation.py`.
8. Open the experiment URL printed in the terminal and saved to `data/langsmith_run_metadata.json`.
9. Review aggregate scores and inspect the failed or disputed examples in the LangSmith UI.
10. Commit the generated raw results CSV and metadata JSON if required for submission; confirm neither file contains secrets.

