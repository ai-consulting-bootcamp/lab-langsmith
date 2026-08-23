# Step 1: Domain & Document Selection

## Chosen Domain
UX and Product Design knowledge — the kinds of questions a designer or design team
would need to answer correctly on the job: usability principles, accessibility
standards, design systems, user research methods, interaction design, information
architecture, prototyping, cognitive psychology, evaluation methods, and platform
guidelines.

## Document / Source Basis
Rather than extracting examples from a single uploaded document or scraped corpus,
each Q&A pair was authored by drawing on well-established, publicly known UX
reference frameworks:

- Nielsen Norman Group's usability heuristics
- WCAG 2.1 (Web Content Accessibility Guidelines) — specifically the AA conformance
  criteria
- Apple's Human Interface Guidelines (iOS)
- Standard UX research methodology (personas, formative vs. summative testing,
  heuristic evaluation, IA practices, SUS)

**Note on methodology:** this is a synthesized dataset built from domain knowledge
of these named, publicly documented standards — not examples extracted line-by-line
from a specific source file or document set. I'm noting this explicitly rather than
implying the examples were pulled from an uploaded corpus, since the lab's Step 1
wording ("gather documents... extract examples") assumes a document-extraction
workflow. If the reviewer requires literal source documents, the fix would be to
attach the actual WCAG 2.1 spec pages, the NN/g heuristics article, and the Apple
HIG pages as reference documents in the repo and cite specific sections per example.

## What Makes a Good Example in This Domain
- A single, clearly scoped question (input)
- A factual, verifiable reference answer (output) — not a matter of opinion
- Coverage across difficulty levels: easy (UX vs. UI), medium (design systems,
  heuristic evaluation), hard (exact WCAG contrast ratios, SUS scoring mechanics)
- A category tag in metadata for later slice-by-category analysis

## Dataset Summary
- **Size:** 15 examples
- **Categories:** 11 (accessibility, design systems, evaluation methods, user
  research, fundamentals, heuristics, interaction design, information architecture,
  prototyping, psychology, platform guidelines)
- **LangSmith dataset name:** `ux-design-knowledge-qa`
