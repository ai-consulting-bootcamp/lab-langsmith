
Deterministic evaluator:
{'key': 'label_accuracy', 'score': 0.0, 'comment': '0/1 criterion labels correct. criterion 42: expected NOT APPLICABLE, got NOT MET'}

LLM-as-judge evaluator:
{'key': 'correctness', 'score': True, 'comment': 'The patient is an 8-year-old male presenting with fever, dyspnea, and cough. The trial exclusion criterion is pregnancy, which is not applicable to this patient. The output correctly identifies that the exclusion criterion regarding pregnant women does not apply here. The label "NOT MET" indicates the exclusion criterion is not met, meaning the patient is not excluded for this reason, which is logically consistent with the patient data. Although the terminology could arguably be "NOT APPLICABLE" or "NOT MET" depending on conventions, the response uses "NOT MET" appropriately to indicate the exclusion criterion does not exclude the patient. There are no factual errors, all parts of the question are addressed, and the explanation is clear and accurate. Thus, the score should be: true.', 'metadata': None}






Changed prompt into very deterministic one:


Deterministic evaluator:
{'key': 'label_accuracy', 'score': 0.0, 'comment': '0/1 criterion labels correct. criterion 42: expected NOT APPLICABLE, got NOT MET'}

LLM-as-judge evaluator:
{'key': 'correctness', 'score': False, 'comment': "The recommended label for the criterion 'Pregnant women' is 'NOT APPLICABLE' since the patient is an 8-year-old male, making this exclusion criterion irrelevant. The output assigned the label 'NOT MET', which is incorrect because this label implies the exclusion criterion applies and is present, orthe inclusion criterion is unmet. The reasoning correctly states that the criterion does not apply to the patient, but the chosen label contradicts this reasoning. There is no evidence provided, which is consistent with the referenceoutput due to the criterion's inapplicability. The screening summary states that at least one trial criterion is notmet and that human review is required, which is inconsistent with the criterion being not applicable. Thus, the output is not fully correct. Hence, the score should be: false.", 'metadata': None}


## so
Generic task
→ generic CORRECTNESS_PROMPT may be enough

Domain-specific terminology / strict labels / business rules
→ custom rubric + stronger judge if needed

Exact ground truth available
→ deterministic evaluator should remain the primary metric

---

after running run_evaluation baseline, quite a lot of missinterpretations

Why did the model disagree with the expert reference?

Typical patterns we should look for are:

wrong interpretation of inclusion vs exclusion
treating missing information as absence
confusing NOT MET with NOT APPLICABLE
over-inference from medical context
partial failure in multi-criterion cases
reasoning that contradicts the chosen label

---

