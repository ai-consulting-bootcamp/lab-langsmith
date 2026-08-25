# Step 1: Domain & Document Selection

## Chosen Domain: Content Creation — Blog Title Generation

This dataset evaluates an LLM's ability to generate an engaging, accurate blog title from
the body of an article. It sits within the broader "Content Creation" domain (blog posts,
articles, social media content) called out in the lab instructions, narrowed to a single,
gradeable task so that correctness has a real ground truth to check against.

## Source(s) of Documents

- **Dataset:** [`fabiochiu/medium-articles`](https://huggingface.co/datasets/fabiochiu/medium-articles)
  on Hugging Face (mirrored from the [190k+ Medium Articles](https://www.kaggle.com/datasets/fabiochiusano/medium-articles)
  Kaggle dataset by Fabio Chiusano).
- Contains real, human-published Medium articles scraped from the web, with fields:
  `title`, `text`, `tags`, `url`, `authors`, `timestamp`.
- For this lab, 15–20 articles will be sampled across a diverse set of `tags`
  (e.g. technology, self-improvement, business, health, culture) to avoid the dataset
  skewing toward one topic.

## What Makes a Good Example

- **Input:** The article body (`text`), truncated to a representative excerpt (e.g. first
  ~300–500 words or the first few paragraphs) — this mirrors a realistic prompt: "here is a
  draft article, write a title for it."
- **Expected output:** The article's real, originally published `title` — genuine
  human-authored ground truth rather than a synthetic or hand-written label.
- **Metadata:** `tags`/category, article length, and source `url`, kept alongside each
  example to support categorical analysis later (Step 9) — e.g. checking whether the model
  performs better on technical vs. narrative content.
- **Diversity:** Examples are drawn from different tags and article lengths so the
  evaluation isn't dominated by a single writing style or topic.

## Why This Framing

Using real published titles as ground truth gives the correctness evaluator (Step 6) an
actual target to compare against via LLM-as-judge semantic similarity, rather than an
invented "correct" answer — which is the main weakness of purely synthetic content-creation
datasets (e.g. instruction-style social-media-post datasets) for this kind of evaluation.
