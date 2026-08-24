# Evaluation Summary

This evaluation tested a 10-example OpenEvals repository/documentation Q&A dataset in LangSmith using a traced, LLM-backed target function with `gpt-4o-mini` at temperature 0 and an OpenEvals `CORRECTNESS_PROMPT` LLM-as-judge evaluator. The completed experiment produced a mean correctness score of 0.90, median of 1.00, and pass rate of 90% (9/10 examples). 1 example(s) failed, concentrated in these topic(s): evaluator. The main limitations are the small manually curated dataset, the use of short supplied context passages, and possible variation in LLM-as-judge scoring. The next recommendation is to keep this as the baseline and add several harder cross-section documentation questions. LangSmith evidence: [dataset](https://eu.smith.langchain.com/o/283e274f-8408-4b7c-a69f-356479c84a57/datasets/bd8fb86b-f3e4-4431-b93c-ad22852c8423) and [experiment](https://eu.smith.langchain.com/o/283e274f-8408-4b7c-a69f-356479c84a57/projects/p/8bb1d7ed-f9ba-49ff-b831-b9db86989d3c).

- Dataset: `openevals-repo-qa-v2`
- Model: `gpt-4o-mini`
- Correctness pass rate: 90%
- Results export: `results.csv`
- Detailed analysis: `analysis.md`
