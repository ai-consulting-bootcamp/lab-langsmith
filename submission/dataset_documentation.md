# Dataset Documentation

## Domain
Structured field extraction from real U.S. federal defense-vehicle
procurement contract descriptions. Given a natural-language contract notice,
the task is to extract vendor name, award amount, and award ID.

## Source
Pulled live from the USAspending.gov public API (no key required), filtered
to NAICS codes 336350, 336330, 336310, and 336399 (motor vehicle
transmission/power train, steering/suspension, gasoline engine parts, and
other motor vehicle parts manufacturing), Department of Defense awards,
2023-2026, sorted by award amount descending. Raw API response saved to
`raw_contract_awards.json`; reshaped into extraction examples via
`structure_dataset.py` -> `dataset_examples.json`.

## LangSmith Datasets
1. **should-cost-contract-extraction** (15 examples) -- real USAspending.gov
   data, reshaped into natural-language contract notices with the dollar
   amount written into the text, paired with ground truth pulled directly
   from the same API fields.
   Dataset ID: `5ccaaafc-e5d3-4f86-8c29-f45dac39d45e`
2. **should-cost-contract-extraction-edge-cases** (5 examples) --
   hand-authored hard cases: missing data, multi-vendor notices, multiple
   dollar figures, abbreviated currency, and contract modifications.
   Dataset ID: `e46144a4-9676-4e00-ab99-e7df765e6d42`

## Data Structure
Each example:
- **input.contract_notice** (string) -- a natural-language procurement
  notice sentence.
- **output.vendor_name** (string or null) -- the awarded company/organization.
- **output.award_amount** (number or null) -- the dollar value of the award.
- **output.award_id** (string or null) -- the contract/award identifier.
- **metadata** -- awarding_agency and start_date (main dataset) or
  edge_case_type (edge-case dataset), used for categorical analysis.

## Note on Dataset Limitation
All 15 examples in the main dataset are Department of Defense awards, a
side effect of the NAICS filter combined with sorting by award amount. This
is documented as a known generalizability limitation in
`evaluation_summary.md`.
