# LangSmith Setup

Project name:
- `lab-langsmith-parisa-dehghani`

Environment variables:
- `LANGSMITH_API_KEY`: your LangSmith key
- `LANGSMITH_TRACING=true`: enables tracing
- `LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com`: EU endpoint for this account
- `LANGSMITH_PROJECT=lab-langsmith-parisa-dehghani`: keeps experiments grouped under a clear project name

How the script uses them:
- `run_lab.py` reads the active LangSmith settings and prints a setup summary before evaluation.
- The LangSmith branch only runs when the API key is present and the endpoint is reachable.

Notes:
- If the endpoint is unreachable from the current machine, the script falls back to the local evaluation path.
- The project name above is the one to use for this lab iteration.
