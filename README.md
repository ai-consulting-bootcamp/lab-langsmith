# Minimal LangSmith Lab

Author: Parisa Dehghani

This folder contains the simplest version of the lab required by the provided brief.

What it does:
- builds a 10-example repository-QA dataset from local files
- defines a traceable target function
- evaluates outputs with exact match
- optionally uploads the dataset and experiment to LangSmith when `LANGSMITH_API_KEY` is set
- documents the Part 1 domain and document sources in `part1_domain_writeup.md`
- documents the LangSmith setup in `langsmith_setup.md`

How to run:

```bash
cd /home/parisa/Ironhack-Practice/7th-Week/Day5/lab-langsmith
python run_lab.py --mode local
```

To try the LangSmith upload path, set `LANGSMITH_API_KEY` and run:

```bash
cd /home/parisa/Ironhack-Practice/7th-Week/Day5/lab-langsmith
python run_lab.py --mode both
```

The local run writes the short narrative to `evaluation_summary.md`.  

# For a clean run on this machine, use:
python run_lab.py --mode local. For the full LangSmith attempt, you need a machine that can actually reach the EU endpoint.
