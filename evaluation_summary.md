# Evaluation Summary

Evaluated gpt-4o-mini (temperature 0) on a 15-example structured
field-extraction task built from real USAspending.gov defense-vehicle
contract awards (NAICS 336350/336330/336310/336399), extracting vendor
name, award amount, and award ID from natural-language contract notices
using a rule-based correctness evaluator with 0.01 floating-point tolerance
on dollar amounts; the model scored a perfect 1.0 average across all 15
examples with zero failures on any field. This is a genuine result for this
specific task -- the required fields are stated verbatim in the input text,
so temperature-0 extraction against unambiguous ground truth should score
perfectly if the pipeline works -- but it also means the task, as designed,
is not diagnostic on its own: it demonstrates the model can copy explicit
values, not that it can handle ambiguity or missing data. To address this,
a second 5-example edge-case dataset was hand-built with deliberately harder
conditions (missing data, multi-vendor notices, multiple dollar figures,
abbreviated currency, contract modifications); on this set, average
correctness dropped to 0.87, revealing two real failure modes: the model
silently substituted 0/"" for genuinely missing data rather than returning
null, and it concatenated two vendor names into one string on a multi-vendor
notice rather than disambiguating. A further limitation on the main dataset
is that all 15 examples come from a single awarding agency (Department of
Defense), a side effect of sorting by award amount within a narrow NAICS
filter, so results do not generalize to procurement extraction broadly.
Recommendation: before treating gpt-4o-mini as production-ready for this
extraction task, add explicit prompt instructions for null-handling on
missing fields and vendor disambiguation on multi-party notices, then
re-run against an expanded, harder, multi-agency dataset.

**Key metrics**
| Metric | Main Dataset | Edge-Case Dataset |
|---|---|---|
| Examples evaluated | 15 | 5 |
| Average correctness score | 1.00 | 0.87 |
| Average format-compliance score | -- | 0.96 |
| Model | gpt-4o-mini, temperature 0 | gpt-4o-mini, temperature 0 |
| Dataset diversity | 1 agency (DoD) | Hand-authored, mixed conditions |
