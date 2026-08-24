# LangSmith Setup

This lab uses the LangSmith **EU** endpoint.

Configuration:
- Project: `lab-langsmith-parisa-dehghani`
- Endpoint: `https://eu.api.smith.langchain.com`
- Tracing: `true`
- Dataset: `openevals-repo-qa-v2`

Required local environment variables:
- `LANGSMITH_API_KEY`
- `OPENAI_API_KEY`
- `LANGSMITH_TRACING=true`
- `LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com`
- `LANGSMITH_PROJECT=lab-langsmith-parisa-dehghani`

`run_lab.py` performs a real LangSmith API connection check before evaluation. It prints the active project, endpoint, and tracing setting. If authentication or connectivity fails, the script raises the real error instead of silently falling back to a local-only result.

The OpenAI client is wrapped with `wrap_openai`, and the target function also uses `@traceable`, so the model call and target function are visible in LangSmith tracing.
