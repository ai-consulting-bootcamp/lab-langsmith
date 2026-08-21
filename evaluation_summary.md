# Evaluation Summary

**LAB | Micromanage your agents** — Step 10
**Author:** Nnanyelugo Ahukannah

I built a 22-example LangSmith dataset of grounded question answering over a
three-document consumer-credit compliance corpus (Regulation B adverse-action
duties, FCRA §615 disclosures, and Cardinal Trust Bank's internal notice policy),
where every reference answer cites the corpus clauses it rests on, and evaluated
three configurations against it with five evaluators — openevals' stock
correctness judge, a custom groundedness judge, and three deterministic citation
checks. The result that matters is not which model won but that **correctness was
blind to the biggest failure in the run**: stripping the grounding discipline out
of the system prompt, on the same model, *raised* correctness from 0.818 to 0.909
while collapsing citation validity from 0.909 to 0.318 and groundedness from
0.955 to 0.318 — the answers stayed right and became unciteable, because the model
returned bare clause numbers like `6` where `RB-6`, `FC-6` and `CT-6` all exist.
The biggest failure pattern is therefore prompt-induced and invisible to the
obvious metric; the main limitation is that 22 examples over one authored corpus
cannot separate a 0.818 from a 0.909 with any confidence (the mini-vs-terse
correctness gap is two examples, and is noise), and the corpus is modelled on
public statutory structure rather than reviewed by counsel. **Recommendation:
ship `gpt-4o-mini` with the full grounded prompt and gate on citation validity,
not correctness** — `gpt-4o` buys +0.14 correctness for 16.7× the cost, which is
not worth it, and no model choice repairs a prompt that stops asking for
verifiable citations.

| target | model | prompt | correctness | citation validity | citation wellformed | fabricated-free | groundedness | $/1k queries |
|---|---|---|---|---|---|---|---|---|
| mini | gpt-4o-mini | full | 0.818 | 0.909 | 1.000 | 1.000 | 0.955 | **0.34** |
| gpt4o | gpt-4o | full | **0.955** | **0.955** | 1.000 | 1.000 | 0.955 | 5.61 |
| terse | gpt-4o-mini | terse | 0.909 | **0.318** | **0.364** | 1.000 | **0.318** | 0.32 |

- **Nothing was ever fabricated.** `citation_fabricated_free` is 1.000 in all
  three runs — no configuration invented a clause that does not exist. An earlier
  version of that evaluator conflated "invented" with "badly formatted" and
  reported 77% hallucination on `terse`. That was the evaluator's fault, and
  splitting the two metrics is what corrected it.
- **The custom judge needed auditing more than the models did.** My first
  groundedness prompt contradicted itself on 7.8% of judgements (5 of 64) —
  reasoning ending "Thus, the score should be: true" against a recorded score of
  false — while openevals' stock correctness prompt was self-consistent on all 65.
  Rewriting the prompt in the stock rubric style took it to 0 of 65, and
  `analyze_results.py` re-measures it every run.
- **Failure modes.** `terse`: 15/22 wrong-or-missing clause, 15/22 ungrounded,
  14/22 unverifiable citation. `mini`: 4 incorrect (Q02, Q05, Q06, Q22), 2 wrong
  clause (Q09, Q20). `gpt4o`: 1 incorrect (Q05), 1 wrong clause (Q20). Zero API
  errors across all 66 runs.
- **Hard questions were not the hard part.** Correctness by difficulty was
  easy 0.86 / medium 0.67 / hard 1.00 for `mini` — the edge cases I built to be
  difficult were answered well, and the misses clustered in mid-difficulty
  Regulation B items (category correctness 0.67, the weakest cell in the run).

Full numbers in `lab_langsmith_ugo_ahukannah/analysis_summary.json`; charts in
`lab_langsmith_ugo_ahukannah/figures/`.
