# Part 1: Domain and Documents

Domain: repository documentation Q&A for the OpenEvals project.

This dataset uses the repository README, Python package metadata, and the lab brief as source material. The goal is to evaluate whether a model can answer straightforward questions about the project setup, intended use, and required deliverables.

Good examples in this domain are short, unambiguous questions with one clear reference answer, such as package requirements, environment variables, dataset requirements, or file locations. A strong example should be answerable directly from the source text and should not require guessing or outside knowledge.

Source documents:
- `README.md`
- `python/pyproject.toml`
- the lab brief provided for this exercise

Example fields:
- `inputs.question`: the user question or prompt
- `outputs.answer`: the expected answer for exact-match evaluation
- `metadata.source`: which source document the example came from
- `metadata.topic`: the category of the example
