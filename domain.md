## Domain and Data Sources

The chosen domain is **clinical trial eligibility screening**. The evaluation will test whether an LLM can compare a patient note with clinical trial inclusion and exclusion criteria, classify each eligibility requirement as `MET`, `NOT MET`, `UNKNOWN`, or `NOT APPLICABLE`, identify supporting evidence from the patient record, and preserve the boundary between decision support and final clinical enrollment decisions.

The primary data source will be the public **NCBI TrialGPT Criterion Annotations** dataset. It contains 1,015 patient–criterion pairs with patient notes, clinical trial criteria, criterion types, expert eligibility annotations, and expert evidence-sentence annotations. The patient notes originate from public research cohorts containing synthetic or idealized clinical case descriptions rather than identifiable real patient records.

A good evaluation example consists of a patient note and one or more clinical trial eligibility criteria as input, together with an expert-derived eligibility classification and supporting evidence as the reference output. Approximately 15 examples will be selected to cover clear inclusion and exclusion criteria, missing information, ambiguous evidence, multiple criteria, temporal reasoning, boundary values, medical terminology, contradictory information, and not-applicable cases.



Step 1 decision

Use: TrialGPT Criterion Annotations as our main data source.  
Dataset size for this lab: ~15 carefully selected examples.  
Ground truth: expert eligibility annotations + expert evidence sentences.  
Metadata: category, difficulty, source, criterion type.  
Normalized labels: MET / NOT MET / UNKNOWN / NOT APPLICABLE. 