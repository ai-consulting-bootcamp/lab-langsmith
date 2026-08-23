# Evaluation Summary

We evaluated `gpt-4o-mini` on a 16-example AG News content classification benchmark using a deterministic Python exact-match evaluator in LangSmith, achieving an overall accuracy of 87.5% (14/16) with a P50 latency of 0.62s and a total cost of ~$0.00036. The model correctly classified 100% of World, Sports, and Business articles (recall), but only 50% of Sci/Tech articles, with the two Sci/Tech misclassifications also slightly denting Sports' and Business' precision to 80% each — driven by a consistent failure pattern where surface-level keyword density (e.g., "ESPN/Football" in a video game software release, or "Sell/Market" in PC retail news) caused the LLM to pull Sci/Tech articles into whichever adjacent category's vocabulary dominated the text. While this evaluation is limited by a modest dataset size (16 examples) and historical taxonomy drift in the 2004 AG News benchmark, we recommend updating the system prompt in `target_functions.py` with explicit disambiguation rules and 2–3 few-shot examples specifying that video game software and consumer tech sales strictly belong under `Sci/Tech`.

**Key Performance Metrics**
- **Model & Setup:** `gpt-4o-mini` | `temperature=0.0` | `max_tokens=10`
- **Accuracy (Exact Match):** 87.5% overall
- **Per-category recall:** World 100%, Sports 100%, Business 100%, Sci/Tech 50%
- **Per-category precision:** World 100%, Sports 80%, Business 80%, Sci/Tech 100%
- **Difficulty Breakdown:** Medium 100% (7/7) | Easy 80% (4/5) | Hard 75% (3/4)
- **Performance:** P50 Latency 0.62s | Mean Tokens 145/run | Total Cost ~$0.00036 USD
- **Primary Failure Mode:** Cross-domain keyword distraction pulling `Sci/Tech` articles into `Sports` (Madden release) and `Business` (AOL PC sales)