# Step 1 Deliverable: Domain & Document Selection
## 1. Domain Choice
For this evaluation benchmark, I selected the Content Creation domain, specifically focusing on News Content Classification. Rather than using subjective tasks like article rewriting or creative content generation, this domain evaluates an LLM's ability to analyze raw text and categorize it into a predefined taxonomy. This objective approach ensures verifiable, deterministic evaluation results without relying on opinionated scoring.

## 2. Document Source(s)
* Dataset: AG News Dataset (fancyzhx/ag_news), hosted on Hugging Face Datasets.
* Storage Location: Curated locally at [content_creation_dataset.json](data/content_creation_dataset.json) (16 total examples).
* Categories Covered: World, Sports, Business, and Sci/Tech.

## 3. What Makes a Good Example in This Domain
Input: A prompt containing raw news article text along with a explicit categorization instruction (e.g., "Classify the following article text into one of these categories: World, Sports, Business, Sci/Tech.").

Expected Output: A single, deterministic category string matching the ground-truth publisher label (World, Sports, Business, or Sci/Tech).

Dataset Quality & Diversity: A strong dataset includes unambiguous category anchors (e.g., Olympic game results for Sports, international treaties for World) alongside boundary/edge cases (e.g., technology IPOs sitting between Business and Sci/Tech) to test model precision and evaluator robustness.

### Step 2 Deliverable: LangSmith Environment & Client Setup

1. **Environment & Tracing Configuration:**
   - Configured `.env` with `LANGSMITH_TRACING=true` and authenticating `LANGSMITH_API_KEY`.
   - Loaded environment settings into python environment using `python-dotenv`.

2. **Project Naming:**
   - **Project Name:** `content-creation-eval`
   - **Domain Context:** Dedicated project space for tracing and evaluating news content classification models against defined taxonomies.

3. **Client Connection & Verification:**
   - Initialized `langsmith.Client()` alongside `langsmith.wrappers.wrap_openai(OpenAI())`.
   - Verified connection by executing `@traceable(name="verify_langsmith_connection")` in `src/setup_env.py`.
   - Confirmed trace delivery directly in the LangSmith Web UI under the `content-creation-eval` project space.

### Step 3 Deliverable: Example Extraction & Structuring

**1. Data Structure Overview:**
The dataset consists of 16 examples extracted from the AG News benchmark, serialized in JSON format. Each record is isolated and can be evaluated independently.

**2. Field Documentation:**
*   **`inputs`**: What is fed into the LLM target function.
    *   `question` (string): The explicit prompt given to the LLM, containing both the instruction and the raw article text to be classified.
*   **`outputs`**: The ground truth used by evaluators.
    *   `expected_output` (string): The exact category string (`World`, `Sports`, `Business`, or `Sci/Tech`) the model is supposed to predict.
*   **`metadata`**: Additional context used for filtering or post-evaluation analysis in LangSmith.
    *   `source_index` (integer): The original index of the article in the huggingface dataset.
    *   `dataset` (string): Identifies the origin source (`ag_news`).
    *   `category` (string): Redundant category tag to easily filter subsets in the LangSmith UI.
    *   `difficulty` (string): One of `easy`, `medium`, or `hard`, hand-assigned based on how much category-boundary ambiguity the article contains (e.g., a tech-company retail story that could plausibly read as Business or Sci/Tech is tagged `hard`). Used in Step 9's categorical analysis to check whether errors correlate with anticipated difficulty.

**3. Quality Checks:**
- Total examples: 16 (meets the 10-20 requirement).
- Output categories strictly conform to the expected 4-class taxonomy.
- Inputs are formatted uniformly with clear separation between instructions and data.

### Step 4 Deliverable: LangSmith Dataset Creation
1. **Dataset Details**
* **Dataset Name:** `ag-news-content-classification`
* **Description:** "AG News 4-category classification benchmark with difficulty metadata."
* **Domain Context:** The naming convention clearly indicates the dataset's origin (AG News) and its specific evaluation purpose (content classification), ensuring it remains distinct from future generative or summarization datasets.

2. **Example Structure & Upload**
* **Format:** Uploaded as a standard Key-Value dictionary matching LangSmith's requirements.
* **Inputs:** `{"question": "Classify the following article text..."}`
* **Outputs:** `{"expected_output": "<Category Name>"}`
* **Metadata:** Included `dataset`, `category`, `source_index`, and `difficulty` to enable granular performance filtering later.
* **Total Count:** 16 independent examples successfully ingested.

3. **Verification Confirmation**
* **Status:** Verified directly in the LangSmith Web UI. Screenshot attached in `screenshots/` 
* **Confirmation:** The examples appear under the Datasets & Experiments tab. All fields are correctly associated, and opening an individual example (e.g., Example #0244) confirms that the updated difficulty metadata key is now successfully attached and visible.

### Step 5 Deliverable: Target Function Implementation

**1. Target Function Design & Documentation:**
*   **Function Name:** `target_classifier(inputs: dict) -> dict`
*   **Model Selected:** `gpt-4o-mini` (Fast and highly capable for classification).
*   **Parameters:** `temperature=0.0` (to force deterministic and repeatable outputs for evaluation), `max_tokens=10` (to limit output to the category string only).
*   **System Prompt:** Strict constraints applied: *"You are an expert news classifier. Classify the user's text into exactly one of these categories: World, Sports, Business, Sci/Tech. Reply ONLY with the exact category name."*
*   **Error Handling:** Implemented a `try/except` block that safely catches API exceptions and returns `{"actual_output": "Error", "error_details": str(e)}` to prevent evaluation pipeline crashes.
*   **Tracing:** Function is wrapped with the `@traceable(name="news-classifier-target")` decorator.

**2. Test Execution Results:**
The function was successfully tested on 3 distinct dataset examples:
*   **Test 1 (Swimming article):** Correctly output `{'actual_output': 'Sports'}`
*   **Test 2 (Stocks/Economy article):** Correctly output `{'actual_output': 'Business'}`
*   **Test 3 (International politics article):** Correctly output `{'actual_output': 'World'}`

### Step 6 Deliverable: Evaluator Implementation

**1. Evaluator Design:**
*   **Evaluator Type:** Exact Match (Custom Python Function).
*   **Rationale:** Since the news classification domain forces strict adherence to a 4-category taxonomy, a deterministic string-comparison evaluator is more accurate, faster, and cheaper than using an LLM-as-a-judge.

**2. Data Mapping Strategy:**
*   Compares outputs["expected_output"] (from the target model) against reference_outputs["expected_output"] (from the dataset).
*   Added normalization (`.strip().lower()`) to prevent false negatives caused by trailing spaces or minor casing issues.

**3. Output Format:**
*   Returns a dictionary with `key`, `score` (1 or 0), and a `comment` to log the result directly in the LangSmith UI.

### Step 7 Deliverable: Final Evaluation Run & Analysis

**1. Experiment Execution:**
*   **Experiment Prefix:** `gpt-4o-mini-20260823-141007`
*   **Dataset Scored:** `ag-news-content-classification`
*   **Pipeline:** Successfully routed 16 inputs through the `@traceable` target classifier and graded outputs using the custom `exact_match_evaluator`. Max concurrency was set to 3 to safely respect rate limits.

**2. Final Metrics & Insights:**
*   **Accuracy:** 87.50% (14/16 exact matches).
*   **Cost:** $0.00036 total (~$0.00002/example) — essentially free
*   **Tokens:** 2,321 total
*   **Failure Analysis:** The model struggled exclusively with cross-domain edge cases. It misclassified two `Sci/Tech` articles as `Sports` (video game context) and `Business` (corporate tech context). 
*   **Next Steps for Optimization:** To hit 100% accuracy, the system prompt in `target_functions.py` needs to be updated with few-shot examples clarifying that video game releases and tech-corporate initiatives should strictly default to `Sci/Tech`.

### Step 8 Deliverable: LangSmith UI Results Review
1. **Experiment Summary & Aggregate Metrics**
* **Total Examples Processed:** 16
* **Overall Pass Rate (Accuracy):** 87.5% (14 out of 16 correct)
* **Latency:** Individual classification calls ranged roughly 0.5–1.2s each (P50 latency: 0.62s). The full 16-example run completed in ~4 seconds total, not because each call was that fast individually, but because `max_concurrency=3` ran three examples in flight at once.
* **Cost:** Negligible — under $0.0001 per example, ~$0.00036 total for the full run, due to `gpt-4o-mini` and a `max_tokens=10` cap.
* **UI Navigation Notes:** In the LangSmith Datasets & Experiments tab, sorting/filtering the `exact_match` column to isolate `0.00` scores made it fast to jump straight to the two failing examples rather than scanning all 16 rows manually.
2. **Initial Observations on Performance**
* The target classifier scored **100% on World, Sports, and Business** — every example in these three categories was classified correctly, showing the prompt is generally robust across most of the taxonomy.
* **Sci/Tech was the only category with any failures**, and even there, most Sci/Tech articles (rows 4 and 6) were still classified correctly — it was specifically 2 borderline Sci/Tech articles that failed, not the category as a whole.
* **Error pattern:** Both failures were true Sci/Tech articles that the model misclassified into an adjacent category based on surface-level keyword overlap, rather than the underlying technical subject matter.

3. **Interesting Examples & Failure Modes (To Investigate Further)**
Upon clicking through the failed examples in the UI, two distinct edge cases stand out:

**Example A (The Semantic Trap)**

* Input Text: *"'Madden,' 'ESPN' Football Score in Different Ways... EA Sports would like to think it was because 'Madden NFL 2005' came out that day..."*
* Expected: `Sci/Tech` | Got: `Sports`
* Analysis: The overwhelming presence of words like "Football," "ESPN," and "Sports" triggered a `Sports` classification, missing that this is a software/gaming industry release article rather than a sports story.

**Example B (The Corporate Tech Overlap)**

* Input Text: *"AOL to Sell Cheap PCs to Minorities and Seniors... America Online on Thursday said it plans to sell a low-priced PC..."*
* Expected: `Sci/Tech` | Got: `Business`
* Analysis: Because the article discusses corporate strategy, target demographics, and sales language ("sell," "households," "market"), the model favored `Business`. AG News classifies PC hardware/ISP news as `Sci/Tech`, revealing a taxonomy mismatch between the dataset's labeling convention and the model's default reasoning.

4. **Proposed Next Steps (Iterative Improvement)**

To address these failures in a future iteration, the system prompt in `target_functions.py` could be updated with explicit negative constraints or few-shot examples, such as:

> "Note: Articles about video game releases belong to Sci/Tech, not Sports. Articles about technology companies selling hardware belong to Sci/Tech, not Business."

This would directly counter the surface-keyword bias observed in both failure cases.

### Step 9 Deliverable: Detailed Evaluation Analysis

### 1. Aggregate Quantitative Metrics

| Metric | Value |
|---|---|
| Total Evaluation Runs | 16 examples |
| Mean Score (Accuracy) | 87.50% |
| Median Score | 100.00% |
| Standard Deviation | 0.3416 |
| Pass Rate (Score = 1.0) | 87.50% (14 / 16) |
| Fail Rate (Score = 0.0) | 12.50% (2 / 16) |
| Latency (Mean / P50 / P90) | 0.73s / 0.62s / 1.08s |
| Tokens per Run (Mean / Total) | 145.06 tokens / 2,321 tokens |
| Total Cost | ~$0.00036 USD |

**Best-performing examples:** the 14 correct classifications spanned all four categories and both easy and medium difficulty tiers, with no formatting errors or malformed outputs anywhere in the run — the model never hallucinated a category outside the given four options.

**Worst-performing examples:** both failures were Sci/Tech articles (detailed in Section 3) — no other category produced a single error.

### 2. Categorical & Metadata Analysis

### Category Breakdown

| Category | Total Examples | Correct | Accuracy | Primary Failure Mode |
|---|---|---|---|---|
| World | 4 | 4 | 100.0% | None (100% precision) |
| Sports | 4 | 4 | 100.0% | None (100% precision) |
| Business | 4 | 4 | 100.0% | None (100% precision) |
| Sci/Tech | 4 | 2 | 50.0% | Cross-domain keyword distraction |

### Difficulty Breakdown

| Difficulty Level | Total Examples | Passed | Failed | Accuracy |
|---|---|---|---|---|
| Easy | 5 | 4 | 1 | 80.0% |
| Medium | 7 | 7 | 0 | 100.0% |
| Hard | 4 | 3 | 1 | 75.0% |

**Note:** one failure occurred on an example tagged `Easy` — a mild surprise, since the difficulty label predicted this would be a straightforward classification. This suggests the difficulty tags (assigned based on general topic ambiguity) don't fully anticipate keyword-driven failure modes; a "Madden NFL" article reads as easy in isolation but happens to sit exactly on the Sports/Sci-Tech boundary that trips the model up.

### 3. Qualitative Error Analysis & Taxonomy

### Error Category 1: Semantic & Entity Bias (False Positive — Sports)
- **Failed Example:** *"'Madden,' 'ESPN' Football Score in Different Ways..."* (Difficulty: Easy)
- **Expected:** Sci/Tech | **Model Output:** Sports
- **Root Cause:** High-density domain tokens ("Football," "ESPN," "Madden NFL") led the model to classify based on surface vocabulary rather than the underlying context — a video game software release, not a sports event.

### Error Category 2: Commercial Overlap (False Positive — Business)
- **Failed Example:** *"AOL to Sell Cheap PCs to Minorities and Seniors..."* (Difficulty: Hard)
- **Expected:** Sci/Tech | **Model Output:** Business
- **Root Cause:** Strong commercial/corporate vocabulary ("sell," "low-priced," "market," "households") led the model to favor Business over the underlying PC hardware/ISP topic.

Both errors share a common mechanism: the model appears to weight **surface keyword density** over **subject-matter category**, consistently in the direction of pulling Sci/Tech articles toward whichever adjacent category's vocabulary is more prominent in the text.

### 4. Key Performance Insights & Actionable Recommendations

- **Core Strength:** `gpt-4o-mini` achieved 100% accuracy on World, Sports, and Business — pure-domain news — with zero formatting errors or out-of-taxonomy labels across all 16 runs.
- **Core Weakness:** Sci/Tech articles containing strong auxiliary tokens (gaming/sports terminology or commercial retail language) trigger false-positive classification into the adjacent category whose vocabulary dominates the text.
- **Prompt Engineering Remedy:** Add disambiguation rules to the system prompt in `target_functions.py`:
  > "Software and video game releases, consumer hardware, and ISP services must always be classified as Sci/Tech, even if they mention sports titles or use commercial sales language."
- **Dataset Taxonomy Note:** The Business/Sci-Tech boundary in AG News reflects 2004-era editorial labeling conventions that don't always match a modern LLM's default category intuitions. Adding 2–3 few-shot edge-case examples to the prompt would help bridge this gap in a future iteration, rather than relying on the base prompt alone.

# Custom Evaluator Deliverable: Plausibility LLM Judge

## 1. Evaluator Design & Specification

- **Metric Measured:** Category Plausibility & Defensibility.
- **Core Rationale:** Deterministic exact-match evaluators penalize label mismatches binarily (`0` or `1`) against historical reference outputs. The `plausibility_evaluator` measures whether a predicted label is a defensible interpretation of the article content—separating acceptable taxonomy boundary calls from genuine model hallucinations.
- **Scoring Taxonomy (1–5 Scale):**
  - **5:** Clearly correct and unambiguous fit.
  - **4:** Solid, well-supported fit.
  - **3:** Defensible, but not the single best fit.
  - **2:** Weak or strained connection.
  - **1:** Complete category irrelevance.
  - **0:** Out-of-taxonomy label (short-circuited without an API call).

## 2. Local Unit Test Verification

Executing `python src/custom_evaluator.py` validated the LLM judge's standalone reasoning logic:

- **Test 1 (Clear Sports text → Predicted `Sports`):** Score **5/5**. *Reasoning:* Discusses Olympic swimming competition.
- **Test 2 (Madden NFL release → Predicted `Sports`, Reference `Sci/Tech`):** Score **5/5**. *Reasoning:* Discusses a football video game and fan impact, which strongly aligns with Sports.
- **Test 3 (Out-of-taxonomy `Politics`):** Score **0/5**. *Reasoning:* Invalid category short-circuit.

## 3. Full-Run LangSmith Analysis (`gpt-4o-mini-20260823-180009`)

Executing `run_evaluation.py` tracked both metrics side-by-side across all 16 dataset examples:

- **Aggregate Results:** `exact_match` AVG = **0.88** (87.5%), `plausibility` AVG = **4.75 / 5.0**.
- **Divergence on Hard Edge Cases:**
  - **Row 8 (Madden NFL 2005 Article):** `exact_match` = `0.00` vs. `plausibility` = `5.00`. The reference label is `Sci/Tech`, but the judge confirmed `Sports` is a 5/5 plausible read.
  - **Row 13 (AOL PC Sales Article):** `exact_match` = `0.00` vs. `plausibility` = `4.00`. The reference label is `Sci/Tech`, but the judge recognized that corporate discount pricing is a 4/5 solid fit for `Business`.

## 4. Strategic Insight

Pairing `exact_match` with `plausibility` reveals that `gpt-4o-mini` suffered zero severe hallucinations or format breakages across the entire run. The 12.5% error rate flagged by exact-match scoring consists entirely of highly defensible boundary interpretations (average plausibility of 4.5/5 on failed rows).

### Step 14 Results: A/B Comparison Complete

| Metric | `gpt-4o-mini` | `gpt-4o` |
| --- | ---: | ---: |
| `exact_match` (accuracy) | **87.5% (14/16)** | **81.25% (13/16)** |
| `plausibility` (average) | 4.625 / 5 | 4.6875 / 5 |
| Mean latency | 0.75s | 0.59s |
| P50 latency | 0.67s | 0.58s |
| Total cost (16 examples) | $0.000357 | $0.005952 |
| Cost per example | $0.0000223 | $0.0003720 |
| **Cost ratio** | 1x | **16.7x more expensive** |

**The genuinely interesting finding: `gpt-4o` performed *worse* on accuracy, not better.**

- Both models failed the same two Sci/Tech boundary cases (`Madden → Sports` and `AOL → Business`). Consistent with the earlier analysis, this confusion does not appear to be model-specific.
- However, `gpt-4o` made a **third, new error that `gpt-4o-mini` did not**: it misclassified a **Business** article as **World**. This is a different type of mistake from the Sci/Tech boundary confusion—not an ambiguous taxonomy call, but a clear misclassification.
- `gpt-4o` was also faster in this run (0.59s vs. 0.75s mean latency). This is likely due to infrastructure or endpoint variability rather than an inherent advantage related to model size.

### Step 15 Deliverable: Cost-Performance Trade-off Analysis

#### 1. Metrics per Configuration

| Metric | `gpt-4o-mini` | `gpt-4o` |
| --- | ---: | ---: |
| Accuracy (`exact_match`) | 87.5% (14/16) | 81.25% (13/16) |
| Plausibility (average) | 4.625 / 5 | 4.6875 / 5 |
| Mean latency | 0.75s | 0.59s |
| Total cost (16 examples) | $0.000357 | $0.005953 |
| Cost per example | $0.0000223 | $0.0003720 |
| **Cost per correct answer** | **$0.0000255** | **$0.0004579** |

#### 2. Cost-Performance Frontier

`gpt-4o-mini` sits strictly on the frontier—no configuration tested beats it on cost, and none beats it on accuracy either. `gpt-4o` is **dominated**: it costs approximately 17x more per correct answer while scoring 6.25 percentage points *lower* on accuracy. There is no scenario in this comparison where `gpt-4o`'s extra cost buys better performance—it is strictly worse on the primary accuracy metric.

#### 3. Optimization Opportunities

- The cheaper model already provides the *better* performance here, not just "acceptable" performance. This is not a case of trading some accuracy for savings; both metrics favor the cheaper option.
- `gpt-4o` does not justify its cost on this task. Its additional error (`Business → World`) suggests no meaningful reasoning advantage for this simple four-category news classification task, where `gpt-4o-mini` is already well-suited.
- Plausibility is very close between the two models (4.625 vs. 4.6875), a negligible difference that reinforces the conclusion that `gpt-4o`'s additional capability is not being used productively for this task.

#### 4. Recommendation by Scenario

| Priority | Pick | Why |
| --- | --- | --- |
| Cost efficiency | `gpt-4o-mini` | Approximately 18x cheaper per correct answer |
| Maximum performance | `gpt-4o-mini` | Also the more accurate model on this task |
| Best balanced option | `gpt-4o-mini` | Wins on both axes—no trade-off exists here |