# W7D5_LAB_Micromanage_your_agents
- Week 7 / Day 5
- Student: Andreas Papachristophorou
- Course: AI Consulting & Integration 2026-07
- Date: 2026-08-23
---

# Step 1: Choose Your Domain and Documents

## Chosen domain
This project evaluates an LLM’s ability to answer factual, source-grounded questions about EU ETS for maritime transport and FuelEU Maritime. The aim is to test whether the model can give clear, concise compliance information based only on the official text supplied with each question, rather than relying on unsupported general knowledge. The dataset will contain 12 examples: six on EU ETS and six on FuelEU Maritime.

## Document sources
- European Commission — EU ETS maritime transport FAQ and shipping decarbonisation guidance.
- European Commission — FuelEU Maritime overview and implementation guidance.
- European Maritime Safety Agency (EMSA) — FuelEU Maritime FAQs and implementation materials.
- EUR-Lex — official EU regulations and legal texts.

All material will be taken from publicly available official EU sources, with each source URL and access date recorded. This project provides compliance-information support for learning and evaluation purposes only; it is not legal advice.

## What makes a good example?
A good example contains one clear factual compliance question that can be answered from a short accompanying official source excerpt. The input will include a short source excerpt, a question, and optional metadata such as regulation (EU ETS or FuelEU Maritime) and topic; the expected output will be a concise reference answer supported entirely by that excerpt.

## Dataset Schema
```
{
    "inputs": {
        "context": "Short official source excerpt goes here.",
        "question": "One clear factual compliance question goes here."
    },
    "outputs": {
        "answer": "Short reference answer supported by the context."
    },
    "metadata": {
        "regulation": "EU ETS" or "FuelEU Maritime",
        "topic": "scope, timeline, reporting, etc.",
        "source_url": "Official source URL",
        "accessed_date": "2026-08-23"
    }
}
```

